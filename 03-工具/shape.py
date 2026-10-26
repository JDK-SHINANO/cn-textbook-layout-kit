#!/usr/bin/env python3
"""shape.py —— 把 pandoc 的朴素 HTML 塑成教材的骨相。

改三处：
  ① h1「第 4 章　射线与物质」→ 章首页（左侧色砖 + 章号 + 章名）
  ② h2「4.1 带电粒子…」→ 节号色牌 + 节名；无编号的 h2（动手算一算/本章要点/本章术语）→ 通栏色条
  ③ figcaption「图 4-1　…」→ 图号着色

用法： python3 工具/shape.py out/sample.html
"""
import re
import sys

CH = re.compile(r"^第\s*(\d+)\s*章[\s\u3000]*(.*)$")
SEC = re.compile(r"^(\d+\.\d+)[\s\u3000]+(.*)$")
FIGNO = re.compile(r"^(图\s*\d+[-–]\d+)[\s\u3000]*(.*)$", re.S)

COLHEADS = {"动手算一算", "本章要点", "本章术语", "本章数值出处"}


SUBS = {"题解": "全书习题的逐步详解"}
BRICK = {"题解": ("SOLUTIONS", "解", "书末")}


def shape_h1(m):
    ident, text = m.group(1), m.group(2).strip()
    g = CH.match(text)
    if not g:
        # 书末《题解》升为一章：章首与各章同款色砖
        if text in BRICK:
            kicker, big, above = BRICK[text]
            sub = SUBS.get(text, "")
            return (
                f'<h1 class="chapo" id="{ident}">'
                f'<span class="brick"><span class="bk">{kicker}</span>'
                f'<span class="bn">{big}</span></span>'
                f'<span class="cht"><span class="cn">{above}</span>'
                f'<span class="ct">{text}</span>'
                f'<span class="sub2">{sub}</span></span>'
                f"</h1>"
            )
        return f'<h1 class="plain" id="{ident}">{text}</h1>'
    num, title = g.group(1), g.group(2).strip()
    return (
        f'<h1 class="chapo" id="{ident}">'
        f'<span class="brick"><span class="bk">CHAPTER</span>'
        f'<span class="bn">{num}</span></span>'
        f'<span class="cht"><span class="cn">第 {num} 章</span>'
        f'<span class="ct">{title}</span></span>'
        f"</h1>"
    )


def shape_h2(m):
    ident, text = m.group(1), m.group(2).strip()
    g = SEC.match(text)
    if g:
        return (f'<h2 id="{ident}"><span class="secno">{g.group(1)}</span>'
                f'<span class="sectitle">{g.group(2)}</span></h2>')
    if text in COLHEADS or text.startswith("本章"):
        return f'<h2 class="colhead" id="{ident}">{text}</h2>'
    if CH.match(text):
        return f'<h2 class="chs" id="{ident}">{text}</h2>'
    return m.group(0)


def shape_fig(m):
    inner = m.group(1)
    g = FIGNO.match(inner)
    if not g:
        return m.group(0)
    return f'<figcaption><span class="figno">{g.group(1)}</span>\u3000{g.group(2)}</figcaption>'


LEAD_TITLE = "本章要解决的问题"
NOTE_HEAD = re.compile(r"^<p><strong>(旁注[^<]*)</strong>")


def _blocks(src):
    """逐个返回 <blockquote>…</blockquote> 的 (起, 止) 位置，不跨块、不贪婪。"""
    i = 0
    while True:
        a = src.find("<blockquote>", i)
        if a < 0:
            return
        b = src.find("</blockquote>", a)
        if b < 0:
            return
        b += len("</blockquote>")
        yield a, b
        i = b


