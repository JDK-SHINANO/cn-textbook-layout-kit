# 封面与目录：样书《基础有机化学》骨相

用户拿北大社《基础有机化学》（第 4 版）当参照，明确要这套封面与目录的样子。下面是把那套骨相落到本流水线的做法，末尾几条是用户逐条提过的硬要求，别改回去。

## 一、封面（文字一律右对齐）

特征（照照片提炼，并已按用户要求改过）：

1. **白底**，不加底色块；
2. **顶部一条纹样带**：同一单元横向重复、交错两三行，灰阶（#8e8e8e 线、#5f5f5f 实心），高约 58 mm，占封面上三分之一；
3. **大字书名**：无衬线、特粗（900）、33 pt，两行以内；
4. 书名下一行**英文副题**（衬线斜体、10 pt、灰）；
5. **红色版次小标**（#b23a34 底、白字、9 pt，如「第三版 v3」）；
6. 书名上方一行小字标系列（「全四卷 · 本册收入前三卷 17 章」）；
7. 底部一行日期，细、灰。

**所有文字元素右对齐**（`text-align:right`，并且额外写 `.cover p{text-align:right}`——红色版次小标是 `inline-block` 包在 `<p>` 里，只给 `.cover` 设对齐时它靠父块的行盒，容易看着没靠到底）。理由是要合装订习惯：订口在左，视觉重心靠切口（右），读者的手从右边翻。纹样仍通栏 180 mm。核对办法：量封面每行文字的右沿，应全部落在 194.5–195.5 mm（版心右沿），英文斜体可能溢出 0.5 mm。

纹样是**学科的意象**，不是装饰：化学书用苯环阵列，核物理就用「核子＋两条交叉轨道」的重复单元。生成脚本 `工具/make_cover.py`（matplotlib，180×58 mm，透明底 SVG+PNG，写到 `图v3/cover_pattern.*`）：三行交错、行距 15 mm，每单元 = 半径 1.55 的实心核 + 两条 ±28° 的椭圆轨道。换学科只改单元。

封面 HTML 放在 `build_book.sh` 的 heredoc 里，**末尾紧跟一页空白（封二）**：

```html
<div class="cover">
  <img class="cv-pattern" src="图/cover_pattern.png" alt="">
  <p class="cv-series">全四卷 · 本册收入前三卷 17 章</p>
  <h1 class="cv-title">从零开始的<br>核物理与核能</h1>
  <p class="cv-en">Nuclear Physics and Nuclear Energy from Scratch</p>
  <p><span class="cv-tab">第三版 v3</span></p>
  <p class="cv-foot">2026 年 10 月</p>
</div>
<div class="blankpage"></div>
```

CSS 要点：`.cover{position:relative;height:223mm;background:#fff;text-align:right;break-after:page}`；`img.cv-pattern{width:180mm;display:block;margin:0 0 15mm}`（图片不受 text-align 影响）；`.cv-title{font-size:33pt;font-weight:900;line-height:1.2}`；`.cv-tab{display:inline-block;background:#b23a34;color:#fff;padding:1.8mm 4mm}`；`.cv-foot{position:absolute;bottom:4mm;left:0;right:0;text-align:right}`；`.blankpage{height:223mm;break-after:page}`。

**坑**：装配只把 `图v3/ch*/*.svg` 平铺进 `out/图`，封面纹样在 `图v3/` 根下，会被漏掉 → 封面破图。平铺循环后补一条 `for f in "$BOOK"/图v3/*.svg; do ln -sfn "$f" "$OUT/图/$(basename "$f")"; done`。

## 二、版权页（页序：封面 → 空白 → 版权 → 空白 → 目录）

一页，上半留白约 50 mm，居中书名（22 pt 粗）＋副题（11 pt 灰）＋一道 40 mm 主色细线；下面三行 9.5 pt 居中：卷次与内容范围、版次与月份、开本与字号与印色。

**底部说明按用户定的位置摆**：

- 离页面底边约 **60 mm**（`position:absolute;bottom:60mm`），**居中**，不是上一版的左对齐；
- **不用句号**，一句一行（`<br>` 分隔）；
- 内容四行：自印本性质、数据来源去向、排版流水线、插图工具。

