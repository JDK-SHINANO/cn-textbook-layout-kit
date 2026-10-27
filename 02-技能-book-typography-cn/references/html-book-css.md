# 排版改造方案

**对象**：`核物理课本/src/template.html`、`tools/pdf_finish.py`、`code/bookstyle.py`、`src/ch*.md`（结构级，少量）
**不改**：`build.sh` 的流程、`src/book.md`（自动生成）
**目标数值**：正文 10.5 pt / 行距 17 pt / 40 字/行 / 39 行/页 / 版心 148×234 mm / 天头 28 / 地脚 35 / 订口 32 / 切口 30

---

## 0 三句话结论

1. **全书（259→288 页）的字号、行距、图注、表格都被乘了 0.889**，因为一个超宽的行间公式触发了 Chrome 的"缩放到页宽"。问题在参数没生效，与设计好不好看无关。先修这一条，其它改动才有意义。
2. 修好之后，**行距与段距的层级是反的**（行间 1.72 倍偏松，段距 1.9 pt 几乎为零），标题层级也失效（h3 只比正文大 0.5 pt）。
3. 第三层是**结构化内容没有结构**：练习解答 6 步挤成一段、表格 ①②③ 连排、单元格公式断行。这一层得改源文件，CSS 管不到。

**影响排序：先修全局缩放，再修纵向节奏，最后修结构。**

---

## 1 先修"整体缩放"（P0，影响全书每一页）

### 1.1 证据

| 实验（同 HTML，只改一处，各自重渲染全书） | 正文字号 | 页数 |
|---|---|---|
| 原文 | 9.34 pt | 259 |
| A：删掉所有 `<table>` | 9.34 pt | 214 |
| B：`table{table-layout:fixed}` | 9.34 pt | 259 |
| C：`.katex-display{overflow-x:auto;max-width:100%}` | **10.46 pt** | 303 |
| D | 完整新 CSS（表 9 pt + 固定列宽，格内公式仍 nowrap） | 9.60 pt | 296 |
| E | D + `td .katex{white-space:normal}` | **10.46 pt** | 370 |
| 基线（空白 HTML，同字体） | 10.50 pt | 1 |

`.katex-display` 在 `@media print` 里是 `overflow:visible`（template.html **第 231 行**），一个 166.5 mm 宽的公式成了"可见溢出"，把页面盒撑宽；Chrome 为把 166.5 mm 塞进 148 mm 的可打印区，把**整份文档**缩到 0.889，`@page` 的毫米边距不跟着缩，所以边距精确、字号全错。

### 1.2 改法

把 `.katex-display` 改成溢出容器（§2 的完整 CSS 已含）：

```css
.katex-display{ max-width:100%; overflow-x:auto; overflow-y:hidden; }
```

**溢出源有两个。** 实验 C 只解决了行间公式；换上完整新 CSS（表格 9 pt + 固定列宽）后字号又掉回 9.60（实验 D），因为表格单元格里的行内公式在窄列里被 KaTeX 的 `nowrap` 顶了出去。加上 `td .katex{white-space:normal}` 才回到 10.46（实验 E）。§2 的 CSS 里这两条都必须在。

**副作用（要让甲方知道）**：页数 259 → **370**（实测，未加列宽）。现在的 259 页本来就是“把 10.5 pt 缩成 9.34 pt”换来的，不是这本书真有这么紧凑。加上 §4.2 的逐表列宽后，表格行高会降一截，预计落到 **300–320 页**。若必须压回 270 页以内，见 §2.4 的取舍表；**这个取舍要甲方拍板，不要由排版方自己定。**

**验收**：重渲染后量正文 span 字号，应为 **10.46–10.50 pt**（实测 10.46；残余 0.4% 来自一处 148.6 mm 的元素，可接受）。页数只记录，不作判据，它会随表格列宽在 300–370 之间变动。

> 残余 0.4%：C 实验仍是 10.46 而不是 10.50，说明还有一个 148.6 mm 宽的元素。修完主因后，用 §6 的 `scrollWidth` 检查逐个找出来（候选：某张 5 列表、某个 `pre` 块、目录里某条 `nowrap` 行）。

---

## 2 完整 CSS（整段替换）

### 2.1 印刷部分：替换 template.html **第 147–279 行**（`@media print{…}` 整块）

