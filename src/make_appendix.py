#!/usr/bin/env python3
"""make_appendix.py —— 从各章 v8 稿生成书末附录 D（术语总索引）与 E（插图目录）。

排序按 GB/T 22466—2023：术语条目用汉语拼音。本机 glibc 的 zh_CN.UTF-8
collation 就是拼音序，故借 `sort` 排，不装 pypinyin。

用法：python3 工具/make_appendix.py
输出：src/appendix_D.md、src/appendix_E.md
"""
import glob
import os
import re
import subprocess
import tempfile

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROW = re.compile(r"^\| *([^|]+?) *\| *([^|]+?) *\| *([^|]*?) *\|", re.M)
FIG = re.compile(r"^!\[图\s*(\d+)-(\d+)　(.+?)\]", re.M)


def chapter_files():
    files = [os.path.join(BOOK, "src", "part0_v8.md")]
    files += sorted(glob.glob(os.path.join(BOOK, "src", "ch[0-9][0-9]_v8.md")))
    return [f for f in files if os.path.exists(f)]


def parse(path, num):
    src = open(path, encoding="utf-8").read()
    terms, figs = [], []
    m = re.search(r"## 本章术语(.*?)(?=\n: *表|\n## |\Z)", src, re.S)
    if m:
        for a, b, _ in ROW.findall(m.group(1)):
            a, b = a.strip(), b.strip()
            if a in ("术语", "---") or set(a) <= set("-: "):
                continue
            terms.append((a, b, num))
    for a, b, t in FIG.findall(src):
        figs.append((int(a), int(b), t.strip(), num))
    return terms, figs


def pinyin_sorted(items):
    """借系统 collation 排拼音序。"""
    lines = ["\t".join([t[0], t[1], t[2]]) for t in items]
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", encoding="utf-8", delete=False) as fh:
        fh.write("\n".join(lines) + "\n")
        path = fh.name
    env = dict(os.environ, LC_ALL="zh_CN.UTF-8", LANG="zh_CN.UTF-8")
    out = subprocess.run(["sort", "-s", "-k1,1", path], capture_output=True, text=True, env=env).stdout
    os.unlink(path)
    res = []
    for ln in out.strip().split("\n"):
        if ln:
            p = ln.split("\t")
            res.append(tuple(p))
    return res


def main():
    terms, figs = [], []
    for f in chapter_files():
        base = os.path.basename(f)
        num = "0" if base.startswith("part0") else str(int(re.search(r"ch(\d\d)", base).group(1)))
        t, g = parse(f, num)
        terms += t
        figs += g

    # 同一术语只留一条，章号合并
    merged = {}
    for zh, en, num in terms:
        key = zh
        if key in merged:
            en0, chs = merged[key]
            merged[key] = (en0 or en, sorted(set(chs + [num]), key=int))
        else:
            merged[key] = (en, [num])

    rows = pinyin_sorted([(zh, en, ",".join(chs)) for zh, (en, chs) in merged.items()])

    d = ["# 附录 D　术语总索引", "",
         "按汉语拼音排序（GB/T 22466—2023）。数字为首次出现的章号；同一术语只列一次。", "",
         "| 术语 | 英文 | 章 |", "|---|---|---|"]
    for zh, en, chs in rows:
        d.append(f"| {zh} | {en} | {chs} |")
    d += ["", f": 表 D-1　全书术语总索引（{len(rows)} 条）", ""]
    open(os.path.join(BOOK, "src", "appendix_D.md"), "w", encoding="utf-8").write("\n".join(d))

    figs.sort(key=lambda x: (int(x[3]), x[0], x[1]))
    e = ["# 附录 E　插图目录", "", "| 图号 | 图题 | 章 |", "|---|---|---|"]
    for a, b, t, num in figs:
        e.append(f"| 图 {a}-{b} | {t} | {num} |")
    e += ["", f": 表 E-1　全书插图目录（{len(figs)} 幅）", ""]
    open(os.path.join(BOOK, "src", "appendix_E.md"), "w", encoding="utf-8").write("\n".join(e))

    print(f"术语 {len(rows)} 条（合并前 {len(terms)}）；插图 {len(figs)} 幅")


if __name__ == "__main__":
    main()
