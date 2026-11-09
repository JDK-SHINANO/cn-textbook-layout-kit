#!/usr/bin/env python3
"""按章重出插图：双色 + SVG 矢量字（图内字号即纸上字号）。

两类图，两套规矩：
- **数据图**（曲线、条形、谱线）：图内不留解释性的字，只留坐标轴与曲线；
  说明交给图注与正文。
- **示意图**（剖面、几何、流程）：标注是图的一部分，**全部保留**——删了就成了哑图。

Axes 的几个开关是全局的，同一趟里没法一张一张切换，所以把同一份画图脚本
跑两遍（保留 / 去字），各写到临时目录，再按 SCHEMATIC 名单各取所需。

图一律按最终印刷宽度画（默认主栏 146mm，宽图 180mm），插入时不再缩放，
故图内 8.5 pt 就是纸上 8.5 pt。

用法：
  python3 工具/figs.py ch05
  FIG_WIDE=ch05_fig1,ch05_fig4            # 需要 180mm 的宽图
  FIG_SCHEMATIC=ch05_fig1,ch05_fig4       # 要保留标注的示意图
"""
import os
import re
import shutil
import sys

BOOK = os.path.abspath("../")
HERE = os.path.dirname(os.path.abspath(__file__))
CH = sys.argv[1] if len(sys.argv) > 1 else "ch04"

sys.path.insert(0, os.path.join(BOOK, "code"))
sys.path.insert(0, HERE)

import bookstyle  # noqa: E402

OUT = os.path.abspath(f"fig5_{CH}")
os.makedirs(OUT, exist_ok=True)
bookstyle.FIGDIR = OUT

# ---- 双色盘：一个主色 + 黑 + 两阶灰 ----
bookstyle.BLUE = "#2f6f9f"
bookstyle.BRICK = "#1a1a1a"
bookstyle.GREEN = "#1a1a1a"
bookstyle.SAND = "#8d99a4"
bookstyle.PURPLE = "#6b6b6b"
bookstyle.GRAY = "#6b6b6b"
bookstyle.LIGHT = "#dfe6ec"

import matplotlib  # noqa: E402
import matplotlib.axes as _ma  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.rcParams.update({
    "axes.grid": True,
    "grid.color": "#e3e9ee",
    # 与三线表同一档：粗 1.5pt（轴、数据线）／细 0.75pt（网格、主刻度）
    "grid.linewidth": 0.75,
    "grid.alpha": 0.6,
    "axes.edgecolor": "#1a1a1a",
    "axes.linewidth": 1.5,
    "xtick.major.width": 0.75,
    "ytick.major.width": 0.75,
    "xtick.minor.width": 0.5,
    "ytick.minor.width": 0.5,
    "lines.linewidth": 1.5,
    "lines.dash_capstyle": "round",
    # 图内字与图注同号
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8.5,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "svg.fonttype": "none",     # 文字保留为 <text>，不烙进位图
    "pdf.fonttype": 42,
})

WIDE = {s.strip() for s in os.environ.get("FIG_WIDE", "").split(",") if s.strip()}
SCHEMATIC = {s.strip() for s in os.environ.get("FIG_SCHEMATIC", "").split(",") if s.strip()}


def target_pt(name: str) -> float:
    w = 180 if os.path.splitext(os.path.basename(name))[0] in WIDE else 146
    return w / 25.4 * 72


def _savefig(fig, path):
    fig.savefig(path, format="svg", facecolor="white",
                bbox_inches="tight", pad_inches=0.06)


def save_svg(fig, name, tight=True, pad=0.12):
    """两遍：量 tight 裁切后的宽度，按比例调整画布，使成品≈目标宽度。"""
    if tight:
        try:
            fig.tight_layout(pad=pad)          # 收边，图更紧凑
        except Exception:
            pass
    path = os.path.join(bookstyle.FIGDIR, os.path.splitext(name)[0] + ".svg")
    _savefig(fig, path)
    m = re.search(r'width="([\d.]+)pt"', open(path, encoding="utf-8").read(600))
    if m:
        k = target_pt(name) / float(m.group(1))
        if abs(k - 1) > 0.01:
            w, h = fig.get_size_inches()
            fig.set_size_inches(w * k, h * k, forward=True)
            _savefig(fig, path)
    plt.close(fig)

    # 线宽只留两级：>1.5 → 1.5；0.8–1.0 → 0.75
    svg = open(path, encoding="utf-8").read()
    svg = re.sub(r"stroke-width: (1\.[5-9]\d*|[2-9](?:\.\d+)?)", "stroke-width: 1.5", svg)
    svg = re.sub(r"stroke-width: (0\.[89]\d*|1(\.0+)?)(?=[\"';\s])", "stroke-width: 0.75", svg)
    open(path, "w", encoding="utf-8").write(svg)
    m2 = re.search(r'width="([\d.]+)pt"', open(path, encoding="utf-8").read(600))
    print(f"saved: {path}  {float(m2.group(1)) / 72 * 25.4:.1f}mm")
    return path


bookstyle.save = save_svg

# ---------------- 去字开关 ----------------
_orig_text = _ma.Axes.text
_orig_annotate = _ma.Axes.annotate
_orig_title = _ma.Axes.set_title
_orig_legend = _ma.Axes.legend
_orig_note = bookstyle.note


def strip_on(strip: bool):
    if not strip:
        _ma.Axes.text = _orig_text
        _ma.Axes.annotate = _orig_annotate
        _ma.Axes.set_title = _orig_title
        _ma.Axes.legend = _orig_legend
        bookstyle.note = _orig_note
        return
    _ma.Axes.text = lambda self, *a, **k: None
    _ma.Axes.annotate = lambda self, *a, **k: None      # 引线箭头随之消失
    _ma.Axes.set_title = lambda self, *a, **k: None
    _ma.Axes.legend = lambda self, *a, **k: None
    bookstyle.note = lambda *a, **k: None


# ---------------- 两趟执行，各取所需 ----------------
dual = os.path.join(HERE, f"fig_{CH}_dual.py")
if not os.path.exists(dual):
    shutil.copy(os.path.join(BOOK, "code", f"fig_{CH}.py"), dual)
    print("（从 code/ 复制了", os.path.basename(dual), "）")

source = open(dual, encoding="utf-8").read()
tmp = {m: os.path.join(OUT, f"_{m}") for m in ("keep", "strip")}
for d in tmp.values():
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)

for mode in ("keep", "strip"):
    bookstyle.FIGDIR = tmp[mode]
    strip_on(mode == "strip")
    exec(compile(source, dual, "exec"), {"__name__": "__main__", "__file__": dual})

kept = stripped = 0
for f in sorted(os.listdir(tmp["keep"])):
    is_schematic = os.path.splitext(f)[0] in SCHEMATIC
    src = os.path.join(tmp["keep"] if is_schematic else tmp["strip"], f)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, f))
        kept += is_schematic
        stripped += not is_schematic
for d in tmp.values():
    shutil.rmtree(d, ignore_errors=True)

print(f"归位：示意图（保留标注）{kept} 张，数据图（去字）{stripped} 张 → {OUT}")