def shape_quotes(src):
    """把两类引文就地改写：章首问题清单 → blockquote.lead；旁注 → aside.note。

    早年用一条正则 `<blockquote>\s*<p><strong>…(.*?)</p>\s*</blockquote>`，
    一旦引文里还套着 <ol>（问题清单换了写法就会这样），惰性匹配会一路吞到
    下一个 `</p></blockquote>`，把后面几段连同旁注、表格全吃进去——
    表现为旁注浮成 30mm 宽、表格挤成一字一列。故改为逐块截取，块内再处理。
    """
    out, last, nlead, nnote = [], 0, 0, 0
    for a, b in _blocks(src):
        blk = src[a:b]
        inner = blk[len("<blockquote>"):-len("</blockquote>")]
        if LEAD_TITLE in inner:
            body = re.sub(rf"<p><strong>{LEAD_TITLE}</strong></p>", "", inner)
            body = re.sub(rf"<p><strong>{LEAD_TITLE}</strong>(.*?)</p>",
                          r"\1", body, flags=re.S)
            if "<ol" not in body:                      # 旧式：编号挤在同一个段落里
                body = re.sub(r"\s+", " ", body).strip()
                items = []
                for s in re.split(r"(?<=[？?])\s*(?=\d+\.)", body):
                    s = re.sub(r"^\d+\.\s*", "", s.strip())
                    if s:
                        items.append(f"<li>{s}</li>")
                body = "<ol>" + "".join(items) + "</ol>" if items else body
            blk = (f'<blockquote class="lead"><p class="leadhead">{LEAD_TITLE}</p>'
                   f"{body}</blockquote>")
            nlead += 1
        else:
            m = NOTE_HEAD.match(inner.lstrip())
            if m:
                tag = re.sub(r"[（(].*?[)）]", "", m.group(1)).strip() or "旁注"
                body = inner.lstrip()[m.end():]
                body = re.sub(r"^[\s\u3000]+", "", body)
                blk = (f'<aside class="note"><span class="ntag">{tag}·可跳过</span>'
                       f"{body.rstrip()}</aside>")
                nnote += 1
        out.append(src[last:a]); out.append(blk); last = b
    out.append(src[last:])
    return "".join(out), nlead, nnote


PUNCT = "，。；：、？！）》」』·"
STYLE = re.compile(r"<style.*?</style>", re.S)
CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffefA-Za-z0-9\)\]%‰℃]")
WRAP = '<span class="nw">'


def kinsoku(src: str) -> tuple[str, int]:
    """行首禁则：把「前一字 + 标点」包进 white-space:nowrap 的小片段。

    Chromium 打印不实现 line-break:strict，插 U+2060 反而在它之前断行（实测行首标点
    从 70 余处不减反增），唯一可靠的是让这对字成为一个不可断的行内盒。
    只在正文文字里动手：跳过 <style>，遇到标签内字符不处理。
    """
    n = 0

    def fix(chunk: str) -> str:
        nonlocal n
        out, in_tag, buf = [], False, ""
        for ch in chunk:
            if ch == "<":
                in_tag = True
            if in_tag:
                out.append(ch)
                if ch == ">":
                    in_tag = False
                    buf = ""
                continue
            if ch in PUNCT and len(buf) == 1 and CJK.match(buf):
                # 把上一字从 out 里取出，与标点一起包住
                if out and out[-1] == buf:
                    out.pop()
                out.append(f"{WRAP}{buf}{ch}</span>")
                n += 1
                buf = ""
                continue
            out.append(ch)
            buf = ch
        return "".join(out)

    parts, last = [], 0
    for m in STYLE.finditer(src):
        parts.append(fix(src[last:m.start()]))
        parts.append(m.group(0))
        last = m.end()
    parts.append(fix(src[last:]))
    return "".join(parts), n


FIGDIR = "out/图"
NUMCELL = re.compile(r"^[+\-−±]?[\d\s.,×x*·%‰/⁻⁰¹²³⁴⁵⁶⁷⁸⁹\^·]+(\s*[a-zA-Zμ°/²³%‰]+)?$")


def svg_width_mm(name: str) -> float:
    """读 SVG 的 width（pt）换算成 mm；读不到就当作窄图。"""
    import os
    path = os.path.join(FIGDIR, os.path.basename(name))
    try:
        head = open(path, encoding="utf-8").read(600)
    except OSError:
        return 0.0
    m = re.search(r'width="([\d.]+)pt"', head)
    return float(m.group(1)) / 72 * 25.4 if m else 0.0


