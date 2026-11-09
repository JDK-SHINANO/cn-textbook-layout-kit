#!/usr/bin/env bash
# build_book.sh —— 全书装配：卷首 + 17 章 + 书末《题解》 + 附录 A–E → 210×260 教材版 PDF
#
# 用法：
#   ./build_book.sh                     # 全书
#   CHAPTERS="01 02 03" ./build_book.sh # 只装前几章（调试用；末端的三份附录仍会带上）
#   OUTNAME=全书_样 ./build_book.sh
set -euo pipefail
cd "$(dirname "$0")"

BOOK="$(cd .. && pwd)"
OUT=out
NAME="${OUTNAME:-全書}"
CHAPTERS="${CHAPTERS:-01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17}"
mkdir -p "$OUT/katex/contrib" "$OUT/katex/fonts" "$OUT/图"

# 1) KaTeX 资源
K=/usr/share/javascript/katex
cp -f "$K"/katex.min.css "$OUT/katex/" 2>/dev/null || true
cp -f "$K"/katex.min.js  "$OUT/katex/" 2>/dev/null || true
cp -f "$K"/contrib/auto-render.min.js "$OUT/katex/contrib/" 2>/dev/null || \
  cp -f "$K"/contrib/auto-render.js "$OUT/katex/contrib/auto-render.min.js" 2>/dev/null || true
cp -f "$K"/fonts/* "$OUT/katex/fonts/" 2>/dev/null || true

# 2) 插图：把 图v3/chNN/*.svg 平铺进 out/图（正文引用写成 图/chNN_figK.svg）
rm -f "$OUT"/图/*.svg
for d in "$BOOK"/图v3/ch*; do
  [ -d "$d" ] || continue
  for f in "$d"/*.svg; do [ -e "$f" ] && ln -sfn "$f" "$OUT/图/$(basename "$f")"; done
done
for f in "$BOOK"/图v3/*.svg; do [ -e "$f" ] && ln -sfn "$f" "$OUT/图/$(basename "$f")"; done

# 3) 备料：逐章 → src/full_chNN.md（摘题干、解引用、图改 svg）
for CH in $CHAPTERS; do
  CH="$CH" /usr/bin/python3 - <<'PY'
import os, re
ch = os.environ["CH"]; num = str(int(ch))
BOOK = os.path.abspath("..")
src = open(f"{BOOK}/src/ch{ch}_v8.md", encoding="utf-8").read()

# 章末「动手算一算」：只留题干（详解在书末《题解》）
if "## 动手算一算" in src and "## 本章要点" in src:
    orig = open(f"{BOOK}/src/ch{ch}.md", encoding="utf-8").read()
    stems = re.findall(r"^\*\*题\s*(\d+)\*\*[\s\u3000]*(.+)$", orig, re.M)
    items = "".join(
        f'<p class="qstem"><strong>题 {num}-{k}</strong><span>{t.strip()}</span></p>\n'
        for k, (_, t) in enumerate(stems, 1))
    guide = f"## 动手算一算\n\n" + items
    i, j = src.index("## 动手算一算"), src.index("## 本章要点")
    src = src[:i] + guide + src[j:]

def ref(m):
    k = m.group(1)
    return f"第 {k} 章" if "." not in k else f"§{k}"
src = re.sub(r"\{\{ref:([\d.]+)\}\}", ref, src)
src = re.sub(r"(\]\(图/[^)]+)\.png\)", r"\1.svg)", src)
open(f"{BOOK}/版式对照_有机化学风/src/full_ch{ch}.md", "w", encoding="utf-8").write(src)
print(f"  备料 ch{ch}: {len(src)} 字符")
PY
done

# 4) 卷首
sed 's|^\\newpage$|<div class="pagebreak"></div>|' "$BOOK/src/part0_v8.md" > src/full_part0.md
sed -i 's|(图/\([^)]*\)\.png)|(图/\1.svg)|g; s|{{ref:\([0-9.]*\)}}|第 \1 章|g' src/full_part0.md

# 5) 合并成一本（先封面，再卷首；卷首开头的分页符要去掉，否则多一页空白）
: > src/book_full.md
cat >> src/book_full.md <<'HTML'
<div class="cover">
  <img class="cv-pattern" src="图/cover_pattern.png" alt="">
  <p class="cv-series">全四卷 · 本册收入前三卷 17 章</p>
  <h1 class="cv-title">从零开始的<br>核物理与核能</h1>
  <p class="cv-en">Nuclear Physics and Nuclear Energy from Scratch</p>
  <p><span class="cv-tab">第三版 v3</span></p>
  <p class="cv-foot">2026 年 10 月</p>
</div>
HTML
/usr/bin/python3 "$BOOK/工具/make_front.py"
cat "$BOOK/src/front.md" >> src/book_full.md
printf "\n\n" >> src/book_full.md
awk 'NR==1 && $0=="<div class=\"pagebreak\"></div>"{next} {print}' src/full_part0.md >> src/book_full.md
printf "\n\n" >> src/book_full.md
for CH in $CHAPTERS; do
  cat "src/full_ch${CH}.md" >> src/book_full.md
  printf "\n\n" >> src/book_full.md
done

# 6) 书末《题解》：升为一章
printf "# 题解\n\n" >> src/book_full.md
for CH in $CHAPTERS; do
  f="$BOOK/src/tijie_ch${CH}.md"
  [ -f "$f" ] && { cat "$f" >> src/book_full.md; printf "\n\n" >> src/book_full.md; }
done

# 7) 附录 A–E
for L in A B C D E; do
  f="$BOOK/src/appendix_${L}.md"
  [ -f "$f" ] || continue
  cat "$f" >> src/book_full.md
  printf "\n\n" >> src/book_full.md
done

# 8) pandoc
pandoc src/book_full.md \
  -f markdown-smart+tex_math_dollars+pipe_tables+implicit_figures \
  -t html5 --standalone \
  --template=src/template.html \
  --katex=./katex/ \
  --metadata title="从零开始的核物理与核能" \
  -o "$OUT/book_full.html"

# 9) 塑形
/usr/bin/python3 工具/shape.py "$OUT/book_full.html"

# 10) 出 PDF
BROWSER="$(find "$HOME/.cache/ms-playwright" -maxdepth 3 -name chrome -type f 2>/dev/null | head -1)"
[ -n "$BROWSER" ] || { echo "找不到 chromium"; exit 1; }
"$BROWSER" --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
      --virtual-time-budget=30000 \
      --print-to-pdf="$PWD/$OUT/book_full.pdf" "file://$PWD/$OUT/book_full.html" >/dev/null 2>&1

# 11) 页眉 / 页码 / 书签
PYMUPDF="${PYMUPDF:-python3}"
"$PYMUPDF" 工具/finish.py "$OUT/book_full.pdf" "$OUT/book_full.html"

cp -f "$OUT/book_full.pdf" "$OUT/${NAME}.pdf"
pdfinfo "$OUT/${NAME}.pdf" | grep -E "Pages|Page size"
