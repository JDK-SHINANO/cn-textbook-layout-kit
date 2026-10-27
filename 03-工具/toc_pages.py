#!/usr/bin/env python3
"""toc_pages.py —— 从成品 PDF 书签导出目录条目（章 + 节）与页码，写 src/toc_entries.json。

用法（需 PyMuPDF）：
  ${PYMUPDF:-python3} 工具/toc_pages.py out/全书_v3.pdf

输出：[{"lvl":1,"title":"第 1 章　物质的最小单位","page":14}, …]
目录条数固定，页码写入不改分页；两遍即可稳定。
"""
import json
import re
import os
import sys

import pymupdf

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(pdf):
    doc = pymupdf.open(pdf)
    flat = [re.sub(r"\s+", "", doc[i].get_text()) for i in range(doc.page_count)]
    # 目录页算第 1 页：封面、空白页、版权页不计数
    toc_first = next((i for i in range(min(12, len(flat))) if flat[i].startswith("目录")), 0)
    entries, seen = [], set()
    for lvl, title, pg in doc.get_toc():
        if lvl > 3:
            continue
        key = (lvl, title)
        if key in seen:
            continue
        seen.add(key)
        entries.append({"lvl": lvl, "title": title, "page": pg - toc_first})
    out = os.path.join(BOOK, "src", "toc_entries.json")
    json.dump(entries, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    n1 = sum(1 for e in entries if e["lvl"] == 1)
    print(f"目录条目 {len(entries)} 条（章 {n1}）→ src/toc_entries.json")


if __name__ == "__main__":
    main(sys.argv[1])
