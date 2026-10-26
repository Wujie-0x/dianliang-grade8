# 点亮八年级 · 外研版

基于开源项目 [Word Atlas / 词光](https://github.com/designfuchen/word-atlas) 的**改编版**：外研版初中英语**八年级上下册**词表（约 597 词），英美发音 + FSRS 间隔复习。本版**暂无插画**。

在线试用：https://wujie-0x.github.io/dianliang-grade8/

> **重要声明**
> - 词表来自 [maimemo-export](https://github.com/busiyiworld/maimemo-export)（墨墨导出，MIT），**非外研社官方数据**，与外研社无关。
> - 改编自 [Word Atlas](https://github.com/designfuchen/word-atlas)（代码 MIT；词库内容 / 插画 / 录音上游为 CC BY 4.0）。
> - 使用本站时请保留对 Word Atlas contributors、本仓库与 maimemo-export 的署名。详见 `LICENSE` 与 `CONTENT_LICENSE.md`。

## 本地预览

```bash
npm install
# 若尚未生成词库/音频：
python3 -m venv .venv && .venv/bin/pip install edge-tts eng-to-ipa
.venv/bin/python scripts/atlas/build_grade8_atlas.py
npm run build
npm run preview               # http://127.0.0.1:5188/
```

## 重新生成词库

```bash
.venv/bin/python scripts/atlas/build_grade8_atlas.py           # JSON + UK/US mp3
.venv/bin/python scripts/atlas/build_grade8_atlas.py --json-only
.venv/bin/python scripts/atlas/build_grade8_atlas.py --tts-only --workers 6
```

源词表在 `data/source/`。产出：`public/atlas/index.json`、`entries/*.json`、`audio/{uk,us}/*.mp3`。

## 发布到 GitHub Pages

```bash
ATLAS_BASE=/dianliang-grade8/ npm run build
# 将 dist/ 部署到 gh-pages 分支
```

## 许可

- **代码**：MIT（见 `LICENSE`，含上游 Word Atlas）
- **词库文本与录音**：按 `CONTENT_LICENSE.md` 的 CC BY 4.0 模式使用，并署名 Word Atlas contributors、本项目与 maimemo-export
- 本版录音由 edge-tts 合成；暂无插画
