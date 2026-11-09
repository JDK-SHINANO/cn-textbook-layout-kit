"""measure_pdf.py —— 量一本 PDF 的版式实况（不是看 CSS 声明）

用法：
    python3 measure_pdf.py 书.pdf [--pages 10]

输出：
    正文字号中位数(pt)、基线间距中位数(pt)、每行字数中位数、
    四边页边距(mm)、版心尺寸(mm)、页面尺寸

为什么必须量：CSS 里写 10.5pt，印出来可能是 9.34pt——
只要有一个元素宽过版心，Chrome 会把整页等比缩小，肉眼看不出。
"""
from __future__ import annotations

import statistics
import sys

try:
    import pymupdf as fitz
except ImportError:                      # 老版本
    import fitz

MM = 72 / 25.4


def analyse(path: str, sample: int = 12):
    doc = fitz.open(path)
    n = doc.page_count
    sizes, gaps, chars, margins = [], [], [], []

    step = max(1, n // sample)
    for pno in range(0, n, step):
        page = doc[pno]
        blocks = [b for b in page.get_text("dict")["blocks"] if b.get("lines")]
        if not blocks:
            continue

        # 字号：只取长度 > 8 的正文 span（排除标题/页码）
        for b in blocks:
            for line in b["lines"]:
                for s in line["spans"]:
                    if len(s["text"].strip()) > 8 and 6 < s["size"] < 16:
                        sizes.append(s["size"])

        # 基线间距
        ys = sorted({round(l["spans"][0]["origin"][1], 1)
                     for b in blocks for l in b["lines"] if l["spans"]})
        gaps += [round(b - a, 1) for a, b in zip(ys, ys[1:]) if 8 < b - a < 30]

        # 每行字数：取最长的几行
        widths = sorted((len("".join(s["text"] for s in l["spans"]).strip())
                         for b in blocks for l in b["lines"]), reverse=True)[:5]
        if widths and widths[0] > 20:
            chars.append(statistics.median(widths))

        # 页边距：只看"正文块"——排除书眉/页码（字号 < 9pt 或落在上下 8% 内）
        def is_body(b):
            sz = max((sp["size"] for l in b["lines"] for sp in l["spans"]), default=0)
            cy = (b["bbox"][1] + b["bbox"][3]) / 2
            return sz >= 9 and 0.06 * page.rect.height < cy < 0.94 * page.rect.height

        body = [b for b in blocks if is_body(b)]
        if not body:
            continue
        x0 = min(b["bbox"][0] for b in body)
        y0 = min(b["bbox"][1] for b in body)
        x1 = max(b["bbox"][2] for b in body)
        y1 = max(b["bbox"][3] for b in body)
        w, h = page.rect.width, page.rect.height
        margins.append((x0 / MM, y0 / MM, (w - x1) / MM, (h - y1) / MM))

    def med(x):
        return statistics.median(x) if x else float("nan")

    print(f"页数 {n}  页面 {doc[0].rect.width/MM:.0f}×{doc[0].rect.height/MM:.0f} mm")
    print(f"正文字号中位数   {med(sizes):.2f} pt")
    print(f"基线间距中位数   {med(gaps):.2f} pt   （行距/字号 = {med(gaps)/med(sizes):.2f}）")
    print(f"每行字数中位数   {med(chars):.0f} 字")
    if margins:
        # 版心是"最紧的那一页"决定的：取各边最小值（短页只会让边距看起来更大）
        l = min(m[0] for m in margins)
        t = min(m[1] for m in margins)
        r = min(m[2] for m in margins)
        b = min(m[3] for m in margins)
        print(f"页边距 左 {l:.0f} / 上 {t:.0f} / 右 {r:.0f} / 下 {b:.0f} mm")
        print(f"版心   {doc[0].rect.width/MM - l - r:.0f}×{doc[0].rect.height/MM - t - b:.0f} mm")
    print("\n对照：中文教材常用 10.5pt / 17pt / 40 字 / 版心 148×234")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    pages = 12
    if "--pages" in sys.argv:
        pages = int(sys.argv[sys.argv.index("--pages") + 1])
    analyse(sys.argv[1], pages)
