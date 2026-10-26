#!/usr/bin/env python3
"""文风检查（中文教材）：把「教科书不该有的东西」变成可数的事实。

查五样：
  1. 正文编号：（1）（2）（3）与 ①②③ 一律禁用（表格里的圈号不算，那里是列宽算法的断行锚）
  2. AI 腔／正确废话
  3. 加粗密度（目标：每千字 < 4；版式标记 **旁注** 等也算在里面，看总量即可）
  4. 专有名词首现标记 <span class="term">X</span>（<span class="en">English</span>）
  5. 超长句（>90 汉字）

用法：python3 style_lint_cn.py 章.md [--strict]
      --strict 时有任一项不达标即 exit 1（适合放进构建闸门）。
"""
import re
import sys

# 教科书里不该出现的口气：AI 腔、客服腔、励志腔
BANNED = [
    "我会", "稳稳", "接住你", "接住", "一句话讲清楚", "一句话说清", "简单来说", "简单地说",
    "值得注意的是", "需要指出的是", "总而言之", "综上所述", "让我们一起", "让我们",
    "深入浅出", "干货", "划重点", "敲黑板", "核心要点是", "赋能", "抓手", "闭环",
    "底层逻辑", "认知升级", "相信我", "你会发现", "你可以放心", "别担心",
    "轻松掌握", "一目了然", "秒懂", "必看", "神器", "超级", "极其重要",
    "非常重要", "务必记住", "一定要记住", "请记住",
]

PAREN_NUM = re.compile(r"[（(]\s*[1-9]\s*[)）]")
CIRCLED = re.compile(r"[①②③④⑤⑥⑦⑧⑨⑩]")
BOLD = re.compile(r"\*\*(.+?)\*\*")
TERM = re.compile(r'<span class="term">(.*?)</span>')
EN = re.compile(r'<span class="en">(.*?)</span>')
HAN = re.compile(r"[\u4e00-\u9fff]")


def lint(path: str):
    src = open(path, encoding="utf-8").read()
    body = re.sub(r"```.*?```", "", src, flags=re.S)
    han = len(HAN.findall(body))

    hits = [(b, len(re.findall(b, body))) for b in BANNED if b in body]
    n_ai = sum(n for _, n in hits)
    pn = PAREN_NUM.findall(body)
    # 圈号只许在表格里：先去表格行，再数正文
    prose = "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("|"))
    circ = CIRCLED.findall(prose)
    bolds = BOLD.findall(body)
    dens = len(bolds) / max(1, han) * 1000
    terms, ens = TERM.findall(body), EN.findall(body)
    long_sent = [s for s in re.split(r"(?<=[。！？])", body)
                 if len(HAN.findall(s)) > 90]

    ok = n_ai == 0 and not pn and not circ and dens < 4 and len(terms) >= 8

    print(f"=== {path}")
    print(f"汉字 {han}")
    print(f"\n[1] AI 腔／套话：{n_ai} 处" + ("  ✓" if n_ai == 0 else "  ✗"))
    for b, n in sorted(hits, key=lambda x: -x[1])[:12]:
        print(f"    {b} × {n}")
    print(f"\n[2] 括号编号（1）（2）：{len(pn)} 处" + ("  ✓" if not pn else "  ✗") + f" {pn[:8]}")
    print(f"\n[2b] 正文圈号 ①②③：{len(circ)} 处" + ("  ✓" if not circ else "  ✗（表格里可以用）") + f" {circ[:8]}")
    print(f"\n[3] 加粗：{len(bolds)} 处，每千字 {dens:.1f} 处（宜 < 4）" + ("  ✓" if dens < 4 else "  ✗"))
    for b in bolds[:12]:
        print(f"    **{b[:24]}**")
    print(f"\n[4] 首现标记：term {len(terms)} 处，英文 {len(ens)} 处"
          + ("  ✓" if len(terms) >= 8 else "  ✗（至少 8）"))
    for t in terms[:12]:
        print(f"    {t}")
    print(f"\n[5] 超长句（>90 汉字）：{len(long_sent)} 句")
    print(f"\n结论：{'达标' if ok else '未达标'}")
    return ok


if __name__ == "__main__":
    ok = lint(sys.argv[1])
    if "--strict" in sys.argv and not ok:
        sys.exit(1)
