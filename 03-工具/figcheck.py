#!/usr/bin/env python3
"""figcheck.py —— 按《图表规格 v3》验收插图 SVG。

用法：
  python3 工具/figcheck.py 图v3/ch05          # 目录
  python3 工具/figcheck.py 图v3/ch05/*.svg    # 文件

判据：
  宽 ≤ 65 mm、高 ≤ 78 mm、图内基准字号 = 8.5 pt（mathtext 下标 5.95 放行）
  超限或字号不符即以非零码退出，并逐张列出。
"""
import glob
import os
import re
import sys

MAX_W, MAX_H = 65.0, 78.0
BASE_FS = 8.5
SUB_FS = (5.95, 5.1, 6.0, 4.25)   # mathtext 下标/上标，按比例缩小，放行

SVG_HEAD = re.compile(r'<svg[^>]*?width="([\d.]+)pt"[^>]*?height="([\d.]+)pt"')
FS = re.compile(r'font-size:\s*([\d.]+)px')
TEXT = re.compile(r'<text\b')


def check(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    m = SVG_HEAD.search(s)
    if not m:
        return {"file": path, "error": "no width/height in <svg>"}
    w_pt, h_pt = float(m.group(1)), float(m.group(2))
    w_mm, h_mm = w_pt / 72 * 25.4, h_pt / 72 * 25.4
    sizes = sorted({float(x) for x in FS.findall(s)})
    bad_fs = [x for x in sizes if x > BASE_FS + 0.01 or (x < BASE_FS - 0.01 and not any(abs(x - y) < 0.25 for y in SUB_FS))]
    return {
        "file": os.path.basename(path),
        "w_mm": round(w_mm, 1),
        "h_mm": round(h_mm, 1),
        "n_text": len(TEXT.findall(s)),
        "font_sizes": sizes,
        "over_w": w_mm > MAX_W + 0.3,
        "over_h": h_mm > MAX_H + 0.3,
        "bad_font": bad_fs,
    }


def main(argv):
    paths = []
    for a in argv:
        if os.path.isdir(a):
            paths += sorted(glob.glob(os.path.join(a, "*.svg")))
        else:
            paths += sorted(glob.glob(a))
    if not paths:
        print("没有找到 SVG。用法：figcheck.py <目录或文件…>")
        return 2

    fail = 0
    print(f"{'文件':<22}{'宽mm':>7}{'高mm':>7}{'字元素':>7}  字号集合")
    for p in paths:
        r = check(p)
        if "error" in r:
            print(f"{r['file']:<22}  !! {r['error']}")
            fail += 1
            continue
        flag = []
        if r["over_w"]:
            flag.append("宽超")
        if r["over_h"]:
            flag.append("高超")
        if r["bad_font"]:
            flag.append("字号" + "/".join(f"{x:g}" for x in r["bad_font"]))
        print(f"{r['file']:<22}{r['w_mm']:>7}{r['h_mm']:>7}{r['n_text']:>7}  {r['font_sizes']}  {' '.join(flag)}")
        if flag:
            fail += 1

    print(f"\n共 {len(paths)} 张，不合格 {fail} 张（上限 {MAX_W}×{MAX_H} mm，基准字号 {BASE_FS} pt）")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