版权页后同样补一页空白（`<div class="blankpage"></div>`）。用户把这两页都叫「封面背面」，别问是哪一页——两处都加。

## 三、目录（三层、每章一块、块内双栏）

用户逐条指定的样子：

1. **跨满版心 180 mm，但排版分两区**：章号占**副区**（右对齐），条目只在**主区**；不是全页通栏排字。
2. **每章一条章条**：蓝底**实心方框**里写「第 N 章」（白字、9 pt），**放在副区里右对齐**（框的右沿贴副区右沿 34 mm）；章名从**主区左沿**起（黑体、12 pt、粗），与章号**同一行**；章名后一条主色下划线一直拉到右端，最右是「/ 页码」（如 `/ 69`）；
3. **条目只在主区**：`margin-left:34mm; width:146mm`，主区一分为二；**每章条目左右各半，读序先左后右**（`column-fill:balance`）。章与章之间留 4.6 mm，不是全页连续双栏；
4. **三层字体**：章条＝黑体，二级大节（`N.M`）＝宋体，三级小节（`N.M.K`）＝仿宋、缩进 4.5 mm；
5. 节条目点线引右端页码；章条与它下面的第一节不许断页（`break-after:avoid`）；
6. 目录页**排**页眉「目录」与页码；封面、版权页、空白页不排。

结构（`工具/make_front.py` 生成）：

```html
<div class="toc-chap">
  <div class="toc-bar">
    <span class="toc-no"><span class="toc-box">第 5 章</span></span>
    <span class="toc-name">核反应与截面</span>
    <span class="toc-line"></span><span class="toc-pg">/ 77</span>
  </div>
  <div class="toc-cols">
    <p class="toc-sec lv2"><span class="toc-t">5.1　核反应怎么写</span><span class="toc-dot"></span><span class="toc-p">77</span></p>
    <p class="toc-sec lv3">…</p>
  </div>
</div>
```

CSS（标注「用户改定」的两处是第二轮纠正的核心）：

```css
.toc-bar{display:flex;align-items:baseline;break-after:avoid}
/* 章号在副区里右对齐：flex 子项固定 34mm，内部 justify-content:flex-end */
.toc-no{flex:0 0 34mm;display:flex;justify-content:flex-end;padding-right:3mm;box-sizing:border-box}
.toc-box{background:var(--accent);color:#fff;font-family:var(--sans);font-size:9pt;font-weight:700;padding:.9mm 1.8mm;white-space:nowrap}
.toc-name{font-family:var(--sans);font-weight:700;font-size:12pt;margin-left:0}
.toc-line{flex:1;border-bottom:.75pt solid var(--accent);margin:0 2.2mm 1.6mm}
.toc-pg{font-family:var(--sans);font-size:8.5pt;color:var(--accent)}
/* 条目只在主区，每章左右各半（用户改定） */
.toc-cols{margin-left:34mm;width:146mm;column-count:2;column-gap:7mm;column-fill:balance;margin-top:1.6mm}
.toc-sec{display:flex;align-items:baseline;margin:0;text-indent:0;break-inside:avoid}
.toc-sec.lv2{font-family:var(--serif);font-size:8.8pt;line-height:13.2pt}
.toc-sec.lv3{font-family:"仿宋","FangSong",serif;font-size:8.3pt;line-height:12.4pt;padding-left:4.5mm}
.toc-sec .toc-dot{flex:1;border-bottom:.5pt dotted #b9c6d2;margin:0 1.6mm 1.1mm}
.toc-sec .toc-p{font-family:var(--sans);font-size:8pt;min-width:6mm;text-align:right}
```

**坑：`column-fill:auto` 会让「只有长章分两栏」**。auto 先把左列堆到底，短章的条目全留在左列，只有条目多的章（附录 C）溢出到右列——成品上就是「为什么只有公式速查分成两半」。用户要的是每章条目左右各半、读序先左后右 → **`balance`**。核对办法：抽一章数左右列条目（应相近，如 31/31），而不是看总页数。

