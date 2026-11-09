#!/usr/bin/env python3
"""make_cover.py —— 生成封面顶部的重复纹样（核子＋轨道，灰阶）。

参考《基础有机化学》封面：顶部一排排重复的结构图，灰黑，留白在上。
我们换成核物理的意象：每个单元是一个核（实心圆）加两条交叉轨道。

输出：图v3/cover_pattern.svg（180 mm × 58 mm）
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse

W, H = 180 / 25.4, 58 / 25.4
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "图v3")

fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 180)
ax.set_ylim(0, 58)
ax.axis("off")

GREY = "#8e8e8e"
DARK = "#5f5f5f"

# 三行交错排列，行内等距；单元 = 核 + 两条交叉椭圆轨道
for row, y in enumerate((44.0, 29.0, 14.0)):
    offset = 0 if row % 2 == 0 else 7.5
    for x in range(-4, 190, 15):
        cx = x + offset
        ax.add_patch(Ellipse((cx, y), 13.2, 4.6, angle=28, fill=False,
                             ec=GREY, lw=0.7))
        ax.add_patch(Ellipse((cx, y), 13.2, 4.6, angle=-28, fill=False,
                             ec=GREY, lw=0.7))
        ax.add_patch(Circle((cx, y), 1.55, fc=DARK, ec="none"))

fig.savefig(os.path.join(OUT, "cover_pattern.svg"), transparent=True)
fig.savefig(os.path.join(OUT, "cover_pattern.png"), transparent=True, dpi=300)
print("封面纹样写好:", os.path.join(OUT, "cover_pattern.svg"))
