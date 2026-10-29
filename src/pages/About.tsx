import { ArrowUpRight, Github, Heart } from "lucide-react";
import { useEffect } from "react";
import { useAtlas } from "../atlas/context";
import { MAIMEMO_URL, REPO_URL, UPSTREAM_URL } from "../config";
import { useLocation } from "../lib/router";

const BASE = import.meta.env.BASE_URL;

/** Deep link for the annual-pass section. Hash routes have no second fragment. */
export const ANNUAL_HREF = "#/about/annual";

function wantsAnnual(hash: string) {
  return hash.includes("/about/annual");
}

export function About() {
  const atlas = useAtlas();
  const loc = useLocation();

  useEffect(() => {
    if (!wantsAnnual(location.hash)) return;
    const el = document.getElementById("annual");
    if (!el) return;
    const t = window.setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
    return () => window.clearTimeout(t);
  }, [loc]);

  return (
    <div className="page about">
      <header className="about-hero">
        <img src={`${BASE}brand/og.webp`} alt="" />
        <div>
          <p className="eyebrow">关于点亮八年级</p>
          <h1 className="display">外研版八年级，一颗颗点亮。</h1>
          <p className="lede">
            把外研版初中英语八年级上下册整理成 {atlas.count.toLocaleString()}{" "}
            个词条，配英美发音和间隔复习。学会一个，就在你的星图上点亮一颗星。本版暂未收录插画。
          </p>
          <p className="lede">它免费、开源、无需注册。代码用 MIT，词库用 CC BY 4.0，谁都可以拿去用。</p>
          <div className="about-actions">
            <a className="btn btn-primary" href={REPO_URL} target="_blank" rel="noreferrer">
              <Github size={18} /> 点亮八年级 GitHub
            </a>
            <a className="btn btn-ghost" href={UPSTREAM_URL} target="_blank" rel="noreferrer">
              基于 Word Atlas 改编 · MIT / CC BY
            </a>
          </div>
        </div>
      </header>

      <div className="about-grid">
        <section className="panel">
          <h3 className="eyebrow">为什么记得住</h3>
          <ul className="feature-list">
            <li>
              <b>听得清。</b>每个词都有英音和美音，可随时跟读。
            </li>
            <li>
              <b>再想起。</b>选义、听音辨词、拼写，从认得走到会写。
            </li>
            <li>
              <b>刚好在快忘时重逢。</b>FSRS 是新版 Anki 用的开源记忆算法，只在你快要遗忘时安排复习。
            </li>
            <li>
              <b>分数诚实。</b>只算第一次作答。答错的词会换个题型再见一面，但不会抬高正确率。
            </li>
            <li>
              <b>进度只属于你。</b>没有账号，没有服务器，数据存在你的浏览器里，随时能导出。
            </li>
          </ul>
        </section>

        <section className="panel">
          <h3 className="eyebrow">快捷键</h3>
          <dl className="keys">
            <div>
              <dt>
                <kbd>⌘</kbd>
                <kbd>K</kbd> 或 <kbd>/</kbd>
              </dt>
              <dd>搜索任何词</dd>
            </div>
            <div>
              <dt>
                <kbd>1</kbd>–<kbd>4</kbd>
              </dt>
              <dd>选择答案</dd>
            </div>
            <div>
              <dt>
                <kbd>Enter</kbd>
              </dt>
              <dd>确认 / 继续</dd>
            </div>
            <div>
              <dt>
                <kbd>←</kbd> <kbd>→</kbd>
              </dt>
              <dd>词卡里切换上一个、下一个</dd>
            </div>
            <div>
              <dt>
                <kbd>Esc</kbd>
              </dt>
              <dd>关闭弹窗</dd>
            </div>
          </dl>
        </section>

        <section className="panel">
          <h3 className="eyebrow">内容从哪里来</h3>
          <p className="muted">
            词表来自开源项目 <a href={MAIMEMO_URL} target="_blank" rel="noreferrer">maimemo-export</a>（墨墨导出，MIT），中文释义参考 ECDICT /
            墨墨翻译 CSV。发音由 edge-tts 合成（英音 Sonia，美音 Jenny）。前端与学习算法改编自开源项目{" "}
            <a href={UPSTREAM_URL} target="_blank" rel="noreferrer">Word Atlas</a>（MIT / 内容 CC BY 4.0）。本站不是外研社官方词表，也不承诺提分。
          </p>
          <p className="muted">当前版本暂无插画；词条会显示字母板占位。欢迎以后补图。</p>
        </section>

        <section className="panel">
          <h3 className="eyebrow">给开发者</h3>
          <p className="muted">
            <code>data/word-atlas.json</code> 和 <code>.csv</code> 是完整词库；<code>public/atlas</code>{" "}
            里是网页用的分块数据和音频。拿去做 Anki 牌组或背词小程序，按许可证署名即可。
          </p>
          <a className="link" href={`${REPO_URL}#readme`} target="_blank" rel="noreferrer">
            阅读本仓库说明 <ArrowUpRight size={14} />
          </a>
        </section>
      </div>

      <section className="panel annual" id="annual" aria-labelledby="annual-title">
        <h2 className="eyebrow" id="annual-title">
          平价年卡
        </h2>
        <p className="annual-story">爸爸给儿子做的平价背词工具。</p>
        <p className="lede">
          现在的全部词表、英美发音和 FSRS 复习永远免费，不用登录也能学完。年卡只是可选的支持，不会打断背词。
        </p>
        <p className="annual-price">
          <b>¥19.9</b>
          <span>/ 年</span>
        </p>
        <div className="annual-plans">
          <article className="annual-plan">
            <h3>免费，一直都在</h3>
            <ul>
              <li>现有全部词表</li>
              <li>英美发音</li>
              <li>FSRS 间隔复习</li>
              <li>无需登录，学习路径没有付费墙</li>
            </ul>
          </article>
          <article className="annual-plan is-paid">
            <h3>年卡 ¥19.9 / 年</h3>
            <ul>
              <li>优先补全词条插画</li>
              <li>加微信一对一答疑（使用问题/背词方法）</li>
            </ul>
          </article>
        </div>
        {/*
          年卡由微信扫码开通，没有账号，也没有支付 SDK。
          收款码是 public/assets/wechat-qr.png（中心为项目头像，昵称已涂白）。
          不要换成假二维码，也不要在页面上写微信号。
        */}
        <div className="annual-cta">
          <img className="annual-qr" src={`${BASE}assets/wechat-qr.png`} alt="微信扫码开通年卡，¥19.9" />
          <div>
            <a className="btn btn-primary" href={ANNUAL_HREF}>
              加微信开通年卡
            </a>
            <p className="muted">微信扫码开通年卡 · ¥19.9</p>
            <p className="muted">扫码即可。不开通也不影响免费背词。</p>
          </div>
        </div>
      </section>

      <p className="colophon">
        <Heart size={14} /> 做给每一个在背单词的人。
      </p>
    </div>
  );
}
