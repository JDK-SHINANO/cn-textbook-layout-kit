"""
bookstyle.py —— 全书的图形风格（所有章节共用）

用法（在每一章的 fig_chNN.py 开头）：
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from bookstyle import *

    fig, ax = plt.subplots(figsize=(7,4))
    ...
    save(fig, "ch02_fig1.png")      # 输出到 ../图/ch02_fig1.png

约定：
  · 字号 10/11，DPI 150，白底
  · 配色：BLUE 主线、BRICK 强调/警示、GREEN 正确路径、PURPLE 次要、SAND 高亮
  · 坐标轴一律带单位；图内不要写标题（标题写在正文图注里）
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---- 字体：本机 Noto Sans SC（中文）+ DejaVu（符号） ----
plt.rcParams.update({
    "font.family": ["Noto Sans SC", "Noto Sans CJK JP", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10,
    "axes.labelsize": 10.5,
    "axes.titlesize": 11,
    "legend.fontsize": 8.5,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 100,
    "savefig.dpi": 200,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "axes.edgecolor": "#555555",
    "axes.linewidth": 0.9,
    "figure.facecolor": "white",
})

BLUE = "#2f6f9f"
BRICK = "#c1553b"
GREEN = "#5a8f5a"
PURPLE = "#8a6a9f"
SAND = "#c9a227"
GRAY = "#777777"
LIGHT = "#c9d6e2"

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(os.path.dirname(HERE), "图")


def save(fig, name, tight=True, pad=0.25):
    """保存并关闭图；返回路径。name 例如 'ch02_fig1.png'"""
    os.makedirs(FIGDIR, exist_ok=True)
    if tight:
        try:
            fig.tight_layout(pad=pad)
        except Exception:
            pass
    # 画布收到印刷宽度（148 mm = 5.83 in），字号不变 → 图内文字相对放大，印出 1:1
    w, h = fig.get_size_inches()
    if w > 5.83:
        fig.set_size_inches(5.83, h * 5.83 / w, forward=True)
    path = os.path.join(FIGDIR, name)
    fig.savefig(path, dpi=plt.rcParams["savefig.dpi"], facecolor="white", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("saved:", path)
    return path


def note(ax, x, y, text, color="#333333", fs=8.5, ha="left", va="bottom", **kw):
    """统一风格的图内标注。"""
    return ax.annotate(text, (x, y), fontsize=fs, color=color, ha=ha, va=va, **kw)


def arrow(ax, p0, p1, color=GRAY, lw=1.4, style="-|>", ls="-", rad=0.0):
    """统一风格的箭头。"""
    from matplotlib.patches import FancyArrowPatch
    return ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle=style, mutation_scale=12, lw=lw,
        color=color, linestyle=ls,
        connectionstyle=f"arc3,rad={rad}"))


def hband(ax, lo, hi, color=LIGHT, alpha=0.35, label=None):
    """横向色带（表示"可接受区间"之类）。"""
    ax.axhspan(lo, hi, color=color, alpha=alpha, zorder=0, label=label)


def vband(ax, lo, hi, color=LIGHT, alpha=0.35, label=None):
    ax.axvspan(lo, hi, color=color, alpha=alpha, zorder=0, label=label)


# ---- 常用物理量（全书统一，别各写各的） ----
NA = 6.02214076e23      # 1/mol
MEV_J = 1.602176634e-13  # 1 MeV 的焦耳数
U_KG = 1.66053906660e-27  # 原子质量单位 kg
U_MEV = 931.494          # 1 u 对应的能量 MeV
E_CHARGE = 1.602176634e-19
ALPHA = 1 / 137.035999   # 精细结构常数
K_COULOMB = 8.9875517923e9  # N·m²/C²
