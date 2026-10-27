#!/usr/bin/env python3
"""验收章.py —— 按《章节骨架 v3》逐章体检。

用法：
  python3 工具/验收章.py ../src/ch05_v8.md [../src/ch05_v8.md …]
  python3 工具/验收章.py ../src/ch05_v8.md --orig ../src/ch05.md   # 附录数字集合比对

只读，不改文件。退出码 = 不合格项数（0 为全过）。
"""
import re
import sys

AI = re.compile(r"换句话说|简单来说|值得注意的是|值得注意的是|请记住|你会发现|让我们一起|不难看出|众所周知|总而言之|一句话(讲清|看懂|说清)|三分钟|值得注意|需要指出的是|在这里我们|我们不妨")
SLOGAN_H = re.compile(r"^#{2,4}\s*(它要解决什么问题|麻烦来了|为什么.{0,12}[？?]$|一句话|三分钟|让我们|你想)")
H2 = re.compile(r"^##\s+(.+)$", re.M)
H3 = re.compile(r"^###\s+(.+)$", re.M)
TERM = re.compile(r'<span class="term">(.+?)</span>')
EN = re.compile(r'<span class="en">(.+?)</span>')
BOLD = re.compile(r"\*\*(.+?)\*\*")
FIG = re.compile(r"^!\[图\s*(\d+)-(\d+)", re.M)
FIGREF = re.compile(r"图\s*(\d+)-(\d+)")
TAB = re.compile(r"^(?::\s*)?表\s*(\d+)-(\d+)", re.M)
例 = re.compile(r"^例\s*(\d+)-(\d+)", re.M)
题 = re.compile(r"题\s*(\d+)-(\d+)")
NUMS = re.compile(r"\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
SEC_REQ = ["动手算一算", "本章要点", "本章术语"]


def stats(text):
    han = len(re.findall(r"[\u4e00-\u9fff]", text))
    return dict(
        汉字=han,
        行间公式=len(re.findall(r"\$\$.*?\$\$", text, re.S)),
        图=len(FIG.findall(text)),
        图引用=len(set(FIGREF.findall(text))),
        表=len(TAB.findall(text)),
        例题=len(set(例.findall(text))),
        习题=len(set(题.findall(text))),
        三级标题=len(H3.findall(text)),
        term=len(TERM.findall(text)),
        en=len(EN.findall(text)),
        加粗=len(BOLD.findall(text)),
        你=len(re.findall("你", text)),
        AI腔=len(AI.findall(text)),
        超长句=len([s for s in re.split(r"[。！？\n]", text) if len(re.findall(r"[\u4e00-\u9fff]", s)) > 90]),
    )


def main(argv):
    files = [a for a in argv if not a.startswith("--")]
    orig = None
    if "--orig" in argv:
        orig = argv[argv.index("--orig") + 1]
    otext = open(orig, encoding="utf-8").read() if orig else None

    bad_total = 0
    for f in files:
        t = open(f, encoding="utf-8").read()
        s = stats(t)
        h2 = [x.strip() for x in H2.findall(t)]
        missing = [x for x in SEC_REQ if not any(x in y for y in h2)]
        bold_per_k = s["加粗"] / max(s["汉字"], 1) * 1000
        you_per_k = s["你"] / max(s["汉字"], 1) * 1000
        slogan = SLOGAN_H.findall(t)

        print(f"\n===== {f} =====")
        print(f"汉字 {s['汉字']}｜行间公式 {s['行间公式']}｜图注 {s['图']}（唯一引用 {s['图引用']}）｜表 {s['表']}｜例题 {s['例题']}｜习题 {s['习题']}｜三级标题 {s['三级标题']}")
        print(f"term {s['term']}｜en {s['en']}｜加粗 {s['加粗']}（{bold_per_k:.1f}/千字）｜你 {s['你']}（{you_per_k:.1f}/千字）｜AI腔 {s['AI腔']}｜超长句 {s['超长句']}")

        probs = []
        if missing:
            probs.append("缺章末节：" + "、".join(missing))
        if s["AI腔"]:
            probs.append(f"AI 腔 {s['AI腔']} 处")
        if slogan:
            probs.append("口号/导语式标题：" + "；".join(slogan[:3]))
        if bold_per_k > 4.05:
            probs.append(f"加粗 {bold_per_k:.1f}/千字 > 4")
        if you_per_k > 2.05:
            probs.append(f"「你」{you_per_k:.1f}/千字 > 2")
        if s["term"] < 8:
            probs.append(f"term 标记 {s['term']} < 8")
        if s["图"] > 6:
            probs.append(f"图注 {s['图']} > 6（v3 每章 3–5 张单幅）")
        if s["图"] != s["图引用"]:
            probs.append(f"图注 {s['图']} ≠ 唯一图引用 {s['图引用']}（有图未被引用或引用无图）")
        if s["超长句"] > 2:
            probs.append(f"超长句 {s['超长句']} > 2")

        if otext:
            na = set(NUMS.findall(otext))
            nb = set(NUMS.findall(t))
            lost = sorted(na - nb, key=lambda x: (len(x), x))[:12]
            new = sorted(nb - na, key=lambda x: (len(x), x))[:12]
            print(f"数字集合：原 {len(na)}／新 {len(nb)}｜只丢 {lost}｜只增 {new}")

        if probs:
            bad_total += len(probs)
            for p in probs:
                print("  ✗", p)
        else:
            print("  ✓ 全过")

    print(f"\n不合格项合计 {bad_total}")
    return bad_total


if __name__ == "__main__":
    sys.exit(min(main(sys.argv[1:]), 120))
