#!/usr/bin/env python3
"""从书影里量版式参数：开本、版心、行距、每行字数、正文字高、强调蓝。

做法：
  1. 纸面掩膜（亮 + 低饱和）→ 成对页的纸面 bbox，用来定像素/毫米比例；
  2. 某页内的暗像素（文字）→ 行投影 → 行距、字高；列投影 → 版心宽；
  3. 蓝色像素（B 明显高于 R）→ 用纸白做白平衡 → 取中位数得强调色。

用法： python3 measure.py 图片1 [图片2 ...]
"""
import sys, glob
import numpy as np
from PIL import Image

PAGE_W_MM = 185.0   # 787×1092 1/16 开标称值，用于标定 px/mm
PAGE_H_MM = 260.0


def load(path, maxdim=2400):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = min(1.0, maxdim / max(w, h))
    if s < 1.0:
        im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def paper_mask(a):
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    mx = a.max(axis=2); mn = a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    return (lum > 150) & (sat < 0.14)


def bbox(mask, min_frac=0.02):
    ys, xs = np.where(mask)
    if len(ys) < 50:
        return None
    # 用分位数去掉零星噪点
    y0, y1 = np.percentile(ys, 0.5), np.percentile(ys, 99.5)
    x0, x1 = np.percentile(xs, 0.5), np.percentile(xs, 99.5)
    return int(x0), int(y0), int(x1), int(y1)


def runs(profile, thresh, min_len):
    """把投影里连续超过阈值的区间找出来。"""
    out, start = [], None
    for i, v in enumerate(profile):
        if v > thresh and start is None:
            start = i
        elif v <= thresh and start is not None:
            if i - start >= min_len:
                out.append((start, i))
            start = None
    if start is not None and len(profile) - start >= min_len:
        out.append((start, len(profile)))
    return out


def analyse_page(a, box, label):
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1]
    lum = sub @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    ink = lum < 110                      # 正文黑字（照片里灰度 40–100）
    # 只保留纸面内部，避开书脊阴影与背景
    pad = int(0.02 * min(sub.shape[:2]))
    ink[:pad, :] = ink[-pad:, :] = False
    ink[:, :pad] = ink[:, -pad:] = False

    # 列投影：正文栏（文字密、左对齐开始）
    colp = ink.sum(axis=0).astype(np.float32)
    colp_s = np.convolve(colp, np.ones(9) / 9, mode="same")
    thr = max(colp_s.max() * 0.06, 2)
    cols = runs(colp_s, thr, 20)
    if not cols:
        return None
    cx0 = int(np.percentile(np.nonzero(colp_s > thr)[0], 1))
    cx1 = int(np.percentile(np.nonzero(colp_s > thr)[0], 99))
    # 去掉裁切边上可能粘连的页边黑影：若区间贴边，向内收
    if cx0 < pad + 3:
        cx0 = pad + 3
    if cx1 > sub.shape[1] - pad - 3:
        cx1 = sub.shape[1] - pad - 3
    cw = cx1 - cx0

    # 行投影：正文行距
    rowp = ink[:, cx0:cx1].sum(axis=1).astype(np.float32)
    rowp_s = np.convolve(rowp, np.ones(3) / 3, mode="same")
    rthr = max(rowp_s.max() * 0.10, 2)
    lines = runs(rowp_s, rthr, 4)
    # 只取正文行（行高 8–40px），排除页眉细线与图
    heights = [(b - a_) for a_, b in lines]
    if not heights:
        return None
    med_h = float(np.median(heights))
    text_lines = [(a_, b) for a_, b in lines if 0.55 * med_h <= (b - a_) <= 1.7 * med_h]
    centers = [((a_ + b) / 2.0) for a_, b in text_lines]
    # 相邻行中心距 → 行距
    diffs = np.diff(centers)
    diffs = diffs[(diffs > 0.6 * med_h) & (diffs < 2.4 * med_h)]
    pitch = float(np.median(diffs)) if len(diffs) > 5 else float("nan")

    ry0 = text_lines[0][0] if text_lines else 0
    ry1 = text_lines[-1][1] if text_lines else 0
    return dict(label=label, box=(int(x0), int(y0), int(x1), int(y1)),
                page_w_px=float(x1 - x0), page_h_px=float(y1 - y0),
                block_w_px=float(cw), block_h_px=float(ry1 - ry0),
                col=[int(cx0), int(cx1)], row=[int(ry0), int(ry1)],
                glyph_h=med_h, pitch=pitch, n_lines=len(text_lines))