LATEX_CMD = re.compile(r"\\[a-zA-Z]+")
LATEX_STRUCT = re.compile(r"[\^_{}$\\]")


def _visible(t: str) -> str:
    """把 LaTeX 源码折成「印出来能看见的字」。
    不这么做，`^{56}\\mathrm{Fe}(n,n')^{56}\\mathrm{Fe}^*` 会被当成三十多个字符，
    列宽虚胖一倍，表格白白开进副区。"""
    t = re.sub(r"<[^>]+>", "", t)
    t = LATEX_CMD.sub("", t)
    return LATEX_STRUCT.sub("", t)


def _text_mm(t: str, fs_pt: float = 9.5) -> float:
    """粗估一行文字印出来的宽度（mm）。中文满字宽，西文按比例收窄。"""
    em = fs_pt * 0.3528                      # 1 pt = 0.3528 mm
    w = 0.0
    for ch in _visible(t):
        if ord(ch) > 0x2E80:                 # 汉字、全角标点
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


def fit_say_columns(src: str):
    """每题按「最长那条注释」定解析列宽：它右顶版心、左端即其余注释的对齐线；
    余下宽度留给公式，公式在其中居中。"""
    n = 0

    marks = [m.start() for m in re.finditer(r'<div class="work">', src)]
    for idx in range(len(marks) - 1, -1, -1):        # 从后往前改，偏移不乱
        a = marks[idx]
        b = marks[idx + 1] if idx + 1 < len(marks) else len(src)
        blk = src[a:b]
        says = re.findall(r'<span class="say">(.*?)</span>', blk, re.S)
        if not says or '<div class="steps">' not in blk:
            continue
        w = min(96.0, max(24.0, max(_text_mm(s) for s in says) + 0.5))
        new = blk.replace('<div class="steps">',
                          f'<div class="steps" style="--sayw:{w:.1f}mm">', 1)
        src = src[:a] + new + src[b:]
        n += 1
    return src, n


H3 = re.compile(r'<h3 id="[^"]*">(.*?)</h3>', re.S)
H2NO = re.compile(r'<span class="secno">(\d+\.\d+)</span>')


def number_h3(src: str):
    """三级标题编号：随所在节走，写成 5.1.1、5.1.2 ……
    无编号的节（本章要点、题解小节）下不编号。"""
    sec, n, out, total = None, 0, [], 0
    pos = 0
    for m in re.finditer(r'<h2[^>]*>.*?</h2>|<h3 id="[^"]*">.*?</h3>', src, re.S):
        out.append(src[pos:m.start()])
        blk = m.group(0)
        if blk.startswith("<h2"):
            g = H2NO.search(blk)
            sec, n = (g.group(1) if g else None), 0
            out.append(blk)
        elif sec:
            n += 1
            total += 1
            inner = H3.match(blk).group(1)
            out.append(f'<h3 id="{blk.split(chr(34))[1]}">'
                       f'<span class="h3no">{sec}.{n}</span>{inner}</h3>')
        else:
            out.append(blk)
        pos = m.end()
    out.append(src[pos:])
    return "".join(out), total


CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"
TABLE_CSS_PT = 8.8            # 表格字号
COL_PAD_MM = 2.6              # 每列左右内边距合计
MAIN_MM, WIDE_MM = 146.0, 180.0


def _split_circled(cell_html: str) -> str:
    """一格里的 ①②③… 先各自起行——不定出断点，量出来的宽度没有意义。"""
    out, first = [], True
    for i, ch in enumerate(cell_html):
        if ch in CIRCLED and not first:
            out.append("<br />")
        out.append(ch)
        if ch.strip():
            first = False
    return "".join(out)


def _line_mm(html: str, fs_pt: float = TABLE_CSS_PT) -> float:
    """一格内最长一行（按 <br> 分）的估算宽度，mm。"""
    em = fs_pt * 0.3528
    best = 0.0
    for line in re.split(r"<br\s*/?>", html):
        txt = re.sub(r"<[^>]+>", "", line)
        w = _text_mm(txt, fs_pt)
        best = max(best, w)
    return best


BREAK_AT = ("；", "，", "、")     # 开了副区仍不够时，才允许在这些地方断行


