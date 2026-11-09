#!/usr/bin/env python3
"""finish.py —— 给样张 PDF 加「页码 + 页眉细线 + 书签」。

页眉依教材惯例镜像：
  偶数页（订口在右）：[页码] │ 第 4 章　射线与物质
  奇数页（订口在左）：4.1 带电粒子… │ [页码]
页码与文字一律排在切口侧（CY/T 200—2019 4.4.2：页码不应置于订口侧）。

用法： python3 finish.py out/sample.pdf out/sample.html
"""
import html
import os
import re
import sys

import fitz

MM = 72 / 25.4
PAGE_W, PAGE_H = 210, 260
M_TOP, M_OUT, M_IN = 22, 15, 15      # 天头 22（页眉占 15–18）/ 左右 15
ACCENT = (0.184, 0.435, 0.624)       # #2F6F9F
RULE = (0.776, 0.847, 0.902)         # 细线：主色 22% 左右
GREY = (0.28, 0.28, 0.30)

FONTS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/local/share/fonts/WindowsFonts/NotoSansSC-VF.ttf",
]


def pick_font():
    for p in FONTS:
        if os.path.exists(p):
            return p
    return None


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).replace("\u3000", " ").strip()


def headings(html_path):
    """从塑形后的 HTML 里取标题序列：(level, 页眉用文字)。"""
    src = open(html_path, encoding="utf-8").read()
    out = []
    last_ch = ""
    for m in re.finditer(r'<h1 class="(?:chapo|plain)".*?</h1>|<h2[^>]*>.*?</h2>|<h3[^>]*>.*?</h3>', src, re.S):
        blk = m.group(0)
        lvl = 1 if blk.startswith("<h1") else (2 if blk.startswith("<h2") else 3)
        txt = strip_tags(blk)
        txt = re.sub(r"\s+", " ", txt)
        # 章首页那团里含 CHAPTER 与重复章号，重构成「第 4 章　射线与物质」
        if lvl == 2:
            g = re.search(r"<span class=\"secno\">([^<]+)</span>", blk)
            if g:
                no = g.group(1).strip()
                rest = re.sub(r"^\s*" + re.escape(no), "", txt).strip()
                txt = f"{no}\u3000{rest}"
        elif lvl == 3:
            g = re.search(r"<span class=\"h3no\">([^<]+)</span>", blk)
            if g:
                no = g.group(1).strip()
                rest = re.sub(r"^\s*" + re.escape(no), "", txt).strip()
                txt = f"{no}\u3000{rest}"
        if "题解" in txt:
            txt = "题解"
        elif re.search(r"第\s*\d+\s*章", txt):
            g = re.search(r"第\s*(\d+)\s*章[\s\u3000]*(.*)$", txt)
            if g:
                txt = f"第 {g.group(1)} 章　{g.group(2).strip()}"
        if lvl == 1:
            last_ch = txt
        elif 'class="colhead"' in blk and last_ch:
            # 「本章要点」「动手算一算」这类栏目每章同名，书签里加章号前缀，避免 17 组重名
            txt = f"{last_ch.split('　')[0]}　{txt}"
        out.append((lvl, txt))
    return out


def locate(items, page_texts, skip=()):
    """按文字在页面上出现的位置给标题定页（单调向右搜索，避免重名误判）。

    page_texts 预先算好（每页一次 get_text），否则 164 条标题 × 372 页会把
    get_text 调六万次，实测 199 秒——预取后降到 2 秒级。
    skip 里是目录页：目录把每个标题都印了一遍，不跳过的话书签会全指到目录上。
    """
    marks = []
    cur = 0
    n = len(page_texts)
    for lvl, txt in items:
        key = re.sub(r"\s+", "", txt)[:14]
        found = None
        for p in range(cur, n):
            if p in skip:
                continue
            if key and key in page_texts[p]:
                found = p
                break
        if found is None:
            continue
        cur = found
        marks.append((found, lvl, txt))
    return marks


