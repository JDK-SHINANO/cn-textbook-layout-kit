#!/usr/bin/env python3
"""规范检查.py —— 按 GB 3100/3101/3102、GB/T 15834/15835 与本书 v4 须知，扫可机器判的硬伤。

用法：
  python3 工具/规范检查.py ../src/ch05_v8.md [更多文件…]
退出码 = 命中项数（0 为全过）。只读，不改文件。

查：
  U1 数值与单位贴死（2.5MeV）        U2 ppm/ppb
  U3 数值范围用短横线（5.5-6.5 MeV） U4 核素写法 U-238 / 238U（无上标）
  U5 半衰期写法 T1/2、T(1/2)         U6 ℃ 前无空格
  U7 千分撇 12,500                   U8 缺前导 0（.46）
  U9 感叹号                          U10 导语式标题（>3 次才报）
  U11 图注未被正文引用
"""
import re
import sys

CHECKS = [
    ("U1 数值贴单位", re.compile(r"\d(?:MeV|keV|GeV|eV|Bq|Gy|Sv|kg|mg|cm|mm|km|mol|Pa|kW|MW|GW|min|hr)\b")),
    ("U2 ppm/ppb", re.compile(r"\bppm\b|\bppb\b|\bpphm\b", re.I)),
    ("U4 核素写法", re.compile(r"\b(?:U|Pu|Th|Am|Cm|I|Xe|Cs|Sr|Co|Fe|Li|B|Na|Mn|Ni|Zr|Mo|Ag|Cd|In|Sn|Ba|La|Ce|Nd|Sm|Eu|Gd|Er|Hf|W|Ir|Au|Pb|Ra|Rn|Po|Bi)-\d{2,3}\b|\b\d{2,3}(?:U|Pu|Th|I|Xe|Cs|Sr|Co)\b")),
    ("U5 半衰期写法", re.compile(r"\b[tT]\s*1\s*/\s*2\b|T\s*\(1/2\)|\btau_\{?1/2")),
    ("U6 ℃ 无空格", re.compile(r"\d°C")),
    ("U7 千分撇", re.compile(r"(?<![\d.])\d{1,3}(?:,\d{3})+(?![\d])")),
    ("U8 缺前导 0", re.compile(r"(?:^|(?<=[\s（(，、。：；]))\.\d+")),
    ("U9 感叹号", re.compile(r"！")),
]

# 数值范围：短横线两侧是数，且后面紧跟单位/量词——这样才不会把 $20.872-6.673$ 这类减法当范围
RANGE = re.compile(
    r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?=(?:MeV|keV|GeV|eV|%|mm|cm|m|nm|km|K|℃|kg|g|mg|mol|Bq|Gy|Sv|MW|kW|W|V|A|T|bar|atm|MPa|kPa|s|ms|min|h|d|a|年|次|倍|个|种|万|亿))"
)
LEAD_TITLE = re.compile(r"(?m)^#{2,4}\s*它要解决[^\n]*")


def check(path):
    src = open(path, encoding="utf-8").read()
    lines = src.split("\n")
    hits = {}

    def add(k, ln, txt):
        hits.setdefault(k, []).append((ln, txt.strip()[:60]))

    for i, line in enumerate(lines, 1):
        for name, pat in CHECKS:
            for m in pat.finditer(line):
                add(name, i, m.group(0))
        for m in RANGE.finditer(line):
            add("U3 范围短横线", i, m.group(0))

    lead = LEAD_TITLE.findall(src)
    total = sum(len(v) for v in hits.values())

    print(f"\n===== {path} =====")
    if not hits and len(lead) <= 3:
        print("  ✓ 可机器判项全过")
    for k in sorted(hits):
        v = hits[k]
        print(f"  ✗ {k}: {len(v)} 处")
        for ln, t in v[:6]:
            print(f"      L{ln}: {t}")
        if len(v) > 6:
            print(f"      … 另 {len(v) - 6} 处")
    if len(lead) > 3:
        print(f"  ✗ U10 导语式标题 {len(lead)} 处（限 3）：{[x.strip('# ') for x in lead][:5]}")
        total += len(lead) - 3

    figs = re.findall(r"^!\[图\s*(\d+)-(\d+)", src, re.M)
    refs = set(re.findall(r"图\s*(\d+)-(\d+)", src))
    unref = [f"{a}-{b}" for a, b in figs if (a, b) not in refs]
    if unref:
        print(f"  ✗ U11 图无正文引用: {len(unref)} 张 {unref}")
        total += len(unref)
    return total


if __name__ == "__main__":
    n = sum(check(p) for p in sys.argv[1:])
    print(f"\n命中合计 {n}")
    sys.exit(min(n, 120))
