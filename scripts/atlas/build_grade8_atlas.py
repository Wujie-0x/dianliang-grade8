#!/usr/bin/env python3
"""Build 外研版八年级 Word Atlas dataset: index + entries + UK/US audio (no illustrations).

Usage:
  .venv/bin/python scripts/atlas/build_grade8_atlas.py           # full: json + tts
  .venv/bin/python scripts/atlas/build_grade8_atlas.py --json-only
  .venv/bin/python scripts/atlas/build_grade8_atlas.py --tts-only
  .venv/bin/python scripts/atlas/build_grade8_atlas.py --workers 6
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "source"
PUB = ROOT / "public" / "atlas"
DATA = ROOT / "data"
PROGRESS = ROOT / ".local" / "tts-progress.json"

TOPICS = [
    ("education", "教育"), ("work", "职场"), ("technology", "科技"), ("science", "科学"),
    ("environment", "环境"), ("health", "健康"), ("society", "社会"), ("government", "政法"),
    ("economy", "经济"), ("media", "媒体"), ("arts", "艺术"), ("travel", "旅行"),
    ("city", "城市"), ("nature", "自然"), ("daily", "生活"), ("emotion", "情感"),
    ("thinking", "思维"), ("sport", "运动"), ("history", "历史"),
]
TOPIC_INDEX = {k: i for i, (k, _) in enumerate(TOPICS)}
CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"]

UK_VOICE = "en-GB-SoniaNeural"
US_VOICE = "en-US-JennyNeural"

POS_RE = re.compile(
    r"^(n|v|vt|vi|adj|adv|prep|conj|pron|num|art|int|aux|modal|phr|phrase|abbr)\.?\s+",
    re.I,
)


def slugify(word: str) -> str:
    s = word.strip().lower().replace("’", "'").replace("…", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "x"


def load_words(path: Path) -> list[str]:
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def load_translations(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue
            w = row[0].strip()
            tr = (row[1] if len(row) > 1 else "").strip()
            if w and tr and w.casefold() not in out:
                out[w.casefold()] = tr
    return out


def parse_senses(raw: str) -> list[dict]:
    senses = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line:
            continue
        m = POS_RE.match(line)
        if m:
            pos = m.group(1).lower() + "."
            zh = line[m.end() :].strip(" ；;，,")
        else:
            pos = ""
            zh = line
        zh = re.sub(r"\s+", " ", zh).strip()
        if not zh:
            continue
        # keep first clause-ish for brevity
        zh_short = re.split(r"[；;]", zh)[0].strip()
        if len(zh_short) > 40:
            zh_short = zh_short[:38] + "…"
        senses.append({"pos": pos, "zh": zh_short or zh, "en": ""})
        if len(senses) >= 3:
            break
    if not senses:
        senses = [{"pos": "", "zh": "（暂无释义）", "en": ""}]
    return senses


def guess_cefr(word: str) -> str:
    letters = re.sub(r"[^a-zA-Z]", "", word)
    parts = word.split()
    if len(parts) >= 3 or len(letters) >= 12:
        return "B1"
    if len(parts) == 1 and len(letters) <= 4:
        return "A1"
    if len(letters) <= 6 and len(parts) == 1:
        return "A1"
    return "A2"


TOPIC_KEYWORDS = [
    ("education", ["school", "teacher", "student", "class", "homework", "exam", "book", "read", "write", "learn", "study", "lesson", "textbook", "spell"]),
    ("sport", ["sport", "ball", "run", "swim", "team", "game", "match", "football", "basketball", "race", "cheer", "fan", "warm"]),
    ("health", ["health", "ill", "sick", "doctor", "hospital", "medicine", "hurt", "pain", "fever", "matter", "tooth"]),
    ("nature", ["nature", "tree", "river", "mountain", "animal", "bird", "flower", "park", "earth", "plant", "forest", "sea"]),
    ("travel", ["travel", "trip", "train", "bus", "plane", "ticket", "hotel", "visit", "tour", "map"]),
    ("city", ["city", "street", "road", "building", "town", "village", "shop", "market", "bridge"]),
    ("emotion", ["happy", "sad", "angry", "feel", "love", "like", "hope", "fear", "worry", "cheer", "smile"]),
    ("science", ["science", "experiment", "lab", "energy", "electric", "space", "planet", "robot"]),
    ("technology", ["computer", "internet", "phone", "digital", "online", "website", "email"]),
    ("environment", ["environment", "pollution", "recycle", "waste", "protect", "green", "climate"]),
    ("food", []),  # unused key kept out of TOPICS
    ("arts", ["music", "art", "paint", "draw", "song", "dance", "film", "movie", "photo", "camera"]),
    ("history", ["history", "ancient", "king", "museum", "past", "century"]),
    ("work", ["work", "job", "office", "factory", "business"]),
    ("society", ["society", "people", "friend", "family", "community", "help", "share"]),
]


def guess_topic(word: str) -> str:
    wl = word.lower()
    for topic, keys in TOPIC_KEYWORDS:
        if topic not in TOPIC_INDEX:
            continue
        if any(k in wl for k in keys):
            return topic
    # deterministic fallback across daily/education/thinking
    h = int(hashlib.sha1(wl.encode()).hexdigest(), 16)
    pool = ["daily", "education", "society", "thinking", "travel", "nature"]
    return pool[h % len(pool)]


def make_example(word: str, zh_gloss: str) -> dict:
    # Minimal pedagogical example — not publisher content.
    w = word.strip()
    # strip dictionary placeholders for TTS-friendly examples
    display = re.sub(r"\bsb\.\b", "someone", w, flags=re.I)
    display = re.sub(r"\bsth\.\b", "something", display, flags=re.I)
    display = display.replace("…", "…")
    if w.endswith("?") or w.startswith("What's") or w.startswith("What "):
        en = w if w.endswith("?") else w + "?"
        zh = "这句话在课本对话里很常见。"
    elif " " in w or "-" in w:
        en = f"We often say “{display}” in class."
        zh = f"课堂上常说“{zh_gloss[:16]}”。"
    else:
        en = f"I learned the word “{w}” today."
        zh = f"我今天学会了单词“{w}”（{zh_gloss[:12]}）。"
    return {"en": en, "zh": zh}


def tts_text(word: str) -> str:
    t = word.strip()
    t = re.sub(r"\bsb\.\b", "someone", t, flags=re.I)
    t = re.sub(r"\bsth\.\b", "something", t, flags=re.I)
    t = t.replace("…", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t or word


def ipa_for(word: str) -> tuple[str, str]:
    try:
        import eng_to_ipa as ipa
    except ImportError:
        return "", ""
    text = tts_text(word)
    # eng_to_ipa struggles with punctuation / multiword — clean
    clean = re.sub(r"[^a-zA-Z'\s-]", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return "", ""
    try:
        raw = ipa.convert(clean)
    except Exception:
        return "", ""
    if not raw or "*" in raw:
        return "", ""
    form = "/" + raw.replace(" ", " ") + "/"
    return form, form


def build_entries() -> list[dict]:
    up = load_words(SRC / "waiyan-grade8-up.txt")
    down = load_words(SRC / "waiyan-grade8-down.txt")
    tr = {}
    tr.update(load_translations(SRC / "waiyan-grade8-up.csv"))
    tr.update(load_translations(SRC / "waiyan-grade8-down.csv"))

    # union preserving first-seen surface form (上册 first)
    seen: dict[str, str] = {}
    order: list[str] = []
    for w in up + down:
        key = w.casefold()
        if key not in seen:
            seen[key] = w
            order.append(key)

    entries = []
    slug_seen: set[str] = set()
    for key in order:
        w = seen[key]
        senses = parse_senses(tr.get(key, ""))
        uk, us = ipa_for(w)
        cefr = guess_cefr(w)
        topic = guess_topic(w)
        slug = slugify(w)
        if slug in slug_seen:
            slug = f"{slug}-{hashlib.sha1(w.encode()).hexdigest()[:6]}"
        slug_seen.add(slug)
        zh0 = senses[0]["zh"]
        entry = {
            "w": w,
            "uk": uk,
            "us": us,
            "senses": senses,
            "ex": [make_example(w, zh0)],
            "col": [],
            "fam": [],
            "syn": [],
            "ant": [],
            "tip": "",
            "cefr": cefr,
            "topic": topic,
            "note": "",
            "id": slug,
            "m": 0,  # filled after audio
        }
        entries.append(entry)

    entries.sort(key=lambda c: (CEFR.index(c["cefr"]), hashlib.sha1(c["id"].encode()).hexdigest()))
    return entries


def write_atlas(entries: list[dict]) -> dict:
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / "entries").mkdir(parents=True, exist_ok=True)
    (PUB / "audio" / "uk").mkdir(parents=True, exist_ok=True)
    (PUB / "audio" / "us").mkdir(parents=True, exist_ok=True)

    # refresh media flags from disk
    for c in entries:
        m = 0
        if (PUB / "img" / f"{c['id']}.webp").exists():
            m |= 1
        if (PUB / "audio" / "uk" / f"{c['id']}.mp3").exists():
            m |= 2
        if (PUB / "audio" / "us" / f"{c['id']}.mp3").exists():
            m |= 4
        c["m"] = m

    index = []
    for c in entries:
        s0 = c["senses"][0]
        zh = f'{s0["pos"]} {s0["zh"]}'.strip()
        index.append([c["id"], c["w"], zh, c["uk"] or c["us"], CEFR.index(c["cefr"]), TOPIC_INDEX[c["topic"]], c["m"]])

    # wipe old chunks
    for p in (PUB / "entries").glob("*.json"):
        p.unlink()

    for n in range(0, len(entries), 100):
        chunk = entries[n : n + 100]
        (PUB / "entries" / f"{n // 100}.json").write_text(
            json.dumps(chunk, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )

    meta = {
        "id": "waiyan-grade8-atlas",
        "version": 1,
        "name": "点亮八年级 · 外研版",
        "license": "CC BY 4.0",
        "count": len(index),
        "examples": sum(len(c["ex"]) for c in entries),
        "illustrated": sum(1 for c in entries if c["m"] & 1),
        "voiced": sum(1 for c in entries if c["m"] & 2),
        "chunk": 100,
        "topics": TOPICS,
        "cefr": CEFR,
        "fields": ["id", "word", "zh", "ipa", "cefr", "topic", "media"],
        "words": index,
    }
    (PUB / "index.json").write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    DATA.mkdir(exist_ok=True)
    public = [{k: v for k, v in c.items() if k != "m"} for c in entries]
    (DATA / "word-atlas.json").write_text(json.dumps(public, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(DATA / "word-atlas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "word", "ipa_uk", "ipa_us", "cefr", "topic", "meanings_zh", "example1_en", "example1_zh"])
        for c in public:
            ex = c["ex"][0] if c["ex"] else {"en": "", "zh": ""}
            w.writerow([
                c["id"], c["w"], c["uk"], c["us"], c["cefr"], c["topic"],
                " | ".join(f'{s["pos"]} {s["zh"]}'.strip() for s in c["senses"]),
                ex["en"], ex["zh"],
            ])
    return meta


async def synthesize_one(sem, text: str, voice: str, dest: Path, retries: int = 3) -> bool:
    if dest.exists() and dest.stat().st_size > 200:
        return True
    import edge_tts

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".mp3.part")
    for attempt in range(retries):
        async with sem:
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(str(tmp))
                if tmp.exists() and tmp.stat().st_size > 200:
                    tmp.replace(dest)
                    return True
            except Exception as e:
                if attempt == retries - 1:
                    print(f"FAIL {dest.name} ({voice}): {e}", file=sys.stderr)
                else:
                    await asyncio.sleep(1.5 * (attempt + 1))
            finally:
                if tmp.exists():
                    try:
                        tmp.unlink()
                    except OSError:
                        pass
    return False


async def run_tts(entries: list[dict], workers: int) -> dict:
    sem = asyncio.Semaphore(workers)
    tasks = []
    for c in entries:
        text = tts_text(c["w"])
        uk = PUB / "audio" / "uk" / f"{c['id']}.mp3"
        us = PUB / "audio" / "us" / f"{c['id']}.mp3"
        tasks.append(("uk", c["id"], synthesize_one(sem, text, UK_VOICE, uk)))
        tasks.append(("us", c["id"], synthesize_one(sem, text, US_VOICE, us)))

    done = fail = skip = 0
    total = len(tasks)
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)

    async def track(kind, eid, coro):
        nonlocal done, fail, skip
        dest = PUB / "audio" / kind / f"{eid}.mp3"
        if dest.exists() and dest.stat().st_size > 200:
            skip += 1
            return True
        ok = await coro
        if ok:
            done += 1
        else:
            fail += 1
        finished = done + fail + skip
        if finished % 40 == 0 or finished == total:
            PROGRESS.write_text(json.dumps({
                "finished": finished, "total": total, "done": done, "fail": fail, "skip": skip
            }), encoding="utf-8")
            print(f"TTS {finished}/{total} (new={done} skip={skip} fail={fail})", flush=True)
        return ok

    await asyncio.gather(*[track(k, i, c) for k, i, c in tasks])
    return {"done": done, "fail": fail, "skip": skip, "total": total}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--tts-only", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    entries_path = ROOT / ".local" / "grade8-entries.json"
    entries_path.parent.mkdir(parents=True, exist_ok=True)

    if args.tts_only and entries_path.exists():
        entries = json.loads(entries_path.read_text(encoding="utf-8"))
    else:
        entries = build_entries()
        entries_path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
        print(f"Built {len(entries)} entries", flush=True)

    if not args.tts_only:
        meta = write_atlas(entries)
        print(json.dumps({k: meta[k] for k in ("id", "name", "count", "examples", "illustrated", "voiced")}), flush=True)

    if not args.json_only:
        stats = asyncio.run(run_tts(entries, args.workers))
        print("TTS", stats, flush=True)
        meta = write_atlas(entries)  # refresh media flags
        print(json.dumps({k: meta[k] for k in ("count", "illustrated", "voiced")}), flush=True)
        uk = sum(1 for c in entries if (PUB / "audio" / "uk" / f"{c['id']}.mp3").exists())
        us = sum(1 for c in entries if (PUB / "audio" / "us" / f"{c['id']}.mp3").exists())
        print(f"audio coverage uk={uk}/{len(entries)} us={us}/{len(entries)}", flush=True)


if __name__ == "__main__":
    main()