def blue_stat(a, paper_rgb):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    m = (b - r > 28) & (b > 70) & (lum > 40) & (lum < 200)
    if m.sum() < 200:
        return None, 0
    px = a[m]
    # 白平衡：纸白 → 255
    gain = 255.0 / np.maximum(paper_rgb, 1)
    px = np.clip(px * gain, 0, 255)
    med = np.median(px, axis=0).astype(int)
    return "#%02X%02X%02X" % tuple(med), int(m.sum())


def paper_white(a, mask):
    px = a[mask]
    # 取纸面最亮 2% 的中位数当白点（含高光）
    lum = px @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    top = px[lum >= np.percentile(lum, 98)]
    return np.median(top, axis=0)


def main(paths):
    rows = []
    for p in paths:
        a = load(p)
        mask = paper_mask(a)
        box = bbox(mask)
        if not box:
            print(f"{p}: 找不到纸面"); continue
        pw = box[2] - box[0]; ph = box[3] - box[1]
        # 判定是单页还是跨页：宽高比
        ratio = pw / ph
        spread = ratio > 0.95
        print(f"\n=== {p.split('/')[-1]}")
        print(f"  纸面 {pw}×{ph}px  宽高比 {ratio:.2f}  → {'跨页' if spread else '单页'}")
        # px/mm：跨页横宽 = 2 页 = 370mm；单页宽 = 185mm
        # 竖直方向一律 260mm
        mm_w = PAGE_W_MM * (2 if spread else 1)
        pxmm_w = pw / mm_w
        pxmm_h = ph / PAGE_H_MM
        print(f"  标定 px/mm: 横 {pxmm_w:.2f}  纵 {pxmm_h:.2f}")
        white = paper_white(a, mask)
        blue, nb = blue_stat(a, white)
        print(f"  纸白 RGB≈{tuple(int(v) for v in white)}   强调蓝 {blue}（{nb} px）")
        if spread:
            gx = (box[0] + box[2]) // 2
            halves = {"左页": (box[0], box[1], gx, box[3]), "右页": (gx, box[1], box[2], box[3])}
        else:
            halves = {"单页": box}
        for lab, bb in halves.items():
            r = analyse_page(a, bb, lab)
            if not r:
                print(f"    {lab}: 未测得正文"); continue
            pw_mm = r["page_w_px"] / pxmm_w
            ph_mm = r["page_h_px"] / pxmm_h
            bw_mm = r["block_w_px"] / pxmm_w
            bh_mm = r["block_h_px"] / pxmm_h
            pitch_mm = r["pitch"] / pxmm_h if r["pitch"] == r["pitch"] else float("nan")
            glyph_mm = r["glyph_h"] / pxmm_h
            # 版心相对页面的左右边距
            left_mm = r["col"][0] / pxmm_w
            right_mm = (r["page_w_px"] - r["col"][1]) / pxmm_w
            top_mm = r["row"][0] / pxmm_h
            bot_mm = (r["page_h_px"] - r["row"][1]) / pxmm_h
            print(f"    {lab}: 版心 {bw_mm:.1f}×{bh_mm:.1f} mm (测到 {r['n_lines']} 行)")
            print(f"          行距 {pitch_mm:.2f} mm = {pitch_mm*2.845:.1f} pt   字身高 {glyph_mm:.2f} mm ≈ {glyph_mm*2.845:.1f} pt")
            print(f"          边距 内 {left_mm:.1f} 外 {right_mm:.1f} 上 {top_mm:.1f} 下 {bot_mm:.1f} mm")
            if pitch_mm == pitch_mm:
                print(f"          每行约 {bw_mm / pitch_mm * 1.0:.1f} 字（按字宽=行距估）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法：python3 measure.py 书影页/*.jpg   # 从扫描页量开本、版心、行距、字高")
    main(sys.argv[1:])