```css
/* ============================================================
   印 刷（A4 210×297）
   版心 148×234 · 天头 28 · 地脚 35 · 订口 32 · 切口 30
   正文 10.5pt / 行距 17pt / 40 字 × 39 行 = 1560 字/页
   ============================================================ */
@media print{
  @page{ size:A4; margin:28mm 30mm 35mm 32mm; }
  @page:right{ margin:28mm 30mm 35mm 32mm; }   /* 单页码：订口在左 32 */
  @page:left{  margin:28mm 32mm 35mm 30mm; }   /* 双页码：订口在右 32 */
  @page:first{ margin:0; }                     /* 封面满版，必须放在最后 */

  /* ---------- 字与行 ---------- */
  html{ font-size:10.5pt; }
  body{
    background:#fff; color:#111;
    font-size:10.5pt; line-height:17pt;        /* 绝对行距，不用 1.72 这种小数 */
    text-align:justify; orphans:3; widows:3;
    text-autospace:normal;                     /* 中西文间 1/4 字空（clreq） */
    text-spacing-trim:trim-start;              /* 行首行尾标点挤压 */
  }
  .wrap{ display:block; max-width:none; }
  nav#TOC{ display:none; }
  main{ padding:0; margin:0; max-width:none; max-height:none; overflow:visible; }

  p{ margin:0; text-indent:2em; line-height:17pt; }
  p + p{ margin-top:0; }                       /* 段距归零，界线交给缩进 */
  ul,ol{ padding-left:2em; margin:8.5pt 0; }
  li{ margin:0 0 2pt; line-height:17pt; }
  li p{ text-indent:0; margin:0; }

  /* ---------- 标题：字族 + 字号双通道 ---------- */
  h1:not(.cover-title){
    font-family:"Noto Sans CJK SC","Source Han Sans SC","Noto Sans SC",sans-serif;
    font-size:25pt; line-height:1.3; font-weight:700;
    letter-spacing:.01em; color:#000;
    margin:0 0 10mm; padding:0; border:none; background:none;
    break-before:page; page-break-before:always;
    break-after:avoid; page-break-after:avoid; break-inside:avoid;
  }
  h1:not(.cover-title)::before{                 /* 章题降位 32mm（不用 margin-top，分页处会被折叠） */
    content:""; display:block; height:32mm;
  }
  h1:not(.cover-title)::after{                  /* 题下 40mm 短横线，替代原来的 4pt 竖条 */
    content:""; display:block; width:40mm; height:1.6pt;
    background:#8c5a2b; margin-top:6mm;
  }
  h2{
    font-family:"Noto Sans CJK SC","Source Han Sans SC",sans-serif;
    font-size:14pt; line-height:1.35; font-weight:700; color:#000;
    margin:34pt 0 8.5pt; padding:0; border:none;
    break-after:avoid; break-inside:avoid;
  }
  h3{
    font-family:"Noto Sans CJK SC","Source Han Sans SC",sans-serif;
    font-size:11.5pt; line-height:1.4; font-weight:700; color:#1a1a1a;
    margin:25.5pt 0 4.25pt;
    break-after:avoid; break-inside:avoid;
  }
  h1 + p, h2 + p, h3 + p{ text-indent:2em; }

  /* ---------- 图 ---------- */
  figure{
    margin:17pt 0 8.5pt; text-align:center; max-width:100%;
    break-inside:avoid; page-break-inside:avoid;
  }
  img{ max-width:100%; height:auto; margin:0 auto; padding:0;
       border:none; border-radius:0; box-shadow:none; background:none; }
  figcaption{
    font-size:9pt; line-height:13pt; color:#333;
    margin:2mm auto 0; max-width:118mm; text-align:left;   /* 两行以上不居中 */
    break-before:avoid; page-break-before:avoid;
  }
  figcaption p{ text-indent:0; margin:0; }
  .fig-mid{ width:72mm; }        /* 半栏图（配合源文件 class） */
  .fig-third{ width:46mm; }      /* 三分图 */

  /* ---------- 表 ---------- */
  table{
    font-size:9pt; line-height:13pt; width:100%;
    table-layout:fixed;                        /* 严格按 colgroup 分配，不按内容抢宽 */
    border-collapse:collapse;
    border-top:1pt solid #000; border-bottom:1pt solid #000;
    margin:8.5pt 0 17pt;
  }
  caption{ caption-side:top; text-align:left; font-size:9.5pt;
           font-weight:700; padding-bottom:4pt; }
  thead{ display:table-header-group; }         /* 跨页重复表头 */
  thead th{ border-bottom:.5pt solid #000; font-weight:700; border-top:none; }
  th,td{ padding:2.2pt 3pt; border:none; vertical-align:top; text-align:left; }
  tbody tr{ break-inside:avoid; page-break-inside:avoid; }
  tbody tr:nth-child(even), tbody tr:hover{ background:none; }
  td.num, th.num{ text-align:right; font-variant-numeric:tabular-nums; }
  td .katex, th .katex{ white-space:normal; }  /* ★ 格内公式必须可断，否则整张表被推出页面 → 全书缩放 */

  /* ---------- 引文 / 代码 ---------- */
  blockquote{
    margin:17pt 0; padding:0 0 0 5mm; background:none;
    border-left:1.5pt solid #c8a97e; border-radius:0;
    font-size:10pt; line-height:16pt;
  }
  blockquote p{ text-indent:0; margin:0 0 4pt; }   /* 引用块首行不再缩 2em（原第 222 行双重缩进） */
  blockquote > :first-child{ margin-top:0; }
  blockquote > :last-child{ margin-bottom:0; }
  code{ font-size:.9em; background:none; padding:0; color:#000;
        font-family:"DejaVu Sans Mono",monospace; }
  pre{ font-size:8.4pt; line-height:12pt; background:#f5f5f5;
       border:.4pt solid #bbb; border-radius:2pt; padding:4pt 5pt;
       white-space:pre-wrap; word-break:break-all;
       max-width:100%; break-inside:avoid; margin:8.5pt 0; }
  pre code{ font-size:1em; }

  /* ---------- 公式 ---------- */
  .katex-display{
    margin:17pt 0; padding:0;                   /* 上下各 1 行 */
    max-width:100%; overflow-x:auto; overflow-y:hidden;  /* ★ 关键：不许溢出，否则全书被缩放 */
    break-inside:avoid;
  }
  .katex{ font-size:1em; }                     /* 不设 nowrap：KaTeX 自带 nowrap，公式过长会撑出页面 */
  .katex-error{ color:#b00; }
  .eqrow{ display:block; position:relative; }
  .eqrow .eqno{ position:absolute; right:0; top:0; transform:none;
                font-size:10pt; color:#444; font-variant-numeric:tabular-nums; }

  /* ---------- 屏幕专用件在纸上消失 ---------- */
  hr{ display:none; }
  a{ color:#000; text-decoration:none; }
  .ref-todo{ color:#555; border-bottom:none; }

  /* ---------- 封面 ---------- */
  .cover{
    margin:0; width:210mm; height:297mm;
    display:flex; flex-direction:column; justify-content:space-between;
    align-items:center; text-align:center;
    padding:88mm 30mm 47mm;                     /* 标题块上沿 ≈88mm（页高 30%） */
    break-after:page; page-break-after:always; break-inside:avoid;
  }
  .cover-inner{ max-width:none; }
  .cover-kicker{ font-size:10pt; letter-spacing:.42em; margin-bottom:14mm; color:#7a4f26; }
  .cover-title{ font-size:34pt; line-height:1.32; margin:0 0 9mm; letter-spacing:.02em;
                break-before:avoid; page-break-before:avoid; font-family:inherit; }
  .cover-rule{ width:44mm; height:1.6pt; margin:0 auto 8mm; }
  .cover-sub{ font-size:13pt; line-height:1.9; color:#333; }
  .cover-foot{ font-size:9.5pt; line-height:2.1; color:#555; margin:0; }

  /* ---------- 印刷目录 ---------- */
  .tocprint{ display:block; break-after:page; page-break-after:always; }
  .tocprint h2.tochead{
    font-size:17pt; text-align:center; letter-spacing:.5em; font-weight:700;
    margin:6mm 0 10mm; padding:0; border:none;
  }
  .tocprint .row{
    display:flex; align-items:baseline; gap:4mm; white-space:nowrap;
    font-size:9.5pt; line-height:18pt;
  }
  .tocprint .row.l1{
    font-weight:700; font-size:11pt;
    margin-top:8.5pt;                            /* 章前空 0.5 行，不是 4.6pt */
    font-family:"Noto Sans CJK SC",sans-serif;
  }
  .tocprint .row.l2{ padding-left:2em; color:#222; font-size:9.5pt; }
  .tocprint .t{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .tocprint .dots{ flex:1 1 auto; border-bottom:.5pt dotted #999;
                   transform:translateY(-.22em); min-width:2em; }
  .tocprint .pg{ text-align:right; white-space:nowrap; width:8mm;
                 font-variant-numeric:tabular-nums;
                 font-family:"DejaVu Sans Mono",monospace; font-size:9pt; }
  .tocprint .row.l1 .pg{ font-size:9.5pt; }

  /* ---------- 溢出保险丝（配合 §1 的根因修复） ---------- */
  .wrap, main, figure, table, pre, blockquote, .katex-display{ max-width:100%; }
  td, th{ overflow-wrap:anywhere; }             /* 长公式/长单词在格内折，不撑宽表格 */
}
```