**条目来源不是手抄**：`工具/toc_pages.py` 读 `doc.get_toc()`，导出 lvl 1（章／题解／附录）与 lvl 2（节）、lvl 3（小节）到 `src/toc_entries.json`；`make_front.py` 按 json 生成 HTML。为此 `finish.py` 的书签必须**收到 h3**：`headings()` 的匹配式加上 `<h3[^>]*>.*?</h3>`，并把 `<span class="h3no">N.M.K</span>` 重构成「N.M.K　标题」，否则目录第三层永远空着。导出时的层级过滤写 `if lvl > 3: continue`——写成 `> 2` 会把三级小节静默丢掉（实测 164 条 vs 525 条），目录少一层却不报错，只能从条目数对不上（24 章却只有 164 条）看出来。首装时 json 不存在，退回「只列章」的简目，装完跑一次再装即得全目。

## 四、装配顺序（页码互相牵动，别乱）

```
装书 → toc_pages.py（写 entries）→ 装书（目录页码准）
     → index_pages.py（重算索引页码）→ 装书 → index_pages.py（复核不变）
```

前置页条数固定后，页码写入不改分页；但**任何改分页的改动（加前置页、修正文、补图）都会让上一轮的目录与索引页码一起失效**。

**改封面/目录样式时先试排两章**：`CHAPTERS="01 02" OUTNAME=试两章 ./build_book.sh` 只装 80 余页，一轮不到一分钟，目录两遍校准也快；样式经用户认可再动全书（全书一轮约四分钟）。试排本可用 `doc[i].get_text()` 逐行量右沿、数左右列条目数，不必靠目测。

## 五、页眉归属与书签定位

`finish.py` 里从前置页判断：

- 封面（第 1 页）不排；版权页与空白页不排；
- 目录页**排**，标签固定「目录」，页码照常；
- `first_chap` 从 `doc.get_toc()` 取第一章页码，不要用 `p == 0` 了事。

**先修书签，再修页码**：`locate()` 按文字找标题位置，而目录把每个标题都印了一遍。不跳过目录页，全部书签都指到目录上，`first_chap` 也算错，随后 `toc_pages.py` 与 `index_pages.py` 一起崩（症状：索引「未找到页码」两三百条、附录 D 起于第 3–5 页）。判目录页：页首 24 字内出现「目录」，或该页同时含「目录」「附录」。改完先看 `doc.get_toc()[:3]` 是否落在正文页。

**目录页断页只留一处**：`.tocpage` 不写 `break-after:page`，交给下一章 `h1.chapo` 的 `break-before:page`；`front.md` 末尾也不补 pagebreak。多断一次就多一页白页。

## 六、渲染速度（用户问过，先把数摆出来）

377 页、80 幅 SVG、上千行内公式的一次全装：pandoc＋塑形 0.5 s，Chromium 打印约 180 s，`finish.py` 原 199 s、改造后 21 s，索引 7 s。

- **`finish.py` 的 `locate()` 不要边搜边 `doc[p].get_text()`**：164 条标题 × 372 页 = 六万次取文本，实测 199 秒。→ 先 `raw=[doc[i].get_text() for i in range(n)]`、`page_texts=[re.sub(r"\s+","",t) …]`，`locate(items, page_texts, skip=toc_pages)`，降到 2 秒级。
- **`doc.save(garbage=3)` 很贵**（24 MB 书全量重写＋去重，60 s）；改 `garbage=1, deflate=True` 即可，页眉页码不受影响。
- Chromium 那 180 s 是渲染器本身：分页媒体、SVG、KaTeX 全量排版。社区路线（Typst 毫秒级、Paged.js 更慢）已在会话里核对过；迁 Typst 是另一次重写，现阶段不划算。**降低迭代成本靠少装几遍**：目录与索引各只需两遍，别做无谓的复核装书。

## 七、交付路径

给用户成品时，给**源产物** `版式对照_有机化学风/out/全书_v3.pdf`；`BOOK/` 根下那份 `从零开始的核物理与核能_v3.pdf` 是旧拷贝，改版后极易过期。要拷到根目录也行，但拷完立刻给根目录路径，别两种路径混着给。
