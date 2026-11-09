#!/usr/bin/env python3
"""文风检查 v2 —— 把「教科书不该有的东西」变成可数的事实。

规则取自 规范/文风病灶_ch01-09.md（R1–R15）与 ch10-17（14 条），合并去重。
分两档：
  硬门槛（不通过即退出码非零）：R1 正确废话、R2 口号营销、R3 二称闲聊、
      R4 空转过渡模板、R9 模糊量、R11 感叹号、R14 加粗密度、R15 term 标记。
  报警（只计数，人工判）：R5 导语式标题、R8 比喻词典、R10 括号编号、
      R12 强调句密度、R13 语气词、「你」频次、超长句。

用法：
  python3 工具/文风检查.py ../src/ch05_v8.md
  python3 工具/文风检查.py ../src/ch0*.md      # 多文件
"""
import re
import sys

HARD = {
    "R1 正确废话": r"请记住|值得注意|值得一提|需要注意的是|不难(发现|看出)|显而易见|众所周知|无须赘言|不再赘述",
    "R2 口号营销": r"简单来说|换句话说|说白了|说到底|一句话(讲|说|看懂|看清)|三分钟|秒懂|你只需要记住|一眼就能|白忙|白说",
    "R3 二称闲聊": r"你会发现|你以后|你要是|你若|你得|别以为|别嫌|不用怕|够你|咱们",
    "R4 空转过渡": r"让我们一起|我们来看|下面我们|接下来我们|这一节我们|于是我们得到|现在你会|顺带(?:说|算|提)|顺便(?:说|算|看)",
    "R9 模糊量": r"很多倍|非常多|大多数|绝大多数|相当(大|可观)|巨大|极大|惊人|九亿亿|万亿亿|几十亿|一大批|一大截|一大片",
}
WARN = {
    "R5 导语式标题": r"(?m)^#{2,4}\s*.*(它要解决|它要干什么|问题来了|麻烦|会怎样|怎么回事|长什么样|账本|记账|一生|三兄弟)",
    "R8 比喻词典": r"一堵墙|墙里|墙拆开|门票|过路费|钥匙|刹车|口袋|小费|中子海|乒乓球|悬崖|煤山|油门|主角|炉膛|接力|赛跑",
    "R10 括号编号": r"[（(]\s*[1-9]\s*[)）]",
    "R12 强调句": r"这就是为什么|这才是|正是因为|恰恰是|不是因为.{0,12}而是因为",
    "R13 语气词": r"[嗯呢吧啊呀嘛呗](?=[，。；！？\s]|$)",
}
BOLD = re.compile(r"\*\*(.+?)\*\*")
TERM = re.compile(r'<span class="term">(.*?)</span>')
EN = re.compile(r'<span class="en">(.*?)</span>')


def check(path):
    src = open(path, encoding="utf-8").read()
    body = re.sub(r"```.*?```", "", src, flags=re.S)
    han = len(re.findall(r"[\u4e00-\u9fff]", body))
    k = max(han, 1) / 1000

    print(f"\n===== {path} =====")
    print(f"汉字 {han}")

    hard_fail = 0
    print("\n— 硬门槛 —")
    for name, pat in HARD.items():
        hits = re.findall(pat, body)
        mark = "✓" if not hits else "✗"
        print(f"  {mark} {name}: {len(hits)} 处" + ("" if not hits else f"  {sorted(set(hits))[:6]}"))
        hard_fail += 1 if hits else 0

    bolds = [b for b in BOLD.findall(body) if b.strip() not in ("旁注", "本章要解决的问题", "这张图要读出什么", "本章要点", "本章术语", "动手算一算")]
    dens = len(bolds) / k
    ok = dens <= 4.0
    print(f"  {'✓' if ok else '✗'} R14 加粗密度: {len(bolds)} 处, {dens:.1f}/千字（限 4）")
    hard_fail += 0 if ok else 1

    terms = TERM.findall(body)
    ok = len(terms) >= 8
    print(f"  {'✓' if ok else '✗'} R15 术语首现: {len(terms)} 处（下限 8）")
    hard_fail += 0 if ok else 1

    bang = [m for m in re.findall(r"！", body)]
    ok = not bang
    print(f"  {'✓' if ok else '✗'} R11 感叹号: {len(bang)} 处（限 0，数学式内自行排除后重跑）")
    hard_fail += 0 if ok else 1

    print("\n— 报警（人工判） —")
    for name, pat in WARN.items():
        hits = re.findall(pat, body)
        if hits:
            print(f"  ! {name}: {len(hits)} 处  {sorted(set(hits))[:6]}")

    you = len(re.findall("你", body))
    print(f"  ! 「你」: {you} 处, {you / k:.1f}/千字（限 2）")
    long_sent = [s for s in re.split(r"(?<=[。！？])", body) if len(re.findall(r"[\u4e00-\u9fff]", s)) > 90]
    print(f"  ! 超长句（>90 汉字）: {len(long_sent)} 句")
    emph = len(re.findall(WARN["R12 强调句"], body))
    print(f"  ! R12 强调句密度: {emph / k:.2f}/千字（>1.5 报警）")

    print(f"\n  英文标记 {len(EN.findall(body))} 处；硬门槛不合格 {hard_fail} 项")
    return hard_fail


if __name__ == "__main__":
    bad = sum(check(p) for p in sys.argv[1:])
    sys.exit(min(bad, 120))
