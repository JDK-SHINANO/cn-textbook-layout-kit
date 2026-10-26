from PIL import Image, ImageDraw

mm = 5.5  # p05.png 在 140dpi 下约 5.5 px/mm

im = Image.open("out/pages/p05.png").convert("RGB")
W, H = im.size
print("png", W, H, "px/mm≈", W / 210)

box = (int(10 * W / 210), int(55 * H / 260), int(75 * W / 210), int(95 * H / 260))
crop = im.crop(box).resize(((box[2] - box[0]) * 4, (box[3] - box[1]) * 4), Image.LANCZOS)
d = ImageDraw.Draw(crop)

# 版心左沿 22mm、正文左沿 56mm（换算到裁切图坐标并放大 4 倍）
for xmm, color, label in ((26, (220, 30, 30), "版心左沿 26mm"), (60, (30, 140, 60), "正文左沿 60mm")):
    x = (xmm * W / 210 - box[0]) * 4
    for y in range(0, crop.height, 18):
        d.line([(x, y), (x, min(y + 9, crop.height))], fill=color, width=2)
    d.text((x + 6, 6), label, fill=color)

d.text((6, crop.height - 22), "红＝版心左沿（页眉与旁注都应对齐此线）  绿＝正文列左沿", fill=(60, 60, 60))
crop.save("out/校验_副区左沿.png")
print("写出 out/校验_副区左沿.png", crop.size)
