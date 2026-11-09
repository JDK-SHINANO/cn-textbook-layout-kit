#!/usr/bin/env python3
"""对照图 —— 旧版（A4）与新样张（16 开）同内容页并置。

用法： python3 工具/对照图.py
"""
import os
import pymupdf
from PIL import Image, ImageDraw, ImageFont

OLD = "../教材/从零开始的核物理与核能.pdf"
NEW = "out/sample.pdf"
OUT = "out"
PW, PH = 4.2, 4.2        # px/mm，两版按同一比例，直观比大小
GAP, PAD, CAP = 26, 28, 34
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

PAIRS = [
    ("对照1_章首页", 63, 0, "章首页"),
    ("对照2_正文与边注", 67, 4, "正文页（新：边注落副区）"),
    ("对照3_表页", 74, 13, "表 4-1 所在页"),
    ("对照4_题解", 75, 17, "习题详解（旧：章内；新：书末题解）"),
]


def page_img(doc, idx, scale):
    pix = doc[idx].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return img


def compose(old_img, new_img, cap_old, cap_new, path):
    W = PAD * 3 + old_img.width + new_img.width
    H = PAD * 2 + max(old_img.height, new_img.height) + CAP
    cv = Image.new("RGB", (W, H), (245, 244, 242))
    dr = ImageDraw.Draw(cv)
    f = ImageFont.truetype(FONT, 22)
    f2 = ImageFont.truetype(FONT, 17)
    for img, x, cap, col in (
        (old_img, PAD, cap_old, (120, 100, 80)),
        (new_img, PAD * 2 + old_img.width, cap_new, (47, 111, 159)),
    ):
        cv.paste(img, (x, PAD))
        dr.rectangle([x - 1, PAD - 1, x + img.width, PAD + img.height],
                     outline=(205, 200, 194), width=1)
        dr.text((x, PAD + img.height + 8), cap, font=f, fill=col)
    dr.text((PAD, 8), "旧版 · A4 210×297", font=f2, fill=(120, 100, 80))
    dr.text((PAD * 2 + old_img.width, 8), "样张 · 195×260", font=f2, fill=(47, 111, 159))
    cv.save(path)
    print("写出", path, cv.size)


def main():
    old, new = pymupdf.open(OLD), pymupdf.open(NEW)
    for name, oi, ni, cap in PAIRS:
        a, b = page_img(old, oi, PW), page_img(new, ni, PW)
        compose(a, b, f"旧 · 第 {oi + 1} 页 · {cap}", f"新 · 第 {ni + 1} 页 · {cap}",
                os.path.join(OUT, f"{name}.png"))


if __name__ == "__main__":
    main()