def _cell_lines(html: str):
    return re.split(r"<br\s*/?>", html)


def _cell_w(html: str) -> float:
    return max(_text_mm(ln, TABLE_CSS_PT) for ln in _cell_lines(html)) + COL_PAD_MM


def _break_cell(html: str):
    """把一个纯文字格里最长的那行，在靠后的「；」「，」处断开；断不了返回 None。"""
    if "<" in html:                    # 带标签（行内公式等）不硬断，怕拆坏
        return None
    lines = _cell_lines(html)
    order = sorted(range(len(lines)), key=lambda k: -_text_mm(lines[k], TABLE_CSS_PT))
    for li in order:
        ln = lines[li]
        for mark in BREAK_AT:
            cut = ln.rfind(mark)
            if cut > 0 and cut < len(ln) - 1:
                lines[li] = ln[:cut + 1] + "<br />" + ln[cut + 1:]
                return "<br />".join(lines).replace("<br /><br />", "<br />")
    return None


def fit_tables(src: str):
    """列宽判定（按汝的规矩）：

    1. 格内 ①②③… 先各自起行；
    2. 每列取「最长那条不折行」的宽——**首列必须一行，绝不压它**；
    3. 余量均分到各列；
    4. 主栏（146mm）放不下 → 开副区（180mm）；
    5. 开了副区仍放不下 → 才在非首列的「；」「，」「、」处断行，断完回到第 2 步重算，
       直到放得下或再无点可断。
    """
    n = 0

    def one(m):
        nonlocal n
        blk = m.group(0)
        blk = re.sub(r"<td[^>]*>(.*?)</td>",
                     lambda c: "<td>" + _split_circled(c.group(1)) + "</td>",
                     blk, flags=re.S)

        def cells_of(h):
            return [re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, flags=re.S)
                    for r in re.findall(r"<tr>(.*?)</tr>", h, flags=re.S)]

        grid = cells_of(blk)
        if not grid:
            return blk
        ncol = max(len(r) for r in grid)

        def col_need(g):
            out = []
            for ci in range(ncol):
                out.append(max((_cell_w(r[ci]) for r in g if ci < len(r)), default=0.0))
            return out

        room, cls = MAIN_MM, ""
        for _ in range(40):
            need_cols = col_need(grid)
            need = sum(need_cols)
            if need <= MAIN_MM:
                room, cls = MAIN_MM, ""
                break
            room, cls = WIDE_MM, "wide"
            if need <= WIDE_MM:
                break
            # 开副区仍不够：挑最宽的非首列，断它最长的一格
            widest = max(range(1, ncol), key=lambda c: need_cols[c])
            done = False
            # 只断「这一列里最长的那一格」——断短格减不了列宽，白折一行
            cand = [r for r in grid if widest < len(r)]
            cand.sort(key=lambda r: -_cell_w(r[widest]))
            for r in cand:
                old = r[widest]
                nb = _break_cell(old)
                if nb is not None and old in blk:
                    blk = blk.replace(old, nb, 1)   # 只换这一格，<th> 不受牵连
                    done = True
                    break
            if not done:
                break
            grid = cells_of(blk)

        need_cols = col_need(grid)
        need = sum(need_cols)
        share = (room - need) / ncol
        if share >= 0:
            widths = [c + share for c in need_cols]
        else:                                  # 首列不压，其余等分收
            rest = need - need_cols[0]
            k = max(0.0, (room - need_cols[0])) / rest if rest > 0 else 1.0
            widths = [need_cols[0]] + [c * k for c in need_cols[1:]]
        colgroup = "<colgroup>" + "".join(
            f'<col style="width:{w:.1f}mm" />' for w in widths
        ) + "</colgroup>\n"
        blk = re.sub(r"<colgroup>.*?</colgroup>\s*", "", blk, flags=re.S)
        blk = blk.replace("<table", f'<table class="{cls}"' if cls else "<table", 1)
        blk = blk.replace("<thead>", colgroup + "<thead>", 1)
        n += 1
        return blk

    src = re.sub(r"<table[^>]*>.*?</table>", one, src, flags=re.S)
    return src, n


