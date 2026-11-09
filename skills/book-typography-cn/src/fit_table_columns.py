#!/usr/bin/env python3
"""按内容定表格列宽，并把结果写成 <colgroup> 的 mm 值 + class="wide"。

用法：
    python3 fit_table_columns.py in.html [out.html] [--main 146] [--wide 180]

六步（这是定案，别退回「删掉 colgroup 交给浏览器」）：
  1. 格内 ①②③… 各自起行；
  2. 逐列取最长一条不折行的估算宽 + 内边距，**首列必须一行，永不被压**；
  3. 合计 ≤ 主栏 → 余量均分；
  4. 放不下 → 开副区（146 → 180）再均分，表挂 class="wide"；
  5. 仍不够 → 才在非首列的「；」「，」「、」处断行，只断该列最长那一格；
  6. 断完回第 2 步重算，直到放得下或无可再断；最后才等比压缩，首列保宽。

配合 CSS：table{table-layout:fixed}、table.wide{width:180mm;margin-left:0}。
只写 .wide 的让位不写宽度，宽表会被压回主栏宽、每列都折。
"""
from __future__ import annotations

import re
import sys

CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"
BREAK_AT = ("；", "，", "、")
TABLE_PT = 8.8          # 表格字号
PAD_MM = 2.6            # 每列左右内边距合计


def text_mm(t: str, fs_pt: float = TABLE_PT) -> float:
    """粗估一行宽（mm）：中文满字宽，西文按比例收。差 1–2mm 不影响观感。"""
    em = fs_pt * 0.3528
    w = 0.0
    for ch in t:
        if ord(ch) > 0x2E80:
            w += em
        elif ch in "il.,;:'|!()[]":
            w += em * 0.28
        elif ch.isdigit():
            w += em * 0.56
        elif ch.isupper():
            w += em * 0.68
        elif ch.isalpha():
            w += em * 0.52
        else:
            w += em * 0.40
    return w


def cell_lines(html: str) -> list[str]:
    return re.split(r"<br\s*/?>", html)


def cell_w(html: str) -> float:
    return max(text_mm(ln) for ln in cell_lines(html)) + PAD_MM


def split_circled(html: str) -> str:
    out, first = [], True
    for ch in re.sub(r"<[^>]+>", "", html):
        if ch in CIRCLED and not first:
            out.append("<br />")
        out.append(ch)
        if ch.strip():
            first = False
    return "".join(out) or html


def break_cell(html: str):
    """把纯文字格里最长那行在靠后的标点处断开；断不了返回 None。"""
    if "<" in html:                     # 带标签（行内公式等）不硬断
        return None
    lines = cell_lines(html)
    for li in sorted(range(len(lines)), key=lambda k: -text_mm(lines[k])):
        ln = lines[li]
        for mark in BREAK_AT:
            cut = ln.rfind(mark)
            if 0 < cut < len(ln) - 1:
                lines[li] = ln[: cut + 1] + "<br />" + ln[cut + 1:]
                return "<br />".join(lines)
    return None


def fit_table(blk: str, main_mm: float, wide_mm: float) -> str:
    blk = re.sub(r"<td[^>]*>(.*?)</td>",
                 lambda m: "<td>" + split_circled(m.group(1)) + "</td>",
                 blk, flags=re.S)

    def grid_of(h: str):
        return [re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, flags=re.S)
                for r in re.findall(r"<tr>(.*?)</tr>", h, flags=re.S)]

    grid = grid_of(blk)
    if not grid:
        return blk
    ncol = max(len(r) for r in grid)

    def needs(g):
        return [max((cell_w(r[c]) for r in g if c < len(r)), default=0.0)
                for c in range(ncol)]

    room, cls = main_mm, ""
    for _ in range(40):
        need_cols = needs(grid)
        total = sum(need_cols)
        if total <= main_mm:
            room, cls = main_mm, ""
            break
        room, cls = wide_mm, "wide"
        if total <= wide_mm:
            break
        widest = max(range(1, ncol), key=lambda c: need_cols[c])
        done = False
        for r in sorted([r for r in grid if widest < len(r)],
                        key=lambda r: -cell_w(r[widest])):
            old = r[widest]
            nb = break_cell(old)
            if nb and old in blk:
                blk = blk.replace(old, nb, 1)
                done = True
                break
        if not done:
            break
        grid = grid_of(blk)

    need_cols = needs(grid)
    total = sum(need_cols)
    share = (room - total) / ncol
    if share >= 0:
        widths = [c + share for c in need_cols]
    else:
        rest = total - need_cols[0]
        k = max(0.0, room - need_cols[0]) / rest if rest > 0 else 1.0
        widths = [need_cols[0]] + [c * k for c in need_cols[1:]]

    colgroup = "<colgroup>" + "".join(
        f'<col style="width:{w:.1f}mm" />' for w in widths) + "</colgroup>\n"
    blk = re.sub(r"<colgroup>.*?</colgroup>\s*", "", blk, flags=re.S)
    blk = blk.replace("<table", f'<table class="{cls}"' if cls else "<table", 1)
    blk = blk.replace("<thead>", colgroup + "<thead>", 1)
    return blk


def main(argv):
    src_path = argv[1]
    out_path = argv[2] if len(argv) > 2 and not argv[2].startswith("--") else src_path
    main_mm = 146.0
    wide_mm = 180.0
    for i, a in enumerate(argv):
        if a == "--main":
            main_mm = float(argv[i + 1])
        elif a == "--wide":
            wide_mm = float(argv[i + 1])

    html = open(src_path, encoding="utf-8").read()
    n = 0

    def one(m):
        nonlocal n
        n += 1
        return fit_table(m.group(0), main_mm, wide_mm)

    html = re.sub(r"<table[^>]*>.*?</table>", one, html, flags=re.S)
    open(out_path, "w", encoding="utf-8").write(html)
    print(f"fit_table_columns: {n} 张表，主栏 {main_mm:.0f} / 版心 {wide_mm:.0f} mm")


if __name__ == "__main__":
    main(sys.argv)
