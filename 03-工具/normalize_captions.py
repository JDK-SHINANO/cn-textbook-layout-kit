#!/usr/bin/env python3
"""normalize_captions.py —— 把写在表格前面的 `: 表 N-K　…` 挪到表后。

pandoc 的表格 caption：`:` 行要紧贴表格（后一行），中间隔空行就退化成正文段落，
印出来表题会是 10.48 pt 的正文，不是 caption。有些章节把表题写在了表前，本脚本统一。

用法：python3 工具/normalize_captions.py ../src/ch10_v8.md [更多文件]
"""
import re
import sys

CAP = re.compile(r"^: *表 ")
ROW = re.compile(r"^\|")


def fix(text):
    lines = text.split("\n")
    out = []
    i = 0
    moved = 0
    while i < len(lines):
        ln = lines[i]
        if CAP.match(ln):
            # 向前找表格首行（跳过空行）
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and ROW.match(lines[j]):
                # 找表格末行
                k = j
                while k < len(lines) and ROW.match(lines[k]):
                    k += 1
                out.extend(lines[j:k])
                out.append(ln)
                moved += 1
                i = k
                continue
        out.append(ln)
        i += 1
    return "\n".join(out), moved


def main(files):
    for f in files:
        src = open(f, encoding="utf-8").read()
        new, n = fix(src)
        if n:
            open(f, "w", encoding="utf-8").write(new)
        print(f"{f}: 挪动表题 {n} 处")


if __name__ == "__main__":
    main(sys.argv[1:])
