# 全书装配、整本缩放诊断、索引页码

本册只记「一本书从 17 章 md 装成 PDF」的工程细节与两个隐性故障。版式参数见 SKILL.md 第一节，骨架／文风见 `spec-v3.md`。

## 一、装配管线（build_book.sh）

```
封面 HTML 块（.cover，223mm + break-after:page）
  → 卷首 part0_v8.md（跳开首行 pagebreak，否则第 1 页空白）
  → ch01_v8 … ch17_v8（每章备料：摘题干、解 {{ref:}}、图 .png→.svg）
  → # 题解（升为一章，shape.py 认 BRICK 表里的「题解」）
     + tijie_ch01 … tijie_ch17（各自以 ## 第 N 章 开头）
  → 附录 A–E
  → pandoc --template --katex → shape.py → Chromium --print-to-pdf → finish.py
```

- **题干回填**：v8 章末只有「见书末《题解》第 N 章」一句，题干要在装配时从**原稿** `src/chNN.md` 的 `^\*\*题\s*(\d+)\*\*` 摘回，套 `.qstem`。
- **图平铺**：`图v3/chNN/*.svg` 逐个 `ln -sfn` 到 `out/图/`，正文 `.png` 统一改 `.svg`；不改正文文件名。
- **封面**：`finish.py` 加 `if p == 0: continue`，封面不排页眉页码；`finish.py` 靠 `chap_pages` 跳章首页，封面不在其中，必须单独跳。
- **题解章**：`# 题解` 由 `shape.py` 的 `SUBS`/`BRICK` 上色砖（SOLUTIONS／解／书末），与各章同构；题解首页也受「章首页不排页眉」约束。
- 子集调试：`CHAPTERS="01 02" OUTNAME=测X ./build_book.sh`；附录总会带上，正好用来验附录排版。

## 二、整本书被缩到 84%（最隐蔽的排版故障）

Chrome 打印默认「适合可打印宽度」。文档里只要有一处元素宽过可打印区（本书 180 mm），整本会等比缩小：正文 10.5 pt 印成 8.84 pt，行距 17 pt 变成 14.5 pt。单页上看不出，容易被当成字体没设对。

宽出来的来源有三个，逐条堵：

| 来源 | 机理 | 堵法 |
|---|---|---|
| `main{padding-left:34mm}` | 打印时算成额外宽度 | `main > *{margin-left:34mm}`，排在 `p{margin:0}` 之后 |
| `body{width:210mm; padding:22mm 15mm}` 仍未退出 | 210+30=240 mm | 打印块：`html,body{width:auto;margin:0;padding:0}`，页边距全交 `@page` |
| pandoc `<table style="width:100%">` | 100% 按 180 mm 算，再叠 34 mm 左边距 = 214 mm | `table:not(.wide){width:146mm !important}`；`shape.py` 的 `ensure_wide()` 在定宽后 colgroup 合计 ≥176 mm 时补 `class="wide"`；`table.wide{width:180mm;margin-left:0 !important}` 不分层级 |

## 三、诊断：别信「字号中位数」

`measure_pdf.py` 的中位数按全页字符算，表格字（8.8 pt）、图注（8.5 pt）、题解字都会把中位数拉下来。一本书表格多时，正文 10.48 pt 也能报成 8.8。判据换成**按页的字号直方图**：

```python
import pymupdf, collections
d = pymupdf.open(pdf); c = collections.Counter()
for i in range(3, len(d) - 10):            # 跳过封面与末尾附录
    for b in d[i].get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    c[round(s["size"], 2)] += len(s["text"])
print(c.most_common(3))                     # 正文号必须是第一名
```

定位「谁把版面撑宽」——把打印规则临时套成屏幕 CSS，再用 headless Chrome 的 JS 量：

```html
<style>html,body{margin:0;padding:0;width:180mm}main{width:180mm;margin:0;padding:0}
body{font-size:10.5pt;line-height:17pt}main > *{margin-left:34mm}
main,figure,table,blockquote,.katex-display,img{max-width:100%}</style>
<script>window.addEventListener("load",()=>{let a=[];
 document.querySelectorAll("main *").forEach(e=>{if(e.closest("svg")||e.closest("math"))return;
  const r=e.getBoundingClientRect(); if(r.right>760)a.push(e.tagName+"."+e.className+" "+Math.round(r.right));});
 document.title="SW="+document.body.scrollWidth+" "+a.slice(0,6).join(" ; ");});</script>
```

跑法：`chrome --headless=new --dump-dom --virtual-time-budget=20000 file://…probe.html | grep -o "<title>[^<]*"`。

两处必须跳过，否则结果全是假阳性：`closest("svg")`（KaTeX 伸缩符号的 `width="400em"` 路径，量出来 5000+ px）与 `closest("math")`（MathML 内部盒）。`document.body.scrollWidth` 是最快的总判据：等于 214 mm 就是「180 mm 元素 + 34 mm 边距」，等于 240 mm 就是 body 宽度问题。

## 四、索引页码两遍校准

`make_appendix.py` 先出「术语｜英文｜章」（拼音序）。全书 PDF 出来后：

1. `marker-pdf-env/bin/python 工具/index_pages.py src/appendix_D.md out/全书.pdf` —— 逐条在其**所属章**内找首次出现，写回「页」列；
2. 重装全书（页码列会改变索引篇幅，会影响自身页码）；
3. 再跑一次同一脚本，与上一版 diff；两遍一致才算定稿。

三处必须按此实现，否则页码会指错页：

- **章首页从 PDF 书签取，不从正文搜**：章首页的章号是加了字距的（提取出来是「第 1 6 章」），正文搜索取不到，会把术语锚到卷首符号表的偶一提及上。用 `doc.get_toc()` 的 level-1 标题（`第 N 章　…`）建「章 → 起始页」表。
- **搜索范围截到附录 A 之前**：否则术语会命中附录 C 公式速查里的同一符号，页码跳到索引前面去。
- **标目去干净 `$`**：`$Q$ 值` 这类行内公式标目，要把 `$` 全去掉并同时试「去空格版」匹配，否则永远找不到、落成「—」。

未找到页码的条目会写「—」，逐条处理：术语写法与正文不一致（如正文用 ²³⁸U、表里用 LaTeX 符号）就改标目，真没出现过的就从表里删。

## 五、附录 A–E 生成

- A 常数与换算：CODATA 版本必须写进表头与章末；B 核素表：半衰期/衰变方式解析 NUBASE2020，截面按 ENDF/B-VIII.0 在 0.0253 eV 插值，核不到的列「待核」而不是凭记忆填；C 公式速查：从各章 `$$` 块**逐字搬运**，不重排不改符号；D/E 由脚本汇总。
- 索引排序：不装 pypinyin，用 `LC_ALL=zh_CN.UTF-8 sort`（glibc collation 就是拼音序）。同一术语只留一条，章号合并。
