#!/usr/bin/env python3
"""page_guides.py —— 在某一页上画毫米参考线，用来核对版心 / 副区 / 页眉是否对齐。

为什么要有它：几何参数与读者／用户有分歧时，文字争论无效，画一张带标注的放大裁切图
最省事。

用法：
  python3 page_guides.py 书.pdf 5 --v 18.5,52.5 --h 24
  python3 page_guides.py 书.pdf 5 --v 18.5,52.5 --crop 8,55,70,95 --dpi 140

参数：
  page          1 起的页号
  --v a,b,...   竖向参考线（距纸张左边缘的 mm）
  --h a,b,...   横向参考线（距纸张上边缘的 mm）
  --crop x0,y0,x1,y1   只裁这一块（mm），自动放大 4 倍，便于看细节
  --dpi         渲染分辨率，默认 140
  --out         输出 PNG 路径，默认 /tmp/guides_p<page>.png

依赖 pymupdf + Pillow；系统 python 无 pymupdf 时用装了它的解释器
（本机：~/.hermes/Claw_Shinano/tool/marker-pdf-env/bin/python）。
"""
import argparse

import pymupdf
from PIL import Image, ImageDraw

COLORS = [(220, 30, 30), (30, 140, 60), (30, 80, 200), (200, 120, 0)]


def parse_mm(s):
    return [float(x) for x in s.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("page", type=int)
    ap.add_argument("--v", default="")
    ap.add_argument("--h", default="")
    ap.add_argument("--crop", default="")
    ap.add_argument("--dpi", type=int, default=140)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    page = doc[a.page - 1]
    mm = 72 / 25.4
    w_mm, h_mm = page.rect.width / mm, page.rect.height / mm

    zoom = a.dpi / 72.0
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    px = lambda v: v * zoom * mm  # noqa: E731

    if a.crop:
        x0, y0, x1, y1 = parse_mm(a.crop)
        off_x, off_y = px(x0), px(y0)
        box = (int(off_x), int(off_y), int(px(x1)), int(px(y1)))
        im = im.crop(box)
        scale = 4
        im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
        f = lambda v: (px(v) - off_x) * scale  # noqa: E731
        g = lambda v: (px(v) - off_y) * scale  # noqa: E731
    else:
        f, g = px, px

    d = ImageDraw.Draw(im)
    for i, v in enumerate(parse_mm(a.v)):
        x = f(v)
        col = COLORS[i % len(COLORS)]
        for y in range(0, im.height, 18):
            d.line([(x, y), (x, min(y + 9, im.height))], fill=col, width=2)
        d.text((x + 6, 4), f"{v:g}mm", fill=col)
    for i, v in enumerate(parse_mm(a.h)):
        y = g(v)
        col = COLORS[(i + 2) % len(COLORS)]
        for x in range(0, im.width, 18):
            d.line([(x, y), (min(x + 9, im.width), y)], fill=col, width=2)
        d.text((4, y + 3), f"{v:g}mm", fill=col)

    out = a.out or f"/tmp/guides_p{a.page}.png"
    im.save(out)
    print(f"页面 {w_mm:.1f}×{h_mm:.1f} mm → {out}  ({im.width}×{im.height})")


if __name__ == "__main__":
    main()
