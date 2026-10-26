"""Vyřízne tiskovou desku z naskenovaných rytin (Rijksmuseum, CC0) a sjednotí tón.

Použití: python prepare_images.py <slozka_se_skeny> <vystup> [debug]
Skeny stáhne download_scans.py do _build/scans, výstup patří do img/.
"""
import os
import re
import sys

import cv2
import numpy as np

MAX_W = 2000
# Ruční výřezy (zlomky šířky/výšky skenu) tam, kde má rytina světlé nebe bez rámečku
MANUAL = {
    "rp208": (0.131, 0.139, 0.914, 0.901),
    "rp210": (0.075, 0.145, 0.775, 0.84),
    "rp226": (0.117, 0.138, 0.836, 0.846),
    "rp228": (0.103, 0.137, 0.816, 0.834),
    "ng22": (0.04, 0.225, 0.85, 0.75),
}


def longest_run(mask, max_gap):
    """Nejdelší úsek True hodnot, ve kterém mezery nepřesáhnou max_gap."""
    idx = np.flatnonzero(mask)
    best, start = (0, 0), idx[0]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a > max_gap:
            if a - start > best[1] - best[0]:
                best = (start, a)
            start = b
    if idx[-1] - start > best[1] - best[0]:
        best = (start, idx[-1])
    return best


def extend_to_frame(frac, a, b, win, thr=0.35):
    """Posune hranice obsahu ven k nejvzdálenější lince rámečku v okně win."""
    lo = [i for i in range(max(0, a - win), a) if frac[i] > thr]
    hi = [i for i in range(b, min(len(frac), b + win)) if frac[i] > thr]
    return (min(lo) if lo else a), (max(hi) if hi else b)


def plate_bbox(gray):
    h, w = gray.shape
    paper = np.median(gray)
    ink = gray < paper - 60
    # Jádro rytiny má v řádcích/sloupcích hodně inkoustu, okraje papíru s tužkovými čísly téměř žádný.
    rows = cv2.blur(ink.mean(1).astype(np.float32).reshape(-1, 1), (1, 9)).ravel()
    y0, y1 = longest_run(rows > 0.06, h // 60)
    cols = cv2.blur(ink[y0:y1].mean(0).astype(np.float32).reshape(1, -1), (9, 1)).ravel()
    x0, x1 = longest_run(cols > 0.06, w // 60)
    # Světlé nebe má málo inkoustu, proto ještě dohledáme tenkou linku rámečku desky.
    line = gray < paper - 35
    y0, y1 = extend_to_frame(line[:, x0:x1].mean(1), y0, y1, int(h * 0.12))
    x0, x1 = extend_to_frame(line[y0:y1].mean(0), x0, x1, int(w * 0.12))
    return x0, y0, x1 - x0, y1 - y0


def flatten(gray):
    bg = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    bg = cv2.GaussianBlur(bg, (0, 0), 30)
    norm = np.clip(gray.astype(np.float32) / np.maximum(bg.astype(np.float32), 1) * 255, 0, 255)
    lo, hi = np.percentile(norm, 3), np.percentile(norm, 88)
    norm = np.clip((norm - lo) / (hi - lo), 0, 1)
    return (norm ** 1.35 * 255).astype(np.uint8)


def duotone(gray, ink=(28, 30, 38), paper=(236, 228, 210)):
    t = gray.astype(np.float32)[..., None] / 255.0
    ink = np.array(ink[::-1], np.float32)
    paper = np.array(paper[::-1], np.float32)
    return (ink + (paper - ink) * t).astype(np.uint8)


def main(src, out, dbg=None):
    os.makedirs(out, exist_ok=True)
    if dbg:
        os.makedirs(dbg, exist_ok=True)
    for f in sorted(os.listdir(src)):
        m = re.match(r"(RP-P-OB-80\.(\d+)|NG-1979-564-(\d+))\.jpg$", f)
        if not m:
            continue
        name = f"rp{m.group(2)}" if m.group(2) else f"ng{m.group(3)}"
        img = cv2.imread(os.path.join(src, f))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if name in MANUAL:
            H, W = gray.shape
            fx0, fy0, fx1, fy1 = MANUAL[name]
            x0, y0, x1, y1 = int(fx0 * W), int(fy0 * H), int(fx1 * W), int(fy1 * H)
        else:
            x, y, bw, bh = plate_bbox(gray)
            pad = int(0.006 * max(bw, bh))
            x0, y0 = max(0, x - pad), max(0, y - pad)
            x1, y1 = min(gray.shape[1], x + bw + pad), min(gray.shape[0], y + bh + pad)
        tone = duotone(flatten(gray[y0:y1, x0:x1]))
        if tone.shape[1] > MAX_W:
            s = MAX_W / tone.shape[1]
            tone = cv2.resize(tone, (MAX_W, int(tone.shape[0] * s)), interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(out, name + ".webp"), tone,
                    [cv2.IMWRITE_WEBP_QUALITY, 72])
        if dbg:
            vis = img.copy()
            cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 0, 255), 10)
            cv2.imwrite(os.path.join(dbg, name + ".jpg"), cv2.resize(vis, (400, int(400 * vis.shape[0] / vis.shape[1]))))
        print(name, tone.shape[1], "x", tone.shape[0])


if __name__ == "__main__":
    main(*sys.argv[1:])
