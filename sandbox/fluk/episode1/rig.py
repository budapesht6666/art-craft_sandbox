"""Флюк из нарисованных деталей: компоновщик на Pillow + numpy.

Детали (торс, голова, лапы, хвост) — рисунки Gemini из ../gemini-fluk-art/cut/. Каждая
деталь ставится аффинно (точка крепления, поворот, масштаб, сплющивание); хвост и торс
можно гнуть сеткой (PIL MESH: каждая клетка сетки — свой четырёхугольник).
Пересчёт ресэмплинга идёт в предумноженной альфе (RGBa), чтобы не было светлой каймы.
"""
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

ART = Path(__file__).parent.parent / "art"
CUT = ART / "cut"
ROOM = ART / "sheets" / "07_room.png"


@lru_cache(maxsize=None)
def sprite(group, idx, flip=False):
    im = Image.open(CUT / group / f"{group}_{idx:02d}.png").convert("RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.convert("RGBa")


def affine(src, pivot, pos, rot=0.0, sx=1.0, sy=1.0):
    """Матрица «точка исходника -> точка кадра»: pivot исходника встаёт в pos."""
    c, s = math.cos(rot), math.sin(rot)
    A = np.array([[c * sx, -s * sy], [s * sx, c * sy]])
    t = np.array(pos) - A @ np.array(pivot)
    return A, t


def paste(canvas, src, A, t):
    """Вставить исходник в кадр по матрице (A, t)."""
    w, h = src.size
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]]) @ A.T + t
    x0, y0 = np.floor(corners.min(0)).astype(int)
    x1, y1 = np.ceil(corners.max(0)).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, canvas.width), min(y1, canvas.height)
    if x1 <= x0 or y1 <= y0:
        return
    Ai = np.linalg.inv(A)
    # PIL AFFINE: точка кадра (x, y) -> точка исходника; учитываем сдвиг окна x0, y0
    off = Ai @ (np.array([x0, y0]) - t)
    data = (Ai[0, 0], Ai[0, 1], off[0], Ai[1, 0], Ai[1, 1], off[1])
    part = src.transform((x1 - x0, y1 - y0), Image.AFFINE, data, resample=Image.BICUBIC)
    canvas.alpha_composite(part.convert("RGBA"), (x0, y0))


def place(canvas, src, pivot, pos, rot=0.0, sx=1.0, sy=1.0):
    A, t = affine(src, pivot, pos, rot, sx, sy)
    paste(canvas, src, A, t)