**关键差异一览**

| 项 | 现值 | 新值 | 为什么 | 预期效果 |
|---|---|---|---|---|
| `@page` 边距 | 24/29/24/33 | 28/30/35/32 | 地脚 > 天头（视觉重心上移）；订口补偿胶装可视角 | 书"站"起来，不飘 |
| 正文字号 | 10.5 pt（实渲染 9.34） | 10.5 pt（真 10.5） | 修溢出，恢复设计值 | 单字视角 22.6′→25.4′ |
| 行距 | 1.72（18.06 pt） | 17 pt | 科技读物规格 17.06 pt；整数格 | 39 行正好 234 mm |
| 每行字数 | 40（实 43） | 40 | 修字号后自然回到 40 | 回扫次数 −7% |
| 段距 | .18em（1.9 pt） | 0 | 中文用缩进不用段距 | 段落有界线，页不虚 |
| h1 | 20 pt 顶格、左竖条 | 25 pt 降位 32 mm、短横线 | 章首页"开场" | 翻章有明显停顿 |
| h2 | 13 pt | 14 pt 黑体 | 层级 1.33 倍 + 换族 | 节一眼可辨 |
| h3 | 11 pt 宋体粗 | 11.5 pt 黑体 | 换族建立第 3 级 | 不再是"粗正文" |
| 图注 | 9 pt / 55% 行高 / 4.6 mm | 9 pt / 13 pt / 2 mm / 左对齐 118 mm | 图注必须贴图 | 图注归属明确 |
| 表格 | 8.6 pt、均分列 | 9 pt、fixed + colgroup | 列宽按内容 | ①②③ 不再糊 |
| 公式 | 上下 .85em（7.9 pt） | 17 pt | ≥ 1 行 | 公式自成一块 |
| 行内公式 | KaTeX 自带 `nowrap` | 不设全局 nowrap；`td .katex{white-space:normal}` | 公式一旦宽过版心，就把全书顶小 | 全书字号回到 10.46 pt |

