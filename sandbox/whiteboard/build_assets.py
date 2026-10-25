"""Режет три кадра вайтборд-ролика на отдельные элементы для EffectCraft.

Запуск: python sandbox/whiteboard/build_assets.py <папка с кадрами>
Результат: sandbox/whiteboard/assets/ — bg.png, <элемент>.png (цвет) и
<элемент>_lines.png (только тёмный контур), elements.json с рамками и debug.png.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = Path(sys.argv[1])
OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

F1 = np.asarray(Image.open(SRC / "videoframe_75746.png").convert("RGB")).astype(np.float32)
F2 = np.asarray(Image.open(SRC / "videoframe_78938.png").convert("RGB")).astype(np.float32)
F3 = np.asarray(Image.open(SRC / "videoframe_85862.png").convert("RGB")).astype(np.float32)
H, W, _ = F1.shape


def fit_background(img, deg=4, iters=6):
    """Гладкий фон: полином по (x, y), подогнанный по пикселям, похожим на фон."""
    step = 8
    ys, xs = np.mgrid[0:H:step, 0:W:step]
    sample = img[::step, ::step]
    x = xs.ravel() / W - 0.5
    y = ys.ravel() / H - 0.5
    terms = [x**i * y**j for i in range(deg + 1) for j in range(deg + 1 - i)]
    A = np.stack(terms, 1)
    vals = sample.reshape(-1, 3)
    sat = vals.max(1) - vals.min(1)
    keep = sat < 12
    for _ in range(iters):
        coef, *_ = np.linalg.lstsq(A[keep], vals[keep], rcond=None)
        resid = np.abs(A @ coef - vals).max(1)
        keep = (resid < 6) & (sat < 12)
    fy, fx = np.mgrid[0:H, 0:W]
    fx = fx.ravel() / W - 0.5
    fy = fy.ravel() / H - 0.5
    full = np.stack([fx**i * fy**j for i in range(deg + 1) for j in range(deg + 1 - i)], 1)
    return (full @ coef).reshape(H, W, 3)


BG = fit_background(F1)
Image.fromarray(np.clip(BG, 0, 255).astype(np.uint8)).save(OUT / "bg.png")


def clean(mask, open_px=1):
    if open_px:
        mask = ndimage.binary_opening(mask, iterations=open_px)
    return mask


content1 = clean(np.abs(F1 - BG).max(2) > 14)
diff12 = clean(np.abs(F2 - F1).max(2) > 28)
diff23 = clean(np.abs(F3 - F2).max(2) > 28)
red1 = (F1[..., 0] - F1[..., 1] > 60) & (F1[..., 0] > 120)
# Светлые края красного крестика тоже его, иначе они проступят в слое рамки раньше времени.
red1 = ndimage.binary_dilation(red1, iterations=4) & content1

# Элементы в порядке «кто первым забирает пиксели». source: из какого кадра брать цвет,
# mask: какая маска содержимого, rects: рамки (x0, y0, x1, y1).
ELEMENTS = [
    dict(name="x_mark", source=F1, mask=red1, rects=[(1685, 340, 1860, 495)]),
    dict(name="bubbles_crowd", source=F1, mask=content1, rects=[(1220, 635, 1272, 772)]),
    dict(name="arrow", source=F1, mask=content1, rects=[(935, 622, 1215, 735), (906, 626, 935, 656)]),
    dict(name="buy_icon", source=F1, mask=content1, rects=[(998, 193, 1196, 382)], fill=True),
    dict(name="buy_label", source=F1, mask=content1, rects=[(1068, 384, 1168, 442)]),
    dict(name="wait_icon", source=F1, mask=content1, rects=[(1283, 203, 1492, 368)], fill=True),
    dict(name="wait_label", source=F1, mask=content1, rects=[(1333, 384, 1462, 437)]),
    dict(name="sell_icon", source=F1, mask=content1, rects=[(1588, 208, 1768, 378)], fill=True),
    dict(name="sell_label", source=F1, mask=content1, rects=[(1628, 380, 1722, 437)]),
    dict(name="box", source=F1, mask=content1, rects=[(975, 180, 1800, 452)]),
    dict(name="underline", source=F1, mask=content1, rects=[(1115, 462, 1665, 488)]),
    dict(name="text1", source=F1, mask=content1, rects=[(1090, 488, 1690, 558)]),
    dict(name="text2", source=F1, mask=content1, rects=[(1130, 560, 1650, 632)]),
    dict(name="crowd", source=F1, mask=content1, rects=[(1160, 645, 1595, 1015)], fill=True),
    dict(name="turtle", source=F1, mask=content1, rects=[(445, 435, 935, 970)], fill=True),
    dict(name="title", source=F1, mask=content1, rects=[(80, 55, 848, 138)]),
    # Добавилось во втором кадре
    dict(name="warning", source=F2, mask=diff12, rects=[(938, 140, 1075, 272)], fill=True),
    dict(name="bubbles_turtle", source=F2, mask=diff12, rects=[(515, 330, 585, 468)]),
    dict(name="say1", source=F2, mask=diff12, rects=[(205, 275, 718, 338)]),
    # Добавилось в третьем кадре
    dict(name="say2", source=F3, mask=diff23, rects=[(712, 275, 900, 338)]),
    dict(name="galaxy", source=F3, mask=diff23, rects=[(85, 325, 460, 568)], fill=True),
    dict(name="galaxy_label", source=F3, mask=diff23, rects=[(165, 570, 385, 618)]),
]

claimed = np.zeros((H, W), bool)
debug = (F3 * 0.35 + 160).astype(np.uint8)
rng = np.random.default_rng(7)
meta = []

for el in ELEMENTS:
    region = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in el["rects"]:
        region[y0:y1, x0:x1] = True
    own = el["mask"] & region & ~claimed
    if el.get("fill"):
        # Светлые места внутри сплошного объекта (блики, белки глаз) тоже его часть.
        own = ndimage.binary_fill_holes(ndimage.binary_closing(own, iterations=2)) & region & ~claimed
    claimed |= own
    el["region"], el["own"] = region, own

for el in ELEMENTS:
    region, own = el["region"], el["own"]
    ys, xs = np.nonzero(own)
    if len(xs) == 0:
        print("пусто:", el["name"])
        continue
    pad = 6
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, W)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, H)

    # Альфа: маска элемента, чуть расширенная и размытая. Цвет берём из кадра как есть:
    # вокруг элемента там фон, совпадающий с bg.png, поэтому шва не видно.
    # Расширяем только на фон: на пиксели соседних элементов не заходим.
    grown = ndimage.binary_dilation(own, iterations=3) & region & ~(claimed & ~own)
    alpha = ndimage.gaussian_filter(grown.astype(np.float32), 1.2)
    alpha = np.clip(alpha * 1.4, 0, 1)
    src = el["source"]
    rgba = np.dstack([src, alpha * 255])[y0:y1, x0:x1]
    Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA").save(OUT / f"{el['name']}.png")

    # Контур: только тёмные пиксели элемента, в чёрном цвете.
    lum = src @ np.array([0.299, 0.587, 0.114], np.float32)
    dark = own & (lum < 95)
    la = ndimage.gaussian_filter(ndimage.binary_dilation(dark, iterations=1).astype(np.float32), 0.8)
    la = np.clip(la * 1.5, 0, 1)
    lines = np.dstack([np.full((H, W, 3), 30, np.float32), la * 255])[y0:y1, x0:x1]
    Image.fromarray(np.clip(lines, 0, 255).astype(np.uint8), "RGBA").save(OUT / f"{el['name']}_lines.png")

    meta.append(dict(name=el["name"], x=int(x0), y=int(y0), w=int(x1 - x0), h=int(y1 - y0),
                     darkShare=round(float(dark.sum() / own.sum()), 3)))
    color = rng.integers(40, 255, 3)
    debug[own] = color

(OUT / "elements.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
Image.fromarray(debug).save(OUT / "debug.png")
print(json.dumps(meta, ensure_ascii=False))
