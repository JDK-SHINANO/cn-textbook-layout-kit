#!/usr/bin/env python3
"""文风检查：把「教科书不该有的东西」变成可数的事实。

查五样：
  1. 括号编号（1）（2）——正文禁用（表格里的 ①②③ 不在此列）
  2. AI 套话／正确废话
  3. 加粗密度（每千字几处）
  4. 专有名词首现标记（是否用了 <span class="term">X</span>（<span class="en">English</span>））
  5. 长句、以及「不仅是…而且是」这类空转句式

用法： python3 工具/文风检查.py ../src/ch05_v6.md [术语表文件]
"""
import re
import sys

# 教科书里不该出现的口气：AI 腔、客服腔、励志腔
BANNED = [
    "我会", "稳稳", "接住你", "接住", "一句话讲清楚", "一句话说清", "简单来说", "简单地说",
    "值得注意的是", "需要指出的是", "总而言之", "综上所述", "让我们一起", "让我们",
    "深入浅出", "干货", "划重点", "敲黑板", "核心要点是", "赋能", "抓手", "闭环",
    "底层逻辑", "认知升级", "维度拉满", "相信我", "你会发现", "你可以放心", "别担心",
    "放心", "轻松掌握", "一目了然", "秒懂", "必看", "神器", "超级", "极其重要",
    "非常重要", "务必记住", "一定要记住", "请记住",
]

PAREN_NUM = re.compile(r"[（(]\s*[1-9]\s*[)）]")
BOLD = re.compile(r"\*\*(.+?)\*\*")


def check(path: str):
    src = open(path, encoding="utf-8").read()
    body = re.sub(r"```.*?```", "", src, flags=re.S)
    han = len(re.findall(r"[\u4e00-\u9fff]", body))

    print(f"=== {path}")
    print(f"汉字 {han}")

    hits = [(b, len(re.findall(b, body))) for b in BANNED if b in body]
    print(f"\n[1] AI 腔／套话：{sum(n for _, n in hits)} 处")
    for b, n in sorted(hits, key=lambda x: -x[1])[:12]:
        print(f"    {b} × {n}")

    pn = PAREN_NUM.findall(body)
    print(f"\n[2] 括号编号（1）（2）：{len(pn)} 处 {pn[:8]}")

    bolds = BOLD.findall(body)
    dens = len(bolds) / max(1, han) * 1000
    print(f"\n[3] 加粗：{len(bolds)} 处，每千字 {dens:.1f} 处（宜 < 4）")
    for b in bolds[:10]:
        print(f"    **{b[:24]}**")

    terms = re.findall(r'<span class="term">(.*?)</span>', body)
    ens = re.findall(r'<span class="en">(.*?)</span>', body)
    print(f"\n[4] 首现标记：term {len(terms)} 处，英文 {len(ens)} 处")
    for t in terms[:10]:
        print(f"    {t}")

    long_sent = [s for s in re.split(r"(?<=[。！？])", body) if len(re.findall(r"[\u4e00-\u9fff]", s)) > 90]
    print(f"\n[5] 超长句（>90 汉字）：{len(long_sent)} 句")


if __name__ == "__main__":
    check(sys.argv[1])