def main(pdf_path, html_path):
    doc = fitz.open(pdf_path)
    items = headings(html_path)
    raw = [doc[i].get_text() for i in range(doc.page_count)]
    page_texts = [re.sub(r"\s+", "", t) for t in raw]
    # 目录页：首页顶部就是「目　录」，其后各页会同时列出「附录」
    toc_pages = set()
    for i in range(min(12, doc.page_count)):
        if "目录" in page_texts[i][:24] or ("目录" in page_texts[i] and "附录" in raw[i]):
            toc_pages.add(i)
    marks = locate(items, page_texts, skip=toc_pages)

    chap_pages = {p for p, lvl, _ in marks if lvl == 1}
    # 封面、版权页、目录页都在第一章之前，不排页眉页码
    first_chap = min((pg - 1 for lvl, t, pg in doc.get_toc()
                      if lvl == 1 and re.match(r"第\s*\d+\s*章", t)), default=0)
    # 页码从目录页算第 1 页（封面、空白页、版权页不计数）
    toc_first = next((i for i in range(min(12, doc.page_count))
                      if page_texts[i].startswith("目录")), 0)
    chap_of, sec_of = {}, {}
    cur_ch, cur_sec = "", ""
    idx = {}
    for p, lvl, txt in marks:
        idx.setdefault(p, []).append((lvl, txt))
    for p in range(doc.page_count):
        for lvl, txt in idx.get(p, []):
            if lvl == 1:
                cur_ch, cur_sec = txt, ""
            else:
                cur_sec = txt
        chap_of[p], sec_of[p] = cur_ch, cur_sec

    fontfile = pick_font()
    fnt = fitz.Font(fontfile=fontfile) if fontfile else None

    for p in range(doc.page_count):
        page = doc[p]
        if not page.get_text().strip():
            continue
        if p in chap_pages:            # 章首页不排页眉
            continue
        if p < toc_first:              # 封面、空白页、版权页：不排页眉页码
            continue
        front = p < first_chap        # 目录页
        if front and "录" not in page.get_text():
            continue
        num = str(p - toc_first + 1)
        recto = (p % 2 == 0)           # 第 1 张为单页码（右页）
        # 页眉基线距纸顶 15mm、细线 17.6mm；版心自 22mm 起，中间留 4.4mm
        y_txt = 15.0 * MM
        y_rule = 17.6 * MM
        x_in = (M_IN if recto else M_OUT) * MM
        x_out = (PAGE_W - (M_OUT if recto else M_IN)) * MM

        # 细线（版心宽，0.5pt）
        page.draw_line(fitz.Point(x_in, y_rule), fitz.Point(x_out, y_rule),
                       color=RULE, width=0.5)

        label = "目录" if front else (sec_of[p] if recto else chap_of[p])
        if not label:
            label = chap_of[p] or ""

        fs = 8.5
        lw = fnt.text_length(label, fontsize=fs) if fnt else 0
        nw = fnt.text_length(num, fontsize=9) if fnt else 0
        gap = 2.6 * MM
        bar_h = 7.8

        if recto:   # 右页：版心 x 22→170mm，页码贴右切口
            x_num = x_out - nw
            x_bar = x_num - gap
            x_lab = x_bar - gap - lw
            page.draw_line(fitz.Point(x_bar + gap * .45, y_txt - bar_h),
                           fitz.Point(x_bar + gap * .45, y_txt + 1.6),
                           color=RULE, width=0.4)
            page.insert_text((x_num, y_txt), num, fontname="hdr", fontfile=fontfile,
                             fontsize=9, color=ACCENT)
            if label:
                page.insert_text((x_lab, y_txt), label, fontname="hdr",
                                 fontfile=fontfile, fontsize=fs, color=GREY)
        else:       # 左页：版心 x 15→163mm，页码贴左切口，文字朝订口
            x_num = x_in
            x_bar = x_num + nw + gap
            x_lab = x_bar + gap
            page.draw_line(fitz.Point(x_bar + gap * .55, y_txt - bar_h),
                           fitz.Point(x_bar + gap * .55, y_txt + 1.6),
                           color=RULE, width=0.4)
            page.insert_text((x_num, y_txt), num, fontname="hdr", fontfile=fontfile,
                             fontsize=9, color=ACCENT)
            if label:
                page.insert_text((x_lab, y_txt), label, fontname="hdr",
                                 fontfile=fontfile, fontsize=fs, color=GREY)

    # 书签
    toc = []
    for p, lvl, txt in marks:
        toc.append([lvl, txt, p + 1])
    if toc:
        doc.set_toc(toc)
    tmp = pdf_path + ".tmp"
    doc.save(tmp, garbage=1, deflate=True)
    doc.close()
    os.replace(tmp, pdf_path)
    print(f"finish: {fitz.open(pdf_path).page_count} 页，书签 {len(toc)} 条，页眉已排")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