### 2.2 屏幕部分：替换/修改 template.html 的 4 处

| 行 | 现值 | 新值 | 为什么 |
|---|---|---|---|
| 23 | `html{font-size:17px}` | 不变 | 17 px 在屏幕上等于 12.75 pt，合理 |
| 28 | `line-height:1.8` | `1.75` | 1.8 太散，屏幕 1.7–1.8 的中间值更稳 |
| 55 | `main{… max-width:800px; padding:2.8rem 3rem}` | `max-width:720px; padding:2.8rem 3rem 6rem`（`max-width` 含 padding） | 800−96=704 px ≈ 41.4 字 → 720−96=624 px ≈ **36.7 字**，落在屏幕 34–40 字区间中部 |
| 76–78 | `figcaption{color:var(--ink-3)}` | `color:#5b5349` | 实测对比度 4.43:1，低于 AA 的 4.5:1；改后 7.18:1 |
| 65 | `p{margin:0 0 .38em}` | `margin:0 0 .55em` | 屏幕用段距（0.55em ≈ 9.35 px），纸上用缩进 |


### 2.3 一页纸上的效果预演

- 版心 148×234，39 行 × 40 字 = 1560 字/页。
- 页数：341 000 ÷ 1560 ≈ 219 页纯文字 + 70 图（每图约 0.55 页）+ 72 表 ≈ **370 页（实测，未加列宽）**；逐表加 colgroup 后 **300–320 页**。
- 现在的 259 页是缩到 88.9% 换来的，并不真的紧凑。验收时不要把页数变多当成退步。

---

### 2.4 页数与字号的取舍（必须甲方拍板）

| 方案 | 字号 | 行距 | 每行 | 版心 | 实测页数 | 单字视角 50/60 cm | 代价 |
|---|---|---|---|---|---|---|---|
| 现状 | 9.34 | 16.01 | 43 | 148×249 | 259 | 22.6′ / 18.8′ | 字小、行长超、边距偏 |
| **A 标准（本方案）** | 10.5 | 17 | 40 | 148×234 | **370** | 25.4′ / 21.2′ | 页数 +43% |
| B 保页数 | 10 | 16.5 | 42 | 155×234 | **352** | 24.2′ / 20.2′ | 字号未达五号；页数仍 +36% |
| C 待测 | 10.5 | 17 | 40 | 148×234 + 逐表列宽 | 目标 ≤ 310 | 25.4′ / 21.2′ | 需重做 72 张表 |

**页数增长的主因在表格，不在正文。** 72 张表在 9 pt + 允许格内断行后，单表高度普遍 ×1.5–2（占了增量里约 95 页）。把"符号/术语"列压到 20 mm，长文本列放到 70 mm（§4.2 的 colgroup），表格高度能降回接近原状。这一步必须逐表做；批量套比例会适得其反，我用统一比例试过一次，页数反而涨到 400。

所以排序是：**A 的字号 + 逐表列宽 = 300–320 页**（可接受）；只做 A 不做列宽 = 370 页（偏高）。

---

## 3 需要改代码的 3 处（CSS 管不到）

### 3.1 `tools/pdf_finish.py`

