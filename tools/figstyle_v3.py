#!/usr/bin/env python3
"""figstyle_v3.py —— 《从零开始的核物理与核能》v3 插图公共样式。

规矩（见 规范/图表规格_v3.md）：
  · 画布按印刷毫米出图，宽 ≤65 mm、高 ≤78 mm，插入不缩放
  · 图内文字一律 8.5 pt（轴标、刻度、图例、示意标注同号）
  · 线宽两档：轴与曲线 0.75 pt；网格与主刻度 0.4 pt；不画次刻度
  · 主刻度 ≤5 个（8.5 pt 下再密就叠字）
  · 主色 #2f6f9f；黑 #1a1a1a；灰 #6b6b6b；浅灰 #c9d2da；底纹 #eef3f7

用法：
    import figstyle_v3 as fs
    fig, ax = fs.new(58, 44)          # 宽 58 mm、高 44 mm
    ax.plot(x, y, color=fs.MAIN, lw=fs.LW_LINE)
    fs.ticks(ax, 5)
    ax.set_xlabel(r"能量 / MeV"); ax.set_ylabel(r"截面 / b")
    fs.save(fig, "ch05_fig2", outdir="图v3")
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MAIN = "#2f6f9f"
INK = "#1a1a1a"
GRAY = "#6b6b6b"
LIGHT = "#c9d2da"
FILL = "#eef3f7"

LW_AXIS = 0.75
LW_LINE = 0.75
LW_GRID = 0.4
FS = 8.5
MAX_W, MAX_H = 65.0, 78.0

matplotlib.rcParams.update({
    "font.family": ["Noto Sans SC", "Noto Serif SC", "Noto Sans CJK JP", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "svg.fonttype": "none",      # 文字留成 <text>，不烙进位图
    "pdf.fonttype": 42,
    "font.size": FS,
    "axes.labelsize": FS,
    "axes.titlesize": FS,
    "xtick.labelsize": FS,
    "ytick.labelsize": FS,
    "legend.fontsize": FS,
    "legend.frameon": False,
    "lines.linewidth": LW_LINE,
    "axes.linewidth": LW_AXIS,
    "axes.edgecolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "axes.grid": True,
    "grid.color": LIGHT,
    "grid.linewidth": LW_GRID,
    "grid.alpha": 0.9,
    "xtick.major.width": LW_GRID,
    "ytick.major.width": LW_GRID,
    "xtick.minor.visible": False,
    "ytick.minor.visible": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "standard",
})


def new(w_mm, h_mm):
    """按印刷毫米数建一张图。宽高超限直接报错，避免事后才发现。

    用 constrained 布局：图幅固定，坐标区自动让出轴标与刻度的位置——
    58 mm 宽的图上，手调边距十有八九会把横轴标签挤到画布外。
    """
    if w_mm > MAX_W + 0.01 or h_mm > MAX_H + 0.01:
        raise ValueError(f"图幅 {w_mm}×{h_mm} mm 超限（≤{MAX_W}×{MAX_H}）")
    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4), layout="constrained")
    return fig, ax


def ticks(ax, n=5, axis="both", log=False):
    """主刻度限个数：8.5 pt 下一张 65 mm 图最多容 5 个刻度数字。"""
    import matplotlib.ticker as mt
    for a in ([ax.xaxis, ax.yaxis] if axis == "both" else [ax.xaxis if axis == "x" else ax.yaxis]):
        if log:
            a.set_major_locator(mt.LogLocator(numticks=n))
            a.set_minor_locator(mt.NullLocator())
        else:
            a.set_major_locator(mt.MaxNLocator(nbins=n - 1, prune=None))
            a.set_minor_locator(mt.NullLocator())


def clamp_lw(fig):
    """出图后把线宽钳到两档，免得脚本里随手写的 lw=2 比坐标轴还粗。"""
    for ax in fig.axes:
        for ln in ax.get_lines():
            lw = ln.get_linewidth()
            ln.set_linewidth(LW_LINE if lw > 0.5 else LW_GRID)
        for sp in ax.spines.values():
            sp.set_linewidth(LW_AXIS)


def audit(fig):
    """查图内文字是否互压、是否越出画布。返回 (重叠对, 越界数)。

    只审「看得见」的字：轴标、标题、注释、图例、以及落在坐标范围内的刻度。
    matplotlib 为范围外的刻度也建了 Text 对象，它们根本不画，审了全是假阳性。
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = []
    for ax in fig.axes:
        cand = [ax.xaxis.label, ax.yaxis.label, ax.title] + list(ax.texts)
        leg = ax.get_legend()
        if leg is not None:
            cand += list(leg.get_texts())
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            lo, hi = min(lim), max(lim)
            for tick in axis.get_major_ticks():
                loc = tick.get_loc()
                if lo - 1e-12 <= loc <= hi + 1e-12:
                    cand.append(tick.label1)
        for t in cand:
            s = t.get_text().strip()
            if not s or not t.get_visible():
                continue
            try:
                bb = t.get_window_extent(r)
            except Exception:
                continue
            items.append((s, bb))
    fb = fig.bbox
    over = [s for s, bb in items if bb.x0 < fb.x0 - 1 or bb.y0 < fb.y0 - 1 or bb.x1 > fb.x1 + 1 or bb.y1 > fb.y1 + 1]
    pairs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][1], items[j][1]
            if a.overlaps(b):
                ia = a.intersection(a, b)
                if ia is not None and ia.width * ia.height > 2:
                    pairs.append((items[i][0], items[j][0]))
    return pairs, over


def save(fig, name, outdir="图v3"):
    clamp_lw(fig)
    pairs, over = audit(fig)
    if pairs:
        print(f"  ! 文字互压 {len(pairs)} 对: {pairs[:5]}")
    if over:
        print(f"  ! 越出画布 {len(over)} 处: {over[:5]}")
    os.makedirs(outdir, exist_ok=True)
    for ext in ("svg", "png"):
        path = os.path.join(outdir, f"{name}.{ext}")
        fig.savefig(path, dpi=300)
        print("写出", path)
    plt.close(fig)
    return len(pairs) + len(over)
