"""Флюк и лазерная точка: покадровая 2D-анимация кодом, Blender 5.2 + Grease Pencil.

Риг (кости, IK лап, кожа) считается здесь в 2D. Каждый рисунок пишется отдельным
кадром Grease Pencil: по двойкам, быстрые движения по единицам. Blender даёт линию,
дрожание штриха (Noise) и рендер. Тело в профиль, голова в 3/4 к зрителю, как на
фото-референсе пользователя.

blender -b --factory-startup --python-exit-code 1 -P fluk2d.py -- [--stills 1,60,98] [--out DIR]
"""
import math
import sys
from pathlib import Path

import numpy as np

FPS, LAST = 24, 216

# ---------------------------------------------------------------- геометрия

def catmull(pts, closed=False, n=10):
    """Плотная линия через контрольные точки (Катмулл — Ром)."""
    p = [np.array(q, float) for q in pts]
    if closed:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [2 * p[0] - p[1]] + p + [2 * p[-1] - p[-2]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(p[-2])
    return np.array(out)


def tube(center, widths, n=10):
    """Контур трубки вокруг осевой линии: открыт в начале (прячется в теле), круглый конец."""
    c = catmull(center, n=n)
    w = np.interp(np.linspace(0, 1, len(c)), np.linspace(0, 1, len(widths)), widths) / 2
    d = np.gradient(c, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
    left, right = c + nrm * w[:, None], c - nrm * w[:, None]
    a0 = math.atan2(nrm[-1, 1], nrm[-1, 0])
    cap = [c[-1] + w[-1] * np.array([math.cos(a0 - math.pi * k / 12), math.sin(a0 - math.pi * k / 12)])
           for k in range(1, 12)]
    return np.vstack([left, cap, right[::-1]])


def ellipse(cx, cz, rx, rz, rot=0.0, n=28):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x, z = rx * np.cos(t), rz * np.sin(t)
    c, s = math.cos(rot), math.sin(rot)
    return np.stack([cx + c * x - s * z, cz + s * x + c * z], axis=1)


def rect(x0, z0, x1, z1):
    return np.array([[x0, z0], [x1, z0], [x1, z1], [x0, z1]], float)


# ---------------------------------------------------------------- кости
# имя: (родитель, голова, хвост). Покой: кот стоит лицом вправо, земля z = 0.
BONES = {
    "hips": (None, (0.0, 1.08), (-0.75, 1.0)),
    "chest": (None, (0.0, 1.08), (0.62, 1.12)),
    "neck": ("chest", (0.62, 1.12), (0.95, 1.42)),
    "head": ("neck", (0.95, 1.42), (1.5, 1.62)),
    "ear_n": ("head", (0.98, 1.95), (0.88, 2.3)),
    "ear_f": ("head", (1.58, 1.97), (1.68, 2.3)),
    "tail1": ("hips", (-0.8, 1.05), (-1.15, 1.16)),
    "tail2": ("tail1", (-1.15, 1.16), (-1.33, 1.4)),
    "tail3": ("tail2", (-1.33, 1.4), (-1.38, 1.68)),
    "tail4": ("tail3", (-1.38, 1.68), (-1.28, 1.95)),
}
FAR = np.array([0.14, 0.05])  # дальние лапы чуть правее и выше


def leg_bones(prefix, parent, pts):
    for i in range(len(pts) - 1):
        BONES[f"{prefix}{i}"] = (parent, tuple(pts[i]), tuple(pts[i + 1]))


FRONT = [(0.56, 0.95), (0.5, 0.5), (0.57, 0.15), (0.70, 0.08)]
HIND = [(-0.52, 1.0), (-0.4, 0.58), (-0.66, 0.3), (-0.45, 0.08)]
leg_bones("fln", "chest", FRONT)
leg_bones("flf", "chest", [tuple(np.add(p, FAR)) for p in FRONT])
leg_bones("hln", "hips", HIND)
leg_bones("hlf", "hips", [tuple(np.add(p, FAR)) for p in HIND])
REST = {k: (np.array(h, float), np.array(t, float)) for k, (_, h, t) in BONES.items()}


def ang(v):
    return math.atan2(v[1], v[0])


def M(tx=0.0, tz=0.0, rot=0.0, sx=1.0, sz=1.0):
    c, s = math.cos(rot), math.sin(rot)
    return np.array([[c * sx, -s * sz, tx], [s * sx, c * sz, tz], [0, 0, 1.0]])


def T(x, z):
    return M(x, z)


def R(a):
    return M(rot=a)


def bone_matrix(h0, a0, head, a, stretch=1.0, squash=1.0):
    """Деформация кости: покой (h0, a0) -> поза (head, a) с растяжением вдоль кости."""
    return T(*head) @ R(a) @ M(sx=stretch, sz=squash) @ R(-a0) @ T(-h0[0], -h0[1])


def apply(m, p):
    return p @ m[:2, :2].T + m[:2, 2]


# ---------------------------------------------------------------- цвета и материалы
# имя: (линия или None, заливка или None, прозрачность заливки), цвета в sRGB
PALETTE = {
    "ink": ((0.13, 0.12, 0.12), (1.0, 1.0, 1.0)),
    "far": ((0.13, 0.12, 0.12), (0.88, 0.86, 0.84)),
    "line": ((0.13, 0.12, 0.12), None),
    "nose": ((0.13, 0.12, 0.12), (0.95, 0.56, 0.62)),
    "earpink": (None, (0.97, 0.74, 0.78)),
    "iris": (None, (0.67, 0.75, 0.55)),
    "pupil": (None, (0.07, 0.07, 0.08)),
    "white": (None, (1.0, 1.0, 1.0)),
    "shadow": (None, (0.0, 0.0, 0.0), 0.16),
    "laser": (None, (1.0, 0.05, 0.05)),
    "glow": (None, (1.0, 0.2, 0.2), 0.35),
    # комната
    "wall": (None, (0.73, 0.85, 0.81)),
    "stripe": (None, (0.68, 0.81, 0.77)),
    "board": ((0.13, 0.12, 0.12), (0.97, 0.95, 0.9)),
    "floor": (None, (0.82, 0.58, 0.38)),
    "plank": ((0.55, 0.36, 0.22), None),
    "rug": ((0.13, 0.12, 0.12), (0.38, 0.5, 0.74)),
    "rug2": (None, (0.93, 0.89, 0.76)),
    "sky": ((0.13, 0.12, 0.12), (0.64, 0.84, 0.96)),
    "frame": ((0.13, 0.12, 0.12), (0.98, 0.96, 0.92)),
    "curtain": ((0.13, 0.12, 0.12), (0.95, 0.72, 0.3)),
    "wood": ((0.13, 0.12, 0.12), (0.58, 0.4, 0.24)),
    "fish": ((0.13, 0.12, 0.12), (0.96, 0.6, 0.33)),
    "sofa": ((0.13, 0.12, 0.12), (0.36, 0.48, 0.72)),
    "cushion": ((0.13, 0.12, 0.12), (0.96, 0.82, 0.46)),
    "pot": ((0.13, 0.12, 0.12), (0.8, 0.45, 0.3)),
    "leaf": ((0.13, 0.12, 0.12), (0.42, 0.67, 0.36)),
}


# ---------------------------------------------------------------- рисунок кота (покой)

def parts():
    """Части кота в порядке рисования: (имя, точки, замкнута, материал, кости, толщина)."""
    body = catmull([(0.9, 0.92), (0.86, 1.27), (0.4, 1.42), (-0.3, 1.41), (-0.84, 1.28), (-1.04, 0.98),
                    (-0.92, 0.55), (-0.35, 0.42), (0.3, 0.43), (0.8, 0.58)], closed=True)
    # голова в 3/4: широкая, пухлые щёки, пушистые бакенбарды, как у кота на фото
    head = catmull([(0.74, 1.62), (0.8, 1.88), (1.0, 2.04), (1.28, 2.08), (1.55, 2.0), (1.72, 1.8), (1.78, 1.6),
                    (1.86, 1.47), (1.73, 1.4), (1.66, 1.27), (1.42, 1.16), (1.12, 1.17), (0.88, 1.25),
                    (0.74, 1.3), (0.8, 1.42), (0.7, 1.5)], closed=True)
    tail = tube([(-0.8, 1.05), (-1.15, 1.16), (-1.33, 1.4), (-1.38, 1.68), (-1.28, 1.95)],
                [0.24, 0.2, 0.18, 0.16, 0.15])
    fleg = tube(FRONT, [0.3, 0.25, 0.2, 0.18])
    hleg = tube(HIND, [0.62, 0.4, 0.21, 0.18])
    P = [("hlf", hleg + FAR, False, "far", ["hips", "hlf0", "hlf1", "hlf2"], 1.0),
         ("flf", fleg + FAR, False, "far", ["chest", "flf0", "flf1", "flf2"], 1.0),
         ("tail", tail, False, "ink", ["hips", "tail1", "tail2", "tail3", "tail4"], 1.0),
         ("body", body, True, "ink", ["hips", "chest"], 1.1),
         ("hln", hleg, False, "ink", ["hips", "hln0", "hln1", "hln2"], 1.0),
         ("fln", fleg, False, "ink", ["chest", "fln0", "fln1", "fln2"], 1.0),
         ("ear_f", catmull([(1.42, 2.02), (1.7, 2.36), (1.76, 1.86)], n=8), False, "ink", ["ear_f"], 1.0),
         ("ear_f_in", catmull([(1.5, 2.02), (1.67, 2.25), (1.69, 1.93)], closed=True, n=6), True, "earpink", ["ear_f"], 0.0),
         ("ear_n", catmull([(0.8, 1.82), (0.8, 2.38), (1.2, 2.03)], n=8), False, "ink", ["ear_n"], 1.0),
         ("ear_n_in", catmull([(0.87, 1.95), (0.86, 2.26), (1.1, 2.03)], closed=True, n=6), True, "earpink", ["ear_n"], 0.0),
         ("head", head, True, "ink", ["head"], 1.1),
         # большой круглый розовый нос, как на фото
         ("nose", catmull([(1.32, 1.575), (1.42, 1.6), (1.52, 1.575), (1.49, 1.51), (1.42, 1.485), (1.35, 1.51)],
                          closed=True, n=5), True, "nose", ["head"], 0.65),
         ("philtrum", np.array([[1.42, 1.485], [1.42, 1.445]]), False, "line", ["head"], 0.6),
         ("mouth", catmull([(1.3, 1.43), (1.36, 1.405), (1.42, 1.445), (1.48, 1.405), (1.54, 1.43)], n=4),
          False, "line", ["head"], 0.7),
         ("chin", catmull([(1.35, 1.33), (1.42, 1.31), (1.49, 1.33)], n=4), False, "line", ["head"], 0.45)]
    for i, (ex, ez) in enumerate(((0.6, 1.56), (0.58, 1.46), (0.64, 1.35))):
        P.append((f"wl{i}", catmull([(1.22, 1.47), ((1.22 + ex) / 2, (1.47 + ez) / 2 + 0.02), (ex, ez)], n=6),
                  False, "line", ["head"], 0.45))
    for i, (ex, ez) in enumerate(((2.0, 1.57), (2.02, 1.47), (1.97, 1.36))):
        P.append((f"wr{i}", catmull([(1.62, 1.47), ((1.62 + ex) / 2, (1.47 + ez) / 2 + 0.02), (ex, ez)], n=6),
                  False, "line", ["head"], 0.45))
    return P


EYES_AT = [((1.14, 1.7), 0.115, 0.084), ((1.6, 1.72), 0.095, 0.078)]  # ближний и дальний глаз


def eye(state, look):
    """Оба глаза: half — фирменные тяжёлые веки, wide, squint, closed. look: cam, right, left."""
    out = []
    for k, ((cx, cz), rx, rz) in enumerate(EYES_AT):
        if state == "closed":
            out.append((f"lash{k}", catmull([(cx - rx, cz - 0.01), (cx, cz + 0.05), (cx + rx, cz - 0.01)], n=6),
                        False, "line", ["head"], 0.95))
            continue
        if state == "wide":
            rz = rz * 1.35
        dx = {"cam": 0.0, "right": 0.45, "left": -0.45}[look] * rx
        ri = 0.68 * min(rx, rz) if state != "wide" else 0.55 * rx
        ix, iz = cx + dx, cz - (0.012 if state != "wide" else 0.0)
        pr = 0.032 if state != "wide" else 0.016
        out += [(f"eye{k}", ellipse(cx, cz, rx, rz), True, "ink", ["head"], 0.85),
                (f"iris{k}", ellipse(ix, iz, ri, ri * 1.02), True, "iris", ["head"], 0.0),
                (f"pupil{k}", ellipse(ix, iz, pr * 0.85, pr * 1.25, n=16), True, "pupil", ["head"], 0.0),
                (f"shine{k}", ellipse(ix - ri * 0.35, iz + ri * 0.4, 0.014, 0.014, n=10), True, "white", ["head"], 0.0)]
        if state in ("half", "squint"):
            level = cz + (0.004 if state == "half" else -0.03)
            s = (level - cz) / (rz * 1.04)
            t0 = math.asin(max(-0.99, min(0.99, s)))
            t = np.linspace(math.pi - t0, t0, 22)
            arc = np.stack([cx + rx * 1.06 * np.cos(t), cz + rz * 1.08 * np.sin(t)], axis=1)
            sag = catmull([arc[-1], (cx, level - 0.012), arc[0]], n=8)[1:-1]
            out.append((f"lid{k}", np.vstack([arc, sag]), True, "ink", ["head"], 0.95))
    return out


def laser(x, z):
    return [("glow", ellipse(x, z, 0.19, 0.08), True, "glow", None, 0.0),
            ("dot", ellipse(x, z, 0.07, 0.032), True, "laser", None, 0.0)]


# ---------------------------------------------------------------- комната

def room():
    """Статичный фон: (точки, замкнута, материал, толщина)."""
    W = []
    W.append((rect(-5, 0.55, 7, 5), True, "wall", 0.0))
    for x in np.arange(-4.6, 7, 0.5):  # обои в полоску
        W.append((rect(x, 0.72, x + 0.18, 5), True, "stripe", 0.0))
    W.append((rect(-5, -1, 7, 0.55), True, "floor", 0.0))
    for z, off in ((0.38, 0.0), (0.12, 0.6), (-0.2, 0.25), (-0.5, 0.85)):
        W.append((np.array([[-5, z], [7, z]]), False, "plank", 0.6))
        for x in np.arange(-4.5 + off, 7, 1.7):
            W.append((np.array([[x, z], [x - 0.05, z + (0.17 if z < 0.3 else 0.17)]]), False, "plank", 0.5))
    W.append((rect(-5, 0.55, 7, 0.72), True, "board", 0.8))
    # окно со шторами
    W.append((rect(-3.05, 1.55, -1.75, 3.65), True, "frame", 1.0))
    W.append((rect(-2.95, 1.65, -1.85, 3.55), True, "sky", 0.8))
    W.append((catmull([(-2.75, 3.0), (-2.6, 3.12), (-2.4, 3.08), (-2.25, 3.18), (-2.08, 3.04), (-2.25, 2.94),
                       (-2.55, 2.94)], closed=True, n=6), True, "white", 0.0))
    W.append((np.array([[-2.4, 1.65], [-2.4, 3.55]]), False, "line", 0.8))
    W.append((np.array([[-2.95, 2.6], [-1.85, 2.6]]), False, "line", 0.8))
    W.append((np.array([[-3.35, 3.85], [-1.45, 3.85]]), False, "wood", 1.6))
    for x0, x1, sgn in ((-3.3, -2.9, 1), (-1.9, -1.5, -1)):
        xs = (x0 + x1) / 2
        W.append((catmull([(x0, 3.85), (x1, 3.85), (x1 + 0.08 * sgn, 2.6), (x1 - 0.05 * sgn, 1.35),
                           (x0, 1.3), (x0 - 0.03, 2.6)], closed=True, n=6), True, "curtain", 0.9))
        W.append((catmull([(xs, 3.8), (xs + 0.04, 2.6), (xs, 1.4)], n=6), False, "line", 0.5))
    # картина с рыбой
    W.append((rect(0.55, 2.95, 1.6, 3.75), True, "wood", 1.0))
    W.append((rect(0.65, 3.05, 1.5, 3.65), True, "frame", 0.6))
    W.append((catmull([(0.82, 3.35), (1.05, 3.5), (1.28, 3.35), (1.05, 3.2)], closed=True, n=6), True, "fish", 0.6))
    W.append((catmull([(1.28, 3.35), (1.4, 3.46), (1.4, 3.24)], closed=True, n=3), True, "fish", 0.6))
    W.append((ellipse(0.93, 3.37, 0.018, 0.018, n=8), True, "pupil", 0.0))
    # диван справа
    W.append((catmull([(4.55, 0.6), (4.6, 1.95), (4.85, 2.05), (6.5, 2.05), (6.6, 0.6)], closed=True, n=6), True, "sofa", 1.0))
    W.append((catmull([(4.4, 0.55), (4.35, 1.35), (4.55, 1.45), (4.8, 1.35), (4.8, 0.55)], closed=True, n=6), True, "sofa", 1.0))
    W.append((catmull([(4.85, 1.2), (4.95, 1.75), (5.55, 1.8), (5.6, 1.25)], closed=True, n=6), True, "cushion", 0.9))
    W.append((rect(4.8, 0.95, 6.6, 1.2), True, "sofa", 0.9))
    # цветок в углу
    for lx, lz in ((-3.75, 2.0), (-3.35, 2.15), (-3.05, 1.9), (-3.55, 1.75), (-3.2, 1.6)):
        W.append((catmull([(-3.35, 1.2), (lx, lz), (lx + 0.12, lz - 0.05)], n=6), False, "leaf", 1.6))
        W.append((ellipse(lx + 0.05, lz - 0.02, 0.17, 0.08, math.atan2(lz - 1.2, lx + 3.35)), True, "leaf", 0.7))
    W.append((catmull([(-3.65, 1.25), (-3.05, 1.25), (-3.15, 0.75), (-3.55, 0.75)], closed=True, n=4), True, "pot", 0.9))
    # ковёр
    W.append((ellipse(2.0, 0.12, 2.3, 0.33, n=48), True, "rug", 0.9))
    W.append((ellipse(2.0, 0.12, 1.85, 0.22, n=48), True, "rug2", 0.0))
    W.append((ellipse(2.0, 0.12, 1.5, 0.15, n=48), True, "rug", 0.0))
    return W


# ---------------------------------------------------------------- кожа

def seg_dist(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)


def weights(pts, bones):
    if len(bones) == 1:
        return np.ones((len(pts), 1))
    d = np.stack([seg_dist(pts, *REST[b]) for b in bones], axis=1)
    w = 1 / (d + 0.02) ** 4
    return w / w.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------- анимация

def ease(u, kind):
    if kind == "lin":
        return u
    if kind == "in":
        return u * u
    if kind == "out":
        return 1 - (1 - u) ** 2
    return u * u * (3 - 2 * u)


class Track:
    """Ключи (кадр, значение, переход к этому ключу). Значение — число или кортеж."""

    def __init__(self, *keys):
        self.k = sorted(keys, key=lambda k: k[0])

    def __call__(self, f):
        k = self.k
        if f <= k[0][0]:
            return np.array(k[0][1], float)
        for (f0, v0, *_), (f1, v1, *e) in zip(k, k[1:]):
            if f <= f1:
                u = ease((f - f0) / (f1 - f0), e[0] if e else "io")
                return np.array(v0, float) + (np.array(v1, float) - np.array(v0, float)) * u
        return np.array(k[-1][1], float)


def D(a):
    return math.radians(a)


FN0 = (0.70, 0.08)            # точки лап в покое
FF0 = tuple(np.add(FN0, FAR))
HN0 = (-0.45, 0.08)
HF0 = tuple(np.add(HN0, FAR))
DOT = (3.3, 0.06)

# Раскадровка, 24 к/с. root: смещение всего кота, его поворот у земли и масштаб (сплющивание).
A = {
    "root": Track((0, (0, 0)), (34, (0, 0)), (54, (-0.05, -0.3)), (84, (-0.05, -0.3)), (92, (-0.18, -0.42), "out"),
                  (98, (1.25, 0.55), "out"), (104, (2.55, -0.08), "in"), (108, (2.55, -0.18), "out"),
                  (116, (2.55, 0.0)), (140, (2.55, 0.0)), (150, (2.5, 0.04)), (LAST, (2.5, 0.04))),
    "rot": Track((0, 0), (92, D(-2)), (96, D(9)), (101, D(-6)), (104, D(-9)), (110, D(2)), (116, 0), (LAST, 0)),
    "scale": Track((0, (1, 1)), (88, (1, 1)), (92, (1.06, 0.9)), (95, (1.16, 0.88)), (101, (1.1, 0.94)),
                   (104, (1.0, 1.0)), (106, (1.1, 0.84), "out"), (112, (0.98, 1.03)), (118, (1, 1)),
                   (188, (1, 1)), (191, (0.95, 1.1), "out"), (197, (1.0, 1.03)), (LAST, (1.0, 1.03))),
    "hips": Track((0, 0), (40, 0), (54, D(-8)), (92, D(-10)), (96, D(6)), (104, D(-2)), (116, 0), (LAST, 0)),
    "chest": Track((0, 0), (40, 0), (54, D(-6)), (92, D(-8)), (96, D(4)), (106, D(-8)), (116, 0), (150, D(-6)),
                   (176, D(2)), (LAST, D(2))),
    "stretch": Track((0, 1.0), (92, 0.95), (95, 1.22), (102, 1.12), (106, 0.92), (114, 1.0)),
    "neck": Track((0, 0), (20, 0), (30, D(-8)), (54, D(-14)), (92, D(-12)), (98, D(-2)), (104, D(-14)),
                  (118, D(-4)), (140, D(-4)), (150, D(-18)), (158, D(-6)), (170, D(4)), (190, D(4)), (194, D(10)),
                  (LAST, D(8))),
    "head": Track((0, D(9)), (20, D(9)), (30, D(-6)), (54, D(-4)), (104, D(-6)), (118, D(10)), (140, D(10)),
                  (150, D(-8)), (158, D(-2)), (170, D(-8)), (182, D(-8)), (188, D(6)), (194, D(2)), (LAST, D(2))),
    # уши: плюс — вперёд, «на стрёме»; минус — прижаты
    "ears": Track((0, 0), (14, 0), (15, D(-25)), (17, 0), (19, D(-15)), (21, 0), (28, D(10)), (92, D(10)),
                  (96, D(-30)), (104, D(-30)), (112, 0), (160, 0), (166, D(-14)), (188, D(-14)), (191, D(-34)),
                  (LAST, D(-34))),
    "tail": Track((0, (0.0, 1.0)), (40, (0.0, 1.0)), (54, (D(-40), 0.4)), (92, (D(-45), 0.3)), (96, (D(25), 0.2)),
                  (110, (D(10), 0.5)), (130, (D(30), 1.2)), (176, (D(20), 1.0)), (190, (D(20), 1.0)),
                  (193, (D(45), 0.2)), (LAST, (D(40), 0.3))),
    "tail_amp": Track((0, D(6)), (40, D(6)), (54, D(3)), (60, D(10)), (88, D(10)), (92, D(2)), (130, D(8)),
                      (188, D(8)), (191, D(3)), (LAST, D(3))),
    "wiggle": Track((0, 0), (56, 0), (60, 1), (86, 1), (90, 0)),
    "fln": Track((0, FN0), (92, FN0), (95, (0.95, 0.35), "out"), (100, (2.5, 0.75)), (104, (3.25, 0.12), "in"),
                 (108, (3.32, 0.08)), (140, (3.32, 0.08)), (148, (3.18, 0.42), "out"), (160, (3.2, 0.4)),
                 (170, (3.3, 0.1)), (LAST, (3.3, 0.1))),
    "flf": Track((0, FF0), (92, FF0), (95, (1.0, 0.45), "out"), (100, (2.55, 0.85)), (104, (3.12, 0.2), "in"),
                 (108, (3.2, 0.13)), (LAST, (3.2, 0.13))),
    "hln": Track((0, HN0), (92, HN0), (96, (-0.75, 0.1), "out"), (101, (0.2, 0.25)), (106, (1.75, 0.12), "in"),
                 (110, (2.0, 0.08)), (LAST, (2.0, 0.08))),
    "hlf": Track((0, HF0), (92, HF0), (96, (-0.62, 0.15), "out"), (101, (0.35, 0.3)), (106, (1.9, 0.17), "in"),
                 (110, (2.14, 0.13)), (LAST, (2.14, 0.13))),
    # камера: центр кадра (x, z) и ширина кадра
    "cam": Track((0, (1.0, 2.0, 9.0)), (176, (1.0, 2.0, 9.0)), (198, (3.3, 1.75, 6.2)), (LAST, (3.35, 1.75, 6.0))),
}
EYES = [(0, "half"), (20, "closed"), (22, "half"), (26, "wide"), (88, "squint"), (96, "wide"), (114, "closed"),
        (146, "wide"), (160, "half"), (170, "closed"), (172, "half"), (191, "wide")]
LOOK = [(0, "cam"), (18, "right"), (158, "cam"), (182, "left")]
DOT_ON = [(0, False), (12, True), (104, False), (174, True)]


def at(seq, f):
    v = seq[0][1]
    for f0, s in seq:
        if f >= f0:
            v = s
    return v


def ik(s, t, l1, l2, sign):
    """Два звена от s к t. Если не достаёт — кости вытягиваются (по-мультяшному)."""
    d = np.linalg.norm(t - s)
    k = max(1.0, d / (l1 + l2) * 1.0001)
    l1, l2 = l1 * k, l2 * k
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    u = (t - s) / d
    return s + u * a + sign * h * np.array([-u[1], u[0]]), k


def leg_sign(name):
    s, j, t = REST[name + "0"][0], REST[name + "0"][1], REST[name + "1"][1]
    c = (t - s)[0] * (j - s)[1] - (t - s)[1] * (j - s)[0]
    return 1.0 if c > 0 else -1.0


SIGNS = {n: leg_sign(n) for n in ("fln", "flf", "hln", "hlf")}


def pose(f):
    """Матрицы деформации всех костей в кадре f."""
    rx, rz = A["root"](f)
    sx, sz = A["scale"](f)
    G = M(rx, rz, float(A["rot"](f)), sx, sz)
    L = {}
    st = float(A["stretch"](f))
    t = f / FPS
    wig = float(A["wiggle"](f))
    for b in ("hips", "chest"):
        h0, t0 = REST[b]
        rot = float(A[b](f)) + (wig * D(5) * math.sin(2 * math.pi * 3 * t) if b == "hips" else 0)
        L[b] = bone_matrix(h0, ang(t0 - h0), h0, ang(t0 - h0) + rot, st, 1 / math.sqrt(st))
    tail_base, curl = A["tail"](f)
    amp = float(A["tail_amp"](f))
    ears = float(A["ears"](f))
    local = {"neck": float(A["neck"](f)), "head": float(A["head"](f)), "ear_n": -ears, "ear_f": ears * 0.8}
    for i in range(1, 5):
        sway = amp * math.sin(2 * math.pi * 0.6 * (t - i * 0.12)) + wig * D(14) * math.sin(2 * math.pi * 3 * (t - i * 0.05))
        local[f"tail{i}"] = (tail_base if i == 1 else 0) + D(-12) * (curl - 1) * (i - 1) / 3 + sway
    for b in ("neck", "head", "ear_n", "ear_f", "tail1", "tail2", "tail3", "tail4"):
        parent = BONES[b][0]
        h0, t0 = REST[b]
        ph0, pt0 = REST[parent]
        pm = L[parent]
        pa = ang(apply(pm, pt0) - apply(pm, ph0)) - ang(pt0 - ph0)  # поворот родителя
        L[b] = bone_matrix(h0, ang(t0 - h0), apply(pm, h0), ang(t0 - h0) + pa + local[b])
    W = {b: G @ m for b, m in L.items()}
    for leg in ("fln", "flf", "hln", "hlf"):  # лапы: IK в мировых координатах
        parent = BONES[leg + "0"][0]
        h0, j0, w0, p0 = REST[leg + "0"][0], REST[leg + "0"][1], REST[leg + "1"][1], REST[leg + "2"][1]
        shoulder = apply(W[parent], h0)
        paw = A[leg](f)
        wrist = paw - (p0 - w0)
        j, _ = ik(shoulder, wrist, np.linalg.norm(j0 - h0), np.linalg.norm(w0 - j0), SIGNS[leg])
        for i, (a, b, ra, rb) in enumerate(((shoulder, j, h0, j0), (j, wrist, j0, w0), (wrist, paw, w0, p0))):
            W[f"{leg}{i}"] = bone_matrix(ra, ang(rb - ra), a, ang(b - a), np.linalg.norm(b - a) / np.linalg.norm(rb - ra))
    return W


# ---------------------------------------------------------------- Blender

def srgb(c):
    return tuple(x ** 2.2 for x in c)


def build(stills=None):
    import bpy
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, LAST
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.engine = "BLENDER_EEVEE"
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("paper")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb((0.73, 0.85, 0.81)), 1)

    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new("cam", cam_data)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam
    for f in range(1, LAST + 1):  # камера по ключам из раскадровки, каждый кадр
        x, z, w = A["cam"](f)
        cam.location = (float(x), -10, float(z))
        cam_data.ortho_scale = float(w)
        cam.keyframe_insert("location", frame=f)
        cam_data.keyframe_insert("ortho_scale", frame=f)

    mats = {}
    for name, spec in PALETTE.items():
        stroke, fill = spec[0], spec[1]
        alpha = spec[2] if len(spec) > 2 else 1.0
        m = bpy.data.materials.new(name)
        bpy.data.materials.create_gpencil_data(m)
        g = m.grease_pencil
        g.show_stroke = stroke is not None
        g.show_fill = fill is not None
        g.color = (*srgb(stroke), 1) if stroke else (0, 0, 0, 0)
        if fill:
            g.fill_color = (*srgb(fill), alpha)
        mats[name] = m

    def gp_object(name, depth, boil):
        gp = bpy.data.grease_pencils.new(name)
        ob = bpy.data.objects.new(name, gp)
        ob.rotation_euler = (math.pi / 2, 0, 0)  # рисуем в XY объекта, Y смотрит вверх
        ob.location = (0, depth, 0)
        sc.collection.objects.link(ob)
        for m in mats.values():
            gp.materials.append(m)
        layer = gp.layers.new("ink")
        layer.use_lights = False  # плоские цвета, без освещения сцены
        noise = ob.modifiers.new("boil", "GREASE_PENCIL_NOISE")
        noise.factor, noise.factor_thickness, noise.noise_scale = boil, 0.25, 0.6
        noise.use_random, noise.step, noise.seed = True, 2, 3
        return layer

    index = {n: i for i, n in enumerate(mats)}

    def radius(n, closed, thick, seed):
        r = np.full(n, 0.013 * thick)
        r *= 1 + 0.18 * np.sin(np.linspace(0, 6.0, n) + seed)  # живой нажим
        if not closed:
            r *= np.clip(np.minimum(np.arange(n), np.arange(n)[::-1]) / 6, 0.25, 1)  # сход на нет
        return r

    def draw(layer, frame, items):
        d = layer.frames.new(frame).drawing
        d.add_strokes([len(p) for p, *_ in items])
        for si, (pts, closed, mat, th) in enumerate(items):
            s = d.strokes[si]
            s.material_index = index[mat]
            s.cyclic = closed
            s.fill_id = si + 1  # Blender 5.2: с fill_id = 0 заливка не рисуется
            rad = radius(len(pts), closed, th, si * 1.7) if th > 0 else np.full(len(pts), 0.001)
            for pi, (p, r) in enumerate(zip(pts, rad)):
                s.points[pi].position = (float(p[0]), float(p[1]), 0.0)
                s.points[pi].radius = float(r)
        d.tag_positions_changed()

    draw(gp_object("room", 2.0, 0.008), 1, room())
    cat = gp_object("fluk", 0.0, 0.012)
    rest_parts = parts()
    cache = {}

    def skin(key, pts, bones, W):
        if key not in cache:
            cache[key] = weights(pts, bones)
        w = cache[key]
        return sum(w[:, i:i + 1] * apply(W[b], pts) for i, b in enumerate(bones))

    frames = [f for f in range(1, LAST + 1) if f % 2 == 1 or 86 <= f <= 116 or 188 <= f <= 196]
    if stills:
        frames = sorted(set(stills))
    for f in frames:
        W = pose(f)
        rx, rz = A["root"](f)
        items = [(ellipse(rx + 0.05, 0.02, 1.05 * (1 - 0.3 * min(max(0.0, rz), 1)), 0.09), True, "shadow", 0.0)]
        dot_on = at(DOT_ON, f)
        if dot_on and f < 174:
            wob = 0.04 * math.sin(f * 0.9) * (1 if f < 54 else 0.3)
            items += [(p, c, m, th) for _, p, c, m, _, th in laser(DOT[0] + wob, DOT[1])]
        for name, pts, closed, m, bones, th in rest_parts:
            items.append((skin(name, pts, bones, W), closed, m, th))
            if name == "head":
                st, lk = at(EYES, f), at(LOOK, f)
                for en, ep, ec, em, eb, eth in eye(st, lk):
                    items.append((skin(en + st + lk, ep, eb, W), ec, em, eth))
        if dot_on and f >= 174:  # точка у него на спине
            back = apply(W["hips"], np.array([[-0.3, 1.4]]))[0]
            items += [(p, c, m, th) for _, p, c, m, _, th in laser(*back)]
        draw(cat, f, items)
    return sc


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    stills = [int(x) for x in argv[argv.index("--stills") + 1].split(",")] if "--stills" in argv else None
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path(__file__).parent / "out"
    import bpy
    sc = build(stills)
    out.mkdir(parents=True, exist_ok=True)
    if stills:
        for f in stills:
            sc.frame_set(f)
            sc.render.filepath = str(out / f"still_{f:03d}.png")
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).parent / "fluk2d.blend"))
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = str(out / "frames" / "f_")
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