| 行 | 现值 | 新值 | 理由 |
|---|---|---|---|
| 180 | `H - 14*72/25.4` | `H - 15*72/25.4` | 页码距下沿 15 mm，落在地脚 35 mm 的中线偏下，避开拇指 |
| 185 | `y = 13.5*72/25.4` | `y = 19*72/25.4` | 书眉基线距顶 19 mm（距版心 9 mm），天头 28 mm 才放得下 |
| 187–188 | `left_in = 33 if … else 29` | `32 / 30` | 与新的订口 32 / 切口 30 对齐 |

### 3.2 `code/bookstyle.py`（70 幅图的字都偏小）

现参数：`figsize` 宽 6.45 in、刻度 9 pt、图例 8.5 pt、坐标轴标签 10.5 pt。
印刷宽 148 mm = 5.83 in → 缩放 5.83/6.45 = **0.904**；再乘全书 0.889 的 bug → **0.804**。所以刻度实际 7.2 pt、图例 6.8 pt。

| 参数 | 现值 | 新值 | 印后字号（修 bug 后） |
|---|---|---|---|
| `xtick.labelsize` / `ytick.labelsize` | 9 | **10** | 9.04 pt ✓ |
| `legend.fontsize` | 8.5 | **9.5** | 8.6 pt ✓ |
| `axes.labelsize` | 10.5 | **11.5** | 10.4 pt |
| `axes.titlesize` | 11 | **12** | 10.8 pt |
| `font.size` | 10 | **10.5** | 9.5 pt |

**另一个办法**：把 `figsize` 宽度统一改成 **5.83 in**（= 148 mm），字号直接用印刷值（刻度 9、图例 9、标签 10.5），出图即所见，不再有缩放换算。

窄图（半栏 72 mm）不要靠 `max-width` 缩，要单独出一版 `figsize=(2.83, h)` 的图；缩一半的图里 9 pt 会变成 4.5 pt。

### 3.3 需要新增的小工具（建议）

1. **表格 colgroup 注入器**（`tools/table_cols.py`）：读 HTML，按每列平均字符数分配宽度，写回 `<colgroup>`。规则：每列 ≥ 15%，单列 ≤ 60%，按 §9.2 的比例表微调。
2. **填充率检查器**（`tools/fill_check.py`）：对每页算"最低墨迹 y ÷ 版心高"，< 0.75 的页打印出来，人工决定缩版/挪图。当前至少 8 页会中招（p11、p28、p83、p147、p198、p210 等）。

---

## 4 需要改源文件的 3 类结构（CSS 治不了）

### 4.1 练习解答：一步一行（对应抱怨 ⑥）

`src/ch01.md` 第 54、108、215 行等处把解答写成"第 1 步，…第 2 步，…"的连续段落。改法：

```markdown
**解**

1. 质子数直接读记号左下角：$Z=6$。
2. 中子数由 $A=Z+N$ 反解：$N=14-6=8$。
3. 核电荷：$Q=+Ze=6\times1.602\times10^{-19}=9.61\times10^{-19}$ C。
4. 核质量按质量数估：$m\approx Au=14\times1.6605\times10^{-27}=2.32\times10^{-26}$ kg。
```

规则：**每个"第 N 步"必须是独立的 `<li>`**；单步超过 3 行时，把算式单独成行（行间公式），不要塞在句子里。

### 4.2 表格：逐表设列宽 + 单元格 ①②③ 一条一行（对应抱怨 ②，**P0，不做则页数 +95**）

现状（p9/p10 符号表）：一格四条，全在一段里。改法：

```html
<td>① 库仑常数 8.988×10⁹ N·m²/C²（第 1 章）<br>
    ② 有效增殖因子（第 6 章起，无量纲）<br>
    ③ 玻尔兹曼常数 8.617×10⁻⁵ eV/K（第 13 章）<br>
    ④ 张力项 0.9 GeV/fm（第 16 章）</td>
```

配 `colgroup`（18% : 52% : 30%）+ `table-layout:fixed`。

### 4.3 图：加 class 分档 + 单页图

源文件里给图加属性即可（pandoc 会把 `{width=…}` 变成 style，但更稳的是在 md 里写原始 HTML `<figure class="fig-mid">`）：

| class | 宽 | 用在哪 |
|---|---|---|
| 默认（无 class） | 148 mm | 双联/三联图、宽表图 |
| `fig-mid` | 72 mm | 单幅曲线、示意 |
| `fig-third` | 46 mm | 小图标 |
| `fig-page` | 整页 | 图高 ≥ 180 mm |

---

## 5 七条抱怨逐条回应

### ① 总体"怪"——怪在三个参数错配（不是审美）