def warp(canvas, src, grid_dst):
    """Сеточная деформация. grid_dst[r, c] — точка кадра для узла (c, r) равномерной сетки
    исходника (r по высоте, c по ширине). Каждая клетка — два треугольника, каждый
    переносится аффинно."""
    rows, cols = grid_dst.shape[0] - 1, grid_dst.shape[1] - 1
    w, h = src.size
    xs, ys = np.linspace(0, w, cols + 1), np.linspace(0, h, rows + 1)
    lo = np.floor(grid_dst.reshape(-1, 2).min(0)).astype(int) - 2
    hi = np.ceil(grid_dst.reshape(-1, 2).max(0)).astype(int) + 2
    x0, y0 = max(lo[0], 0), max(lo[1], 0)
    x1, y1 = min(hi[0], canvas.width), min(hi[1], canvas.height)
    if x1 <= x0 or y1 <= y0:
        return
    out = Image.new("RGBa", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    for r in range(rows):
        for c in range(cols):
            tl, tr = grid_dst[r, c], grid_dst[r, c + 1]
            br, bl = grid_dst[r + 1, c + 1], grid_dst[r + 1, c]
            stl, str_ = (xs[c], ys[r]), (xs[c + 1], ys[r])
            sbr, sbl = (xs[c + 1], ys[r + 1]), (xs[c], ys[r + 1])
            for d, sp in (((tl, tr, br), (stl, str_, sbr)), ((tl, br, bl), (stl, sbr, sbl))):
                _tri(out, src, np.array(d, float) - [x0, y0], np.array(sp, float))
    canvas.alpha_composite(out.convert("RGBA"), (x0, y0))


def _tri(out, src, d, s):
    """Аффинно перенести треугольник s исходника в треугольник d (координаты out)."""
    D = np.column_stack([d[1] - d[0], d[2] - d[0]])
    S = np.column_stack([s[1] - s[0], s[2] - s[0]])
    if abs(np.linalg.det(D)) < 1e-6:
        return
    Di = np.linalg.inv(D)
    M = S @ Di                                   # кадр -> исходник
    bx0, by0 = np.floor(d.min(0)).astype(int)
    bx1, by1 = np.ceil(d.max(0)).astype(int) + 1
    bx0, by0 = max(bx0, 0), max(by0, 0)
    bx1, by1 = min(bx1, out.width), min(by1, out.height)
    if bx1 <= bx0 or by1 <= by0:
        return
    off = s[0] + M @ (np.array([bx0, by0], float) - d[0])
    patch = src.transform((bx1 - bx0, by1 - by0), Image.AFFINE,
                          (M[0, 0], M[0, 1], off[0], M[1, 0], M[1, 1], off[1]), resample=Image.BICUBIC)
    yy, xx = np.mgrid[by0:by1, bx0:bx1]
    pts = np.stack([xx + 0.5 - d[0, 0], yy + 0.5 - d[0, 1]], -1) @ Di.T   # барицентрические (u, v)
    eps = 1.0 / max(np.linalg.norm(D[:, 0]), np.linalg.norm(D[:, 1]), 1.0)  # ~пиксель запаса от щелей
    inside = (pts[..., 0] >= -eps) & (pts[..., 1] >= -eps) & (pts.sum(-1) <= 1 + eps)
    if not inside.any():
        return
    region = out.crop((bx0, by0, bx1, by1))
    region.paste(patch, (0, 0), Image.fromarray((inside * 255).astype(np.uint8)))
    out.paste(region, (bx0, by0))


def bend_grid(src, base, tip_dir_deg, curl_deg, scale, pos, n=10):
    """Сетка для изогнутой полосы (хвост): исходник вытянут от base к противоположному краю.
    Каждый срез по длине поворачивается на угол, растущий к кончику (curl_deg на кончике)."""
    w, h = src.size
    xs, ys = np.linspace(0, w, n + 1), np.linspace(0, h, n + 1)
    gx, gy = np.meshgrid(xs, ys)
    P = np.stack([gx, gy], -1) - np.array(base, float)
    L = np.max(np.linalg.norm(P.reshape(-1, 2), axis=1)) or 1
    t = np.clip(np.linalg.norm(P, axis=-1) / L, 0, 1)
    a = np.radians(tip_dir_deg) + np.radians(curl_deg) * t ** 1.5
    c, s = np.cos(a), np.sin(a)
    out = np.stack([P[..., 0] * c - P[..., 1] * s, P[..., 0] * s + P[..., 1] * c], -1) * scale
    return out + np.array(pos, float)


def extend_top(group, idx, extra):
    """Удлинить рисунок вверх, повторяя верхнюю строку (рукав уходит за край кадра)."""
    key = (group, idx, extra)
    if key not in _EXT:
        im = Image.open(CUT / group / f"{group}_{idx:02d}.png").convert("RGBA")
        a = np.asarray(im)
        rows = np.nonzero(a[..., 3].max(axis=1) > 200)[0]
        top = rows[0] + 3                       # первая строка, где рукав уже непрозрачный
        strip = np.repeat(a[top:top + 1], extra, axis=0)
        _EXT[key] = Image.fromarray(np.vstack([strip, a[top:]])).convert("RGBa")
    return _EXT[key]


_EXT = {}


def room(size=(1920, 1080)):
    return Image.open(ROOM).convert("RGBA").resize(size, Image.LANCZOS)


def ease(u, kind):
    return {"lin": u, "in": u * u, "out": 1 - (1 - u) ** 2}.get(kind, u * u * (3 - 2 * u))


class Track:
    """Ключи (кадр, значение[, переход к этому ключу: io, in, out, lin, hold])."""

    def __init__(self, *keys):
        self.k = sorted(keys, key=lambda k: k[0])

    def __call__(self, f):
        k = self.k
        if f <= k[0][0]:
            return np.array(k[0][1], float)
        for (f0, v0, *_), (f1, v1, *e) in zip(k, k[1:]):
            if f <= f1:
                if e and e[0] == "hold":
                    return np.array(v0 if f < f1 else v1, float)
                u = ease((f - f0) / (f1 - f0), e[0] if e else "io")
                return np.array(v0, float) + (np.array(v1, float) - np.array(v0, float)) * u
        return np.array(k[-1][1], float)


def pose(canvas, group, idx, foot, pos, scale=1.0, flip=False, rot=0.0, sx=1.0, sy=1.0, regions=(), n=14):
    """Целая поза-рисунок: точка foot исходника встаёт в pos кадра.
    regions — оживление участков: (опора, центр, радиус, угол в градусах). Точки у центра
    поворачиваются вокруг опоры (кивок головы, взмах хвоста), к краю влияние гаснет."""
    src = sprite(group, idx, flip)
    w = src.width
    mir = (lambda p: (w - p[0], p[1])) if flip else (lambda p: p)
    foot = mir(foot)
    if not regions:
        place(canvas, src, foot, pos, rot, scale * sx, scale * sy)
        return
    h = src.height
    gx, gy = np.meshgrid(np.linspace(0, w, n + 1), np.linspace(0, h, n + 1))
    P = np.stack([gx, gy], -1)
    for pivot, center, radius, ang in regions:
        pv, ct = np.array(mir(pivot), float), np.array(mir(center), float)
        a = math.radians(-ang if flip else ang)
        wgt = np.clip(1 - np.linalg.norm(P - ct, axis=-1) / radius, 0, 1) ** 1.5
        d = P - pv
        c, s = np.cos(a * wgt), np.sin(a * wgt)
        P = np.stack([pv[0] + d[..., 0] * c - d[..., 1] * s, pv[1] + d[..., 0] * s + d[..., 1] * c], -1)
    A, t = affine(src, foot, pos, rot, scale * sx, scale * sy)
    warp(canvas, src, P @ A.T + t)
