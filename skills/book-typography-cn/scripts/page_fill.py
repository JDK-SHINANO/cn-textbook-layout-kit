"""page_fill.py —— 找"半空页"（填充率低的页）

用法：
    python3 page_fill.py 书.pdf [--min 0.5]

思路：正文文字块的纵向跨度 ÷ 版心高度。低于阈值的页，多半是
"整表/整图跳页"或"孤行"造成的，是版式返工的第一线索。
"""
from __future__ import annotations

import sys

try:
    import pymupdf as fitz
except ImportError:
    import fitz


def main(path: str, threshold: float = 0.5):
    doc = fitz.open(path)
    bad = []
    for i, page in enumerate(doc):
        blocks = [b for b in page.get_text("dict")["blocks"]
                  if b.get("lines") and b.get("type") == 0]
        if not blocks:
            continue
        top = min(b["bbox"][1] for b in blocks)
        bottom = max(b["bbox"][3] for b in blocks)
        # 版心高度取页面高度减去上下各 28/35 mm 的近似值
        body = page.rect.height - (28 + 35) * 72 / 25.4
        fill = (bottom - top) / body
        if fill < threshold:
            bad.append((i + 1, round(fill * 100)))

    print(f"总页数 {doc.page_count}，填充率 < {int(threshold*100)}% 的页：{len(bad)} 页")
    for p, f in bad:
        print(f"  p{p}: {f}%")
    if len(bad) > doc.page_count * 0.05:
        print("\n提示：超过 5%，说明整表/整图跳页太多——允许表格跨页、图注跟随图片。")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    th = 0.5
    if "--min" in sys.argv:
        th = float(sys.argv[sys.argv.index("--min") + 1])
    main(sys.argv[1], th)