| 你以为看到的 | 实际参数 | 结果 |
|---|---|---|
| "字有点小" | 9.34 pt（不是 10.5） | 单字视角 22.6′，接近舒适下限 |
| "行有点长" | 每行 43 字（不是 40） | 每行多 3 次注视、回扫落点误差 +7% |
| "行距松、段又粘" | 行距 1.72 / 段距 1.9 pt | 竖向节奏的信号给反了 |
| "标题不够气派" | h1 1.91×、h3 1.05×，同族宋体 | 层级靠"大一点、粗一点"，容量不足 |
| "表格看不清" | 3 列均分 43/49/46 mm | 长文本列只有 13 字/行 |

**一次归因**：字号是"小五"，行长是"五号 40 字"，行距是"文学书"，标题是"网页 h1"。四种排版传统混在一页上，读者的眼睛找不到规律。

**改法**：§1 修缩放 + §2 全套 CSS。**改完，"怪"会消失，但页数会涨 25 页左右。**

### ② 表格列宽与单元格换行

**症状（实测）**：p9 三列 43/49/46 mm；第 2 列每格 3–4 条 ①②③，13 字/行，最高 9 行；`8.988×10⁹ N·m²/C²` 在 13 字宽里断成两行；p235 四列 49/25/25/49，英文列把 `average logarithmic energy decrement ξ` 断成 3 行。

**违背**：§9.2 列宽按内容分配；§9.3 一条一行；§9.4 数字对齐。

**改法**：
1. `table-layout:fixed` + `<colgroup>`，按内容比例（3 列 18:52:30；4 列 24:22:12:42）。
2. 单元格内条目用 `<br>` 分行。
3. `td .katex{white-space:nowrap}`。
4. 数字列 `class="num"` → 右对齐 + tabular-nums。
5. 单元格左右内边距从 0.5em 收到 3 pt（省 40% 宽度）。

**预期**：同一张符号表从 9 行/格降到 5 行/格，表高降 30%，p28 那种"表后 142 mm 空白"也会连带减少。

### ③ 子内容缩进不统一

**症状（实测左边界）**：正文续行 33.1 mm（含 math span 时 30.4）、表格首列 34.4、列表序号 35.0、正文首行 35.7、引用块文字 38.7、引用块首行 42.6。**6 种左边界，最大差 12.2 mm**。读者说不出，眼睛会"绊"。

**成因**（都在 template.html）：
- 第 222 行 `blockquote p{margin:.2em 0; text-indent:2em}` → 引用块本身有 5 mm padding，段首又缩 2em = **双重缩进**。
- 第 170 行 `ul,ol{padding-left:1.9em}` → 列表序号在 1.9em 处，但 `<li>` 的 marker 默认在外侧，实际落在 1.9em − 1.2em ≈ 0.7em，比块内文字左凸 3.7 mm。
- 表格 `th,td{padding:.3em .5em}` → 首列文字比版心右移 5.25 mm。

**改法**：
1. `blockquote p{text-indent:0}`（引用块内不再缩进，用 4 pt 段距分段）。
2. `ul,ol{padding-left:2em}` + marker 与文字对齐：`li{padding-left:.2em}`。
3. 缩进只允许 4 档：0 / 1em / 2em / 3em（悬挂）。
4. 表格首列 padding 收到 3 pt。

**验收**：全书出现过的左边界值集合 ≤ 5 个（版心左 32、表格内 32+3pt、列表 32+2em、正文首行 32+2em、引用 32+5mm）。

### ④ 插图能不能左右旁置

**可以，但先算代价。**

148 mm 单栏减去 72 mm 图 + 6 mm 间距 = **70 mm 正文 = 19 字/行**，低于 20 字的舒适下限。绕排的那 5–8 行会变成"窄条文字"，读者的回扫节奏被打断两次（进窄条、出窄条）。所以：

| 方案 | 可行性 | 做法 |
|---|---|---|
| 真旁置（文字绕排） | ✗ 不建议 | 5–8 行 19 字/行，得不偿失 |
| **图注式旁置** | ✓ 推荐 | 图 72 mm + 图注放图**右侧** 60 mm（flex 两列），整体不占额外垂直空间 |
| 半栏居中 | ✓ 最稳 | 图 72 mm 居中，图注在图下 2 mm |

**图注式旁置的 CSS**（需给图加 `<figure class="fig-side">`）：

```css
figure.fig-side{ display:flex; gap:6mm; align-items:flex-start; margin:17pt 0; }
figure.fig-side img{ width:72mm; flex:0 0 72mm; }
figure.fig-side figcaption{ flex:1 1 auto; max-width:none; margin:0; text-align:left; }
```

**用在哪些图**：图 1-1（三种原子模型，148 mm 太宽，其实三联各 46 mm 更好）、图 0-1（全书地图，高 191 mm，应整页）、图 6-4（4 联液滴，应改 2×2 各 72 mm）。旁置的适用条件是"图宽 ≤ 88 mm 且图高 ≤ 70 mm"，本书符合的图不到 15 幅。

