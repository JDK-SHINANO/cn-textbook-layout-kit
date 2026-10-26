import pymupdf
d = pymupdf.open("out/sample.pdf")
for i, p in enumerate(d):
    p.get_pixmap(dpi=140).save(f"out/pages/p{i+1:02d}.png")
t = [p.get_text() for p in d]
print("表页:", [i+1 for i, x in enumerate(t) if "表 4-1" in x])
print("总页:", d.page_count)
