#!/usr/bin/env python3
"""fix_quotes.py —— 把正文里的 ASCII 直引号成对换成中文引号“”。

跳过：数学环境（$…$、$$…$$）、HTML 标签内、反引号代码。
用法：python3 工具/fix_quotes.py ../src/ch06_v8.md [更多文件]
"""
import re
import sys


def convert(text):
    out = []
    i = 0
    n = len(text)
    in_math = False
    in_tag = False
    in_code = False
    opened = False
    while i < n:
        ch = text[i]
        if ch == "\\" and in_math and i + 1 < n:
            out.append(text[i:i + 2])
            i += 2
            continue
        if ch == "$" and not in_tag and not in_code:
            in_math = not in_math
            out.append(ch)
            i += 1
            continue
        if ch == "<" and not in_math and not in_code:
            in_tag = True
        elif ch == ">" and in_tag:
            in_tag = False
        elif ch == "`" and not in_tag and not in_math:
            in_code = not in_code
        if ch == '"' and not in_math and not in_tag and not in_code:
            out.append("”" if opened else "“")
            opened = not opened
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def main(files):
    for f in files:
        src = open(f, encoding="utf-8").read()
        new = convert(src)
        left = len(re.findall(r'"', new))
        open(f, "w", encoding="utf-8").write(new)
        print(f"{f}: 剩余直引号 {left} 个")


if __name__ == "__main__":
    main(sys.argv[1:])