### ⑤ 插图缩放后字号是否匹配

**不匹配，差 20%。**

计算链：`figsize=6.45 in` → 印到 148 mm（5.83 in）= **0.904**；再乘全书 0.889 的 bug = **0.804**。
- 刻度 9 pt → **7.2 pt**
- 图例 8.5 pt → **6.8 pt**
- 最小标注 8.5 pt → **6.8 pt**

判据：图内最小字 ≥ 7.5 pt（正文 10.5 的 0.71 倍，印刷业下限）。**现状全部踩线或越线。**

**改法**：见 §3.2 的参数表。修完 bug 后刻度 9.0 pt、图例 8.6 pt，达标。

**逐图自查**（可写进验收脚本）：`s' = s × 148 / (25.4 × figsize_w)`，要求 ≥ 7.5。

### ⑥ 练习题步骤要一行一步

**症状**：p22 三道题的解答各 5–6 步，全写成连续段落，单段 13–15 行；"第 1 步…第 2 步…"淹没在正文里；行内公式折断 4 处（`2.99×10` / `⁻²⁶ kg` 分处两行）；题与题之间仅 5.7 mm。

**改法（两步）**：
1. **源文件**：把"第 N 步"改写成 `<ol><li>`（§4.1）。
2. **CSS**：`ol` 悬挂缩进 + 步骤间 2 pt + 题间 17 pt。

```css
ol.steps{ padding-left:1.6em; margin:8.5pt 0 12pt; }
ol.steps > li{ margin:0 0 2pt; line-height:17pt; }
ol.steps > li::marker{ font-weight:700; }
```

**效果**：读者可以指着"第 3 步"说"这里不懂"，不必整段重读。

### ⑦ 文风的"AI 味"——可操作的识别清单

不是"读起来像 AI"，而是一组可数的特征。本书实测（34.1 万字）：

| 特征 | 本书频次 | 每千字 | 健康区间 | 判定 |
|---|---|---|---|---|
| 破折号 `——` 作插入语 | **501** | 1.47 | ≤ 0.40 | **超 3.7 倍** |
| "不是…而是 / 不是…是" | **60** | 0.18 | ≤ 0.05 | 超 3.6 倍 |
| "这就是…" 段末收束 | **86** | 0.25 | ≤ 0.08 | 超 3 倍 |
| 标题用逗号对偶（"三个实验，三种模型"） | **36 / 455** | 7.9% | ≤ 2% | 超 4 倍 |
| 每节末尾"一句话"总结 | 15 | — | 0 | 删 |
| 三段排比（"不…不…不…"） | 高频（未精确计） | — | 0 | 删 |

**五条改写规则**：
1. **破折号改括号或句号。** 插入语用（），转折用句号断句。破折号每页最多 1 个。
2. **删掉"不是 A 而是 B"的否定铺垫。** 直接说 B。否定式只用于纠正一个读者确实会犯的错。
3. **删掉段末的"这就是…"总结句。** 结论已经在正文里，不必再说一遍。
4. **删掉开头的问题句（"为什么只有重核走这条路？"）。** 直接给答案，问题留给标题。
5. **长句拆到 40 字以内。** 一句一个信息点。

**改写示例**（`src/ch03.md` 真实段落）：

原文：
> 为什么只有重核走这条路？这里有个容易说反的地方。**被人扔出去的那个包裹必须特别结实**：氦-4 在这一段轻核里是独一无二的紧——每核子 7.07 MeV（氘只有 1.11、氚 2.83、锂-6 5.33，要一直数到碳-12 才追到 7.68），4 个核子合起来 28.3 MeV——把这么紧的一团原样搬走，才谈得上"赚"。

改后：
> α 衰变只发生在重核，原因在能量账上。
>
> **扔出去的那一团必须特别紧。** 氦-4 每核子 7.07 MeV，在轻核里最高（氘 1.11，氚 2.83，锂-6 5.33，直到碳-12 才追到 7.68），四个核子合起来 28.3 MeV。只有这么紧的一团，原样搬走才谈得上赚。

改动：删问题句（−9 字）、删"这里有个容易说反的地方"（元话语）、2 个破折号 → 0、长句 62 字 → 3 句 18/28/18 字、粗体从半句移到整句。

**批量自查命令**：
```bash
cd src && grep -o "——" ch*.md | wc -l            # 目标 ≤ 137（0.4/千字）
grep -o "不是[^。]\{2,30\}而是" ch*.md | wc -l    # 目标 ≤ 17
grep -o "这就是" ch*.md | wc -l                    # 目标 ≤ 27
```

---

## 6 验收（改完必跑）

