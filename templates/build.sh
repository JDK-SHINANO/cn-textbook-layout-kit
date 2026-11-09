#!/usr/bin/env bash
# build.sh —— 单章样张：正文章 + 书末《题解》一章 → 210×260 教材版 PDF
#
# 用法：
#   ./build.sh                 # 默认第 4 章（ch04 + tijie.md）
#   ./build.sh ch05 ch05_v6.md tijie_ch05.md
#        章号  正文章 md       题解 md
set -euo pipefail
cd "$(dirname "$0")"

CH="${1:-ch04}"
SRC_MD="${2:-ch04.md}"
TIJIE_MD="${3:-tijie.md}"
FIGS="fig5_${CH}"
OUT=out
mkdir -p "$OUT/katex/contrib" "$OUT/katex/fonts"

# 1) KaTeX 资源
K=/usr/share/javascript/katex
cp -f "$K"/katex.min.css "$OUT/katex/" 2>/dev/null || true
cp -f "$K"/katex.min.js  "$OUT/katex/" 2>/dev/null || true
cp -f "$K"/contrib/auto-render.min.js "$OUT/katex/contrib/" 2>/dev/null || \
  cp -f "$K"/contrib/auto-render.js "$OUT/katex/contrib/auto-render.min.js" 2>/dev/null || true
cp -f "$K"/fonts/* "$OUT/katex/fonts/" 2>/dev/null || true

# 2) 插图：双色 SVG（工具/figs.py 出图，画布按版心宽校准）
[ -d "$FIGS" ] || /usr/bin/python3 工具/figs.py "$CH" >/dev/null
rm -rf src/图 out/图
ln -sfn "$(cd "$FIGS" && pwd)" src/图
ln -sfn "$(cd "$FIGS" && pwd)" out/图

# 3) 备料：解引用占位、摘章内习题、插图改 SVG
CH="$CH" SRC_PATH="../src/${SRC_MD}" /usr/bin/python3 - <<'PY'
import os, re
ch = os.environ["CH"]
num = ch[-2:].lstrip("0")
src = open(os.environ["SRC_PATH"], encoding="utf-8").read()
src = re.sub(r'^<span id="ch\d+"></span>\n', '', src)

# 章末「动手算一算」：只留题干（详解在书末题解）。题干一律从原章取，
# 免得改过文的 chXX_v6.md 里已经没有题目可选。
if "## 动手算一算" in src and "## 本章要点" in src:
    orig = f"../src/ch{int(num):02d}.md"
    try:
        otext = open(orig, encoding="utf-8").read()
    except OSError:
        otext = src
    stems = re.findall(r"^\*\*题\s*(\d+)\*\*[\s\u3000]*(.+)$", otext, re.M)
    items = "".join(
        f'<p class="qstem"><strong>题 {num}-{k}</strong><span>{t.strip()}</span></p>\n'
        for k, (_, t) in enumerate(stems, 1)
    )
    n = len(stems)
    guide = f"## 动手算一算\n\n" + items
    i, j = src.index("## 动手算一算"), src.index("## 本章要点")
    src = src[:i] + guide + src[j:]

def ref(m):
    k = m.group(1)
    return f"第 {k} 章" if "." not in k else f"§{k}"
src = re.sub(r"\{\{ref:([\d.]+)\}\}", ref, src)

# 插图改用 SVG（文字为矢量文本，插入不缩放 → 图内字号即实数）
src = re.sub(r"(\]\(图/[^)]+)\.png\)", r"\1.svg)", src)

open(f"src/{ch}.md", "w", encoding="utf-8").write(src)
print(f"备料：{ch}", len(src), "字符")
PY

# 4) 合并：正文一章 + 书末《题解》（题解自己以「# 题解」起章）
{
  cat "src/${CH}.md"
  printf "\n\n# 题解\n\n"
  cat "../src/${TIJIE_MD}"
} > src/book.md

# 5) pandoc
pandoc src/book.md \
  -f markdown-smart+tex_math_dollars+pipe_tables+implicit_figures \
  -t html5 --standalone \
  --template=src/template.html \
  --katex=./katex/ \
  --metadata title="从零开始的核物理与核能（样张·${CH}）" \
  -o "$OUT/sample.html"

# 6) 塑形
/usr/bin/python3 工具/shape.py "$OUT/sample.html"

# 7) 出 PDF
BROWSER="$(find "$HOME/.cache/ms-playwright" -maxdepth 3 -name chrome -type f 2>/dev/null | head -1)"
[ -n "$BROWSER" ] || { echo "找不到 chromium"; exit 1; }
"$BROWSER" --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
      --virtual-time-budget=20000 \
      --print-to-pdf="$PWD/$OUT/sample.pdf" "file://$PWD/$OUT/sample.html" >/dev/null 2>&1

# 8) 页眉 / 页码 / 书签
PYMUPDF="${PYMUPDF:-python3}"
"$PYMUPDF" 工具/finish.py "$OUT/sample.pdf" "$OUT/sample.html"

pdfinfo "$OUT/sample.pdf" | grep -E "Pages|Page size"
