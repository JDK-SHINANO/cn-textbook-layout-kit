#!/usr/bin/env python3
"""index_pages.py —— 给附录 D 的术语索引补上真实页码（GB/T 22466：标目 + 页码）。

用法（要用带 PyMuPDF 的解释器）：
  ${PYMUPDF:-python3} 工具/index_pages.py \
      ../src/appendix_D.md ../版式对照_有机化学风/out/全书_v3.pdf

做法：逐条在正文页里找首次出现（跳过附录 D 自身），写回「页」列。
两遍校准：页码列写入会改变索引篇幅，故跑完重装一次再跑本脚本，页码不变才算稳定。
"""
import re
import sys

import pymupdf


def cell_of(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def main(md_path, pdf_path):
    doc = pymupdf.open(pdf_path)
    texts = [p.get_text() for p in doc]
    flat_first = [re.sub(r"\s+", "", t) for t in texts[:12]]
    # 目录页算第 1 页：封面、空白页、版权页不计数
    toc_first = next((i for i, f in enumerate(flat_first) if f.startswith("目录")), 0)

    # 附录起止：用 PDF 书签定位，别在正文里搜文字——目录页也印着「附录 D 术语总索引」
    apx_a, d_start = len(texts), len(texts)
    for lvl, title, pg in doc.get_toc():
        if lvl != 1:
            continue
        t = title.replace(" ", "")
        if t.startswith("附录A"):
            apx_a = min(apx_a, pg - 1)
        if t.startswith("附录D"):
            d_start = min(d_start, pg - 1)
    body = texts[:min(apx_a, d_start)]
    # 章首页与附录 A 的页：直接用 PDF 书签（finish.py 写入，标题是「第 N 章　…」），
    # 比在正文里搜「第 N 章」可靠——章首页的字是加了字距的（「第 1 6 章」）。
    chap_start, apx_a = {}, len(texts)
    for lvl, title, pg in doc.get_toc():
        if lvl != 1:
            continue
        t = title.replace(" ", "")
        m = re.match(r"第(\d+)章", t)
        if m and int(m.group(1)) not in chap_start:
            chap_start[int(m.group(1))] = pg - 1
        if t.startswith("附录A"):
            apx_a = min(apx_a, pg - 1)
    body = texts[:apx_a]
    body_end = len(body)
    starts = sorted(chap_start.values())

    lines = open(md_path, encoding="utf-8").read().split("\n")
    out, n, missing = [], 0, 0
    for ln in lines:
        if not ln.startswith("|"):
            out.append(ln)
            continue
        cells = cell_of(ln)
        if not cells or cells[0] in ("术语",) or set("".join(cells)) <= set("-: "):
            # 表头与分隔行：只保留一次表头，分隔行由本脚本统一重写
            if cells and cells[0] == "术语":
                out.append("| 术语 | 英文 | 章 | 页 |")
                out.append("|---|---|---|---|")
            continue
        term, en, chs = cells[0], cells[1], cells[2]
        needle = term.replace("$", "").strip()
        page = "—"
        flat = needle.replace(" ", "")
        try:
            first_ch = int(chs.split(",")[0])
        except ValueError:
            first_ch = 0
        lo = chap_start.get(first_ch, 0)
        hi = min([s for s in starts if s > lo], default=len(body))
        page = "—"
        for rng in (range(lo, hi), range(0, len(body))):
            for i in rng:
                t = body[i]
                ft = t.replace(" ", "").replace("\n", "")
                if (needle and needle in t) or (flat and flat in ft):
                    page = str(i + 1 - toc_first)
                    break
            if page != "—":
                break
        if page == "—":
            missing += 1
        n += 1
        out.append(f"| {term} | {en} | {chs} | {page} |")

    open(md_path, "w", encoding="utf-8").write("\n".join(out))
    print(f"索引 {n} 行；未找到页码 {missing} 条；附录 D 起于第 {d_start + 1} 页")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