```bash
cd <书目录>
./build.sh                       # 两遍渲染：目录页码回填 → 书眉页码
pdfinfo 教材/从零开始的核物理与核能.pdf | grep Pages

# 1) 字号与行距（应为 10.5 / 17.0）
P=${PYMUPDF:-python3}
$P - <<'EOF'
import pymupdf as fitz
from collections import Counter
d=fitz.open("教材/从零开始的核物理与核能.pdf"); p=d[21]
sz=Counter(); ys=[]
for b in p.get_text("dict")["blocks"]:
    for l in b.get("lines",[]):
        if 20<l["bbox"][1]<270:
            sz[l["spans"][0]["size"]]+=1; ys.append(l["bbox"][1])
ys=sorted(set(ys)); g=[round(ys[i+1]-ys[i],1) for i in range(len(ys)-1)]
print("字号:", sz.most_common(2), "行距:", Counter([x for x in g if x>8]).most_common(2))
EOF

# 2) 版心与边距（应为 148 / 28 / 35 / 32 / 30）
pdftoppm -f 22 -l 22 -r 300 -png 教材/从零开始的核物理与核能.pdf /tmp/v
$P - <<'EOF'
import numpy as np; from PIL import Image; import glob
a=np.array(Image.open(glob.glob("/tmp/v*.png")[0]).convert("L")); d=a<128
px=300/25.4; H,W=a.shape
band=d[int(22*px):int(272*px),:]; cols=np.where(band.sum(0)>3)[0]
print("左 %.1f 右 %.1f 宽 %.1f"%(cols.min()/px,(W-cols.max())/px,(cols.max()-cols.min())/px))
EOF

# 3) 溢出（应为 0 页）
$P - <<'EOF'
import pymupdf as fitz
d=fitz.open("教材/从零开始的核物理与核能.pdf"); bad=[]
for i,p in enumerate(d):
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            if l["bbox"][2] > p.rect.width-25: bad.append(i+1); break
print("溢出页:", len(set(bad)))
EOF
```

**三条硬闸**：
- 正文字号 = 10.5 pt ± 0.05（若仍是 9.34，说明还有元素在撑宽页面）
- 每行 40 字 ± 1，每页 39 行
- 溢出页 = 0

---

## 7 如果只能改三处

### 第一处：修掉全书 0.889 的缩放（§1）

一个 CSS 属性（`.katex-display{max-width:100%; overflow-x:auto}`），
让 259 页的字号从 9.34 → 10.5、行距 16.01 → 17、图注 8 → 9、表格 7.64 → 9。

**为什么排第一**：全书每个字都偏离设计值，不是某处不好看的问题。不修这一条，后面所有数值调整都在错的基础上叠加：h2 从 13 调到 14，实际渲染还是 12.4。这也是唯一一处"改一行、全书受益"的改动。

### 第二处：把行距/段距的层级扳正（17 pt + 段距 0 + 缩进 2 字）

行距 1.72 → 1.62（17 pt），段距 1.9 pt → 0，缩进保持 2 字。

**为什么排第二**：读者面对的是"一页文字"，这一页的节奏由行距与段距决定。现状是"行间松、段间死"：眼睛在行间被推开，在段间被粘住，读两小时就变成"读不动"。这条改完，同样的内容会显得少 10%，因为段落终于有界线。

### 第三处：练习解答一步一行 + 表格 ①②③ 一条一行（结构 + CSS）

**为什么排第三**：前两条决定"读得下去吗"，这一条决定"学得会吗"。这本书的读者是自学，卡住时唯一的求助对象是书里的步骤。6 步挤成一段，读者只能整段重读；一步一行，他能指着第 3 步说"这里不懂"。这是"教材"与"读物"的分界。

**为什么不是标题层级**：标题层级（第三硬伤）影响"翻书的感受"，但它不阻断理解；而且 h1/h2/h3 的改动可以在第二处的 CSS 里顺手完成，不占单独的"三处"名额。

---

## 8 执行顺序（给动手的人）

1. §2.1 换 `@media print` 整块 → `./build.sh` → 验收字号 10.5（**这一步不通，后面全部回滚**）
2. §3.1 改 `pdf_finish.py` 三个数 → 重建
3. §3.3 写 colgroup 注入器 → 重建 → 检查表格
4. §4.1 / §4.2 改源文件（练习、表格单元格）→ 重建
5. §3.2 改 `bookstyle.py` → 重出 70 幅图 → 重建
6. §2.2 改屏幕样式（不动印刷）
7. 跑 §6 三条硬闸 + §3.3 的填充率检查，处理 p11/p28/p83/p147/p198/p210 的空白页
8. 最后跑 §5⑦ 的 grep 自查，文风问题单独一轮

**每一步都要重建后再看 PDF，不要攒到最后。** 排版是联动的：字号改 11%，页数、目录页码、书眉、断页全部跟着变。
