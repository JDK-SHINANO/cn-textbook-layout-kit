#!/usr/bin/env python3
"""量线：把页面渲成高分辨率位图，数暗像素连续厚度，换算成 pt。

用法： python3 工具/线宽.py out/sample.pdf 页码 x位置mm y起mm y止mm [标号]
"""
import sys

import pymupdf

DPI = 1200
PT = DPI / 72          # 每 pt 多少像素


def run_thickness(pdf, page_no, x_mm, y0_mm, y1_mm):
    doc = pymupdf.open(pdf)
    page = doc[page_no - 1]
    mm = DPI / 25.4
    clip = pymupdf.Rect(x_mm * 25.4 / 25.4 * 72 / 25.4, y0_mm * 72 / 25.4,
                        (x_mm + 1) * 72 / 25.4, y1_mm * 72 / 25.4)
    pix = page.get_pixmap(dpi=DPI, clip=clip, colorspace=pymupdf.csGRAY)
    w, h = pix.width, pix.height
    col = 0
    runs = []
    start = None
    for y in range(h):
        v = pix.pixel(col, y)[0]
        dark = v < 140
        if dark and start is None:
            start = y
        elif not dark and start is not None:
            runs.append((start, y - start))
            start = None
    return [(round(y / mm, 2), round(n / PT, 2)) for y, n in runs]


if __name__ == "__main__":
    pdf, page_no, x_mm, y0, y1 = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
    print(f"{pdf} p{page_no} @x={x_mm}mm")
    for ymm, t in run_thickness(pdf, page_no, x_mm, y0, y1):
        print(f"  y={ymm}mm  厚 {t} pt")
