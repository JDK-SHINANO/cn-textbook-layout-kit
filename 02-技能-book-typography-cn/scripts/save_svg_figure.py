#!/usr/bin/env python3
"""把 matplotlib 图存成「矢量字」SVG，并把画布校准到目标印刷宽度。

为什么：PNG 里的字是像素，插进版心一缩放就糊，字号也不再是设计值。
``svg.fonttype='none'`` 让文字留在 SVG 的 ``<text>`` 里，由浏览器按 pt 现排；
再把画布宽度校准到最终印刷宽度（如版心 180mm），插入时缩放比 ≈1，
图内 8.5pt 在纸上就是 8.5pt，可用 PyMuPDF 抽 span 复验。

用法::

    import matplotlib; matplotlib.use("Agg")
    import save_svg_figure as sf

    sf.setup()                      # 设 svg.fonttype='none'
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    ...
    sf.save_svg(fig, "out/fig1.svg", target_mm=180)

为什么是两遍：``bbox_inches="tight"`` 会按内容重新算尺寸，``set_size_inches()``
不保证输出的英寸数。所以「存一次 → 读实际 width → 按比例重设画布 → 再存一次」。
"""
from __future__ import annotations

import os
import re

MM_PER_IN = 25.4
PT_PER_IN = 72.0


def setup() -> None:
    """必须在建图之前调用：让文字留在 SVG 里而不是烙成路径/位图。"""
    import matplotlib

    matplotlib.rcParams.update({
        "svg.fonttype": "none",   # ★ 核心：文字保留为 <text>
        "pdf.fonttype": 42,
    })


def _width_pt(path: str) -> float | None:
    with open(path, encoding="utf-8", errors="ignore") as f:
        head = f.read(800)
    m = re.search(r'width="([\d.]+)pt"', head)
    return float(m.group(1)) if m else None


def save_svg(fig, path: str, target_mm: float = 180.0, tight: bool = True,
             pad: float = 0.25) -> str:
    """存 SVG 并把画布宽度校准到 target_mm（失败时至少返回已存的文件）。"""
    import matplotlib.pyplot as plt

    if tight:
        try:
            fig.tight_layout(pad=pad)
        except Exception:
            pass

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.savefig(path, format="svg", facecolor="white",
                bbox_inches="tight" if tight else None, pad_inches=0.12)

    target_pt = target_mm / MM_PER_IN * PT_PER_IN
    got = _width_pt(path)
    if got and abs(target_pt - got) / target_pt > 0.01:
        k = target_pt / got
        w, h = fig.get_size_inches()
        fig.set_size_inches(w * k, h * k, forward=True)
        fig.savefig(path, format="svg", facecolor="white",
                    bbox_inches="tight" if tight else None, pad_inches=0.12)

    plt.close(fig)
    got = _width_pt(path)
    if got:
        print(f"saved: {path}  {got / PT_PER_IN * MM_PER_IN:.1f}mm（目标 {target_mm}mm）")
    return path


def verify_in_pdf(pdf_path: str, needle: str, pymupdf_module=None):
    """复验：图内标签在 PDF 里应是真文本，且 size ≈ 设计磅值。

    返回 [(页码, 字号, 字体名), ...]；空列表说明图成了位图，字被烙死了。
    """
    fitz = pymupdf_module
    if fitz is None:
        import pymupdf as fitz  # noqa: F401
    doc = fitz.open(pdf_path)
    hits = []
    for i, page in enumerate(doc):
        if needle not in page.get_text():
            continue
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if needle in span["text"]:
                        hits.append((i + 1, round(span["size"], 2), span["font"]))
    return hits


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        print(verify_in_pdf(sys.argv[1], sys.argv[2]))
    else:
        print(__doc__)