def mark_points(src: str):
    """「本章要点」那种 ul 不打圆点：改成段落式（首行缩进两字、项间留 2pt）。
    点号在这里多余——每项本身就是一句完整的话。"""
    def one(m):
        blk = m.group(0)
        return blk.replace("<ul>", '<ul class="points">', 1)

    src, n = re.subn(r'(<h2 class="colhead"[^>]*>本章要点</h2>\s*)<ul>.*?</ul>', one, src, flags=re.S)
    return src, n


def mark_wide(src: str):
    """图：只有比主栏（146mm）还宽的才伸进副区；表：五列以上才破栏。
    其余一律留在主栏——这是样书的规矩，不是「能宽就宽」。"""
    n_fig = n_tab = n_num = 0

    def fig(m):
        nonlocal n_fig
        blk = m.group(0)
        src_ = re.search(r'<img[^>]+src="([^"]+)"', blk)
        if src_ and svg_width_mm(src_.group(1)) > 152:
            n_fig += 1
            return blk.replace("<figure>", '<figure class="wide">', 1)
        return blk

    src = re.sub(r"<figure>.*?</figure>", fig, src, flags=re.S)

    def tab(m):
        nonlocal n_tab
        blk = m.group(0)
        head = blk.split("</thead>")[0] if "</thead>" in blk else blk
        if len(re.findall(r"<th[ >]", head)) >= 5:
            n_tab += 1
            return blk.replace("<table>", '<table class="wide">', 1)
        return blk

    # 列宽：先按圈号断点，再逐列取「最长那条不折行」的宽度，余量均分；
    # 主栏（146mm）放不下就开副区（180mm），仍不够则按比例收。
    n_tab2 = 0
    src, n_tab2 = fit_tables(src)

    def cell(m):
        nonlocal n_num
        txt = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        if txt and NUMCELL.match(txt) and re.search(r"\d", txt):
            n_num += 1
            return f'<td class="num">{m.group(1)}</td>'
        return m.group(0)

    src = re.sub(r"<td>(.*?)</td>", cell, src, flags=re.S)
    return src, n_fig, n_num, n_tab2


def main(path):
    src = open(path, encoding="utf-8").read()
    n1 = n2 = n3 = 0

    def h1(m):
        nonlocal n1
        out = shape_h1(m)
        n1 += out != m.group(0)
        return out

    def h2(m):
        nonlocal n2
        out = shape_h2(m)
        n2 += out != m.group(0)
        return out

    def fc(m):
        nonlocal n3
        out = shape_fig(m)
        n3 += out != m.group(0)
        return out

    # 只处理 <h1 id=...>纯文本</h1>（不含标签的）
    src = re.sub(r'<h1 id="([^"]+)">([^<]+)</h1>', h1, src)
    src = re.sub(r'<h2 id="([^"]+)">([^<]+)</h2>', h2, src)
    src = re.sub(r"<figcaption[^>]*>(.*?)</figcaption>", fc, src, flags=re.S)
    src, nlead, nnote = shape_quotes(src)
    src, npts = mark_points(src)
    src, nh3 = number_h3(src)
    src, nsay = fit_say_columns(src)
    src, nwide, nnum, n_tab2 = mark_wide(src)
    # Chromium 打印不实现行首禁则（line-break:strict 无效）。做法：在全角标点前插入
    # U+2060（WORD JOINER），令「m，」「字。」这类粘连不可断，标点就不会被甩到行首。
    # 行首禁则：Chrome 允许在行内盒边界断行，插 U+2060 与包 nowrap 片段两种办法都试过，
    # 行首标点仍为 71 行（与不处理时相同）——留作已知缺陷，不假装解决。
    njoiner = 0

    open(path, "w", encoding="utf-8").write(src)
    print(f"shape: 章首页 {n1}，节题 {n2}，图题 {n3}，问题清单 {nlead}，"
          f"边注 {nnote}，要点式 {npts}，三级号 {nh3}，解列 {nsay}，破栏图 {nwide}，定宽表 {n_tab2}，数值格 {nnum}，禁则 {njoiner}")


if __name__ == "__main__":
    main(sys.argv[1])
