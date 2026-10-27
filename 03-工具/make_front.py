#!/usr/bin/env python3
"""make_front.py —— 前置页：版权页 + 目录（照《基础有机化学》的目录骨相）。

目录结构（每章一块，块内双栏）：
  第 N 章 [蓝底白字方框]  章名 ————————————— / 页码
    1.1　大节 ………………………… 77        （宋体）
      1.1.1　小节 …………………… 77      （仿宋，缩进）

条目来自 src/toc_entries.json（工具/toc_pages.py 从 PDF 书签导出，含三级）。
首轮若没有该文件，退回「只列章、页码 —」。
"""
import glob
import json
import os
import re

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COPYRIGHT = """<div class="copyright">
  <p class="cp-title">从零开始的核物理与核能</p>
  <p class="cp-sub">从原子核的发现，到反应堆、聚变与粒子物理</p>
  <div class="cp-rule"></div>
  <p class="cp-line">全四卷 · 本册收入前三卷 17 章，附书末《题解》与附录 A–E</p>
  <p class="cp-line">第三版（v3）　2026 年 10 月</p>
  <p class="cp-line">开本 210 mm × 260 mm　正文 10.5 pt　双色印刷</p>
  <p class="cp-note">本书为编写者自印本，非正式出版物<br>数据来源见各章末「本章数值出处」与附录<br>排版 Hermes 排版流水线（HTML + Chromium）<br>插图由 matplotlib 脚本生成</p>
</div>
<div class="blankpage"></div>
"""


def chapter_titles():
    def h1(path):
        m = re.search(r"^# (.+)$", open(path, encoding="utf-8").read(), re.M)
        return re.sub(r"\s*\{#[^}]*\}\s*$", "", m.group(1)).strip() if m else None

    out = []
    p0 = os.path.join(BOOK, "src", "part0_v8.md")
    if os.path.exists(p0) and h1(p0):
        out.append(h1(p0))
    for f in sorted(glob.glob(os.path.join(BOOK, "src", "ch[0-9][0-9]_v8.md"))):
        t = h1(f)
        if t:
            out.append(t)
    if os.path.exists(os.path.join(BOOK, "src", "tijie_ch01.md")):
        out.append("题解")
    for L in "ABCDE":
        f = os.path.join(BOOK, "src", f"appendix_{L}.md")
        if os.path.exists(f) and h1(f):
            out.append(h1(f))
    return out


def row(title, page, lv):
    return (f'<p class="toc-sec lv{lv}"><span class="toc-t">{title}</span>'
            f'<span class="toc-dot"></span><span class="toc-p">{page}</span></p>')


def bar(title, page):
    """章条：章号在副区右对齐（右沿贴副区右沿），章名自主区左沿起，同一行。"""
    m = re.match(r"第\s*(\d+)\s*章[\s\u3000]*(.*)$", title)
    if m:
        box, name = f"第 {m.group(1)} 章", m.group(2).strip()
    else:
        m = re.match(r"(附录\s*[A-E])[\s\u3000]*(.*)$", title)
        if m:
            box, name = m.group(1), m.group(2).strip()
        else:
            box, name = "", title
    boxhtml = f'<span class="toc-box">{box}</span>' if box else ""
    return (f'<div class="toc-bar"><span class="toc-no">{boxhtml}</span>'
            f'<span class="toc-name">{name}</span><span class="toc-line"></span>'
            f'<span class="toc-pg">/ {page}</span></div>')


def main():
    ej = os.path.join(BOOK, "src", "toc_entries.json")
    entries = json.load(open(ej, encoding="utf-8")) if os.path.exists(ej) else []

    groups = []
    for e in entries:
        if e["lvl"] == 1:
            groups.append({"t": e["title"], "p": e["page"], "kids": []})
        elif groups:
            groups[-1]["kids"].append(e)

    if not groups:
        groups = [{"t": t, "p": "—", "kids": []} for t in chapter_titles()]

    out = ['<div class="tocpage">', '<p class="tochead">目　录</p>']
    for g in groups:
        out.append('<div class="toc-chap">')
        out.append(bar(g["t"], g["p"]))
        if g["kids"]:
            out.append('<div class="toc-cols">')
            for k in g["kids"]:
                out.append(row(k["title"], k["page"], k["lvl"]))
            out.append("</div>")
        out.append("</div>")
    out += ["</div>", ""]

    open(os.path.join(BOOK, "src", "front.md"), "w", encoding="utf-8").write(
        COPYRIGHT + "\n".join(out))
    nkids = sum(len(g["kids"]) for g in groups)
    print(f"前置页：目录 {len(groups)} 章块 + {nkids} 条节/小节")


if __name__ == "__main__":
    main()
