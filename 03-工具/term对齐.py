#!/usr/bin/env python3
"""term对齐.py —— 让「本章术语」表与正文 `<span class="term">` 首现一一对应。

用法：
  python3 工具/term对齐.py ../src/ch06_v8.md --dry     # 只看差集
  python3 工具/term对齐.py ../src/ch06_v8.md           # 落盘

做两件事：
1. 表里有、正文没标的词：在正文第一次出现处插
   `<span class="term">词</span>（<span class="en">english</span>）`；
2. 表里没有、正文标了的词：报告（不自动加行）。
跳过：标题行、表格行、图注、旁注、代码块。
"""
import re
import sys

TABLE_SEC = re.compile(r"## 本章术语(.*?)(?=\n: *表|\Z)", re.S)
ROW = re.compile(r"^\| *([^|]+?) *\| *([^|]+?) *\|", re.M)
SKIP_LINE = re.compile(r"^\s*(#{1,4} |\||>|!\[|: *表|```|---)")


def body_lines(lines, start, end):
    return [(i, l) for i, l in enumerate(lines[start:end], start) if not SKIP_LINE.match(l)]


def main(path, dry):
    src = open(path, encoding="utf-8").read()
    m = TABLE_SEC.search(src)
    if not m:
        print("没有「本章术语」节"); return 1
    rows = [(a.strip(), b.strip()) for a, b in ROW.findall(m.group(1))]
    rows = [(a, b) for a, b in rows if a not in ("术语", "---") and not set(a) <= set("-: ")]

    lines = src.split("\n")
    tstart = src[:m.start()].count("\n")
    tend = src[:m.end()].count("\n")

    marked = set(re.findall(r'<span class="term">(.+?)</span>', src))
    missing = [(a, b) for a, b in rows if a not in marked]
    extra = sorted(marked - {a for a, _ in rows})

    print(f"{path}: 表 {len(rows)} 条，已标 {len(marked)}，待补 {len(missing)}")
    if extra:
        print("  正文标了但表里没有：", extra)
    if not missing:
        return 0

    done, skipped = 0, []
    for name, en in missing:
        hit = None
        for i, line in body_lines(lines, 0, tstart):
            if name in line:
                # 不能落在已有 term 标记里
                idx = line.find(name)
                before = line[max(0, idx - 40):idx]
                if 'class="term"' in before and "</span>" not in before[before.rfind('class="term"'):]:
                    continue
                hit = (i, idx)
                break
        if not hit:
            skipped.append(name)
            continue
        i, idx = hit
        repl = f'<span class="term">{name}</span>（<span class="en">{en}</span>）'
        lines[i] = lines[i][:idx] + repl + lines[i][idx + len(name):]
        done += 1

    print(f"  已插 {done} 处；正文找不到（建议从表里删）: {skipped}")
    if not dry:
        open(path, "w", encoding="utf-8").write("\n".join(lines))
        print("  已写回")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], "--dry" in sys.argv))
