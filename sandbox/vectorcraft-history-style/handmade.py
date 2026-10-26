"""«Рукотворный» вид векторного кадра: линии чуть дрожат, бумага с зерном, лёгкая виньетка.

python handmade.py in.png out.png [--wobble 1.6] [--grain 7]
"""
import argparse

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--wobble", type=float, default=1.6, help="размах дрожания линий, px")
ap.add_argument("--grain", type=float, default=7, help="сила зерна, уровни яркости")
ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args()

rng = np.random.default_rng(a.seed)
img = np.asarray(Image.open(a.src).convert("RGB")).astype(np.float32)
h, w, _ = img.shape


def smooth_noise(sigma):
    n = gaussian_filter(rng.standard_normal((h, w)), sigma)
    return n / (np.abs(n).max() + 1e-6)


# Дрожание: плавное поле смещений (крупная волна + мелкая) — линия гуляет, как от руки
dx = smooth_noise(18) * a.wobble + smooth_noise(5) * a.wobble * 0.35
dy = smooth_noise(18) * a.wobble + smooth_noise(5) * a.wobble * 0.35
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
out = np.stack([map_coordinates(img[..., c], [yy + dy, xx + dx], order=1, mode="nearest") for c in range(3)], -1)

# Бумага: крупные пятна + мелкое зерно, сильнее на светлом
paper = gaussian_filter(rng.standard_normal((h, w)), 40) * 18 + rng.standard_normal((h, w)) * a.grain
light = out.mean(-1, keepdims=True) / 255
out = out + (paper[..., None] * (0.35 + 0.65 * light))

# Виньетка
r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
out *= (1 - 0.18 * np.clip(r - 0.55, 0, None) ** 1.5)[..., None]

Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a.dst)
print(a.dst, w, "x", h)
