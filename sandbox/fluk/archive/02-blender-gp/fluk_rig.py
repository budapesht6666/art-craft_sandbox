"""Флюк: общий модуль для серий. Персонаж, риг, ходьба, глаза, комната, сборка в Blender.

Серия — отдельный скрипт с раскадровкой (см. ep01_cucumber.py): он задаёт дорожки
ключей, глаза, рот, реквизит и вызывает run(). Blender 5.2 + Grease Pencil.
"""
import math
import sys
from pathlib import Path

import numpy as np

FPS = 24

# ---------------------------------------------------------------- геометрия

def catmull(pts, closed=False, n=10):
    p = [np.array(q, float) for q in pts]
    p = ([p[-1]] + p + [p[0], p[1]]) if closed else ([2 * p[0] - p[1]] + p + [2 * p[-1] - p[-2]])
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
    """Контур трубки вокруг осевой линии: открыт в начале, круглый конец."""
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


def ellipse(cx, cz, rx, rz, rot=0.0, n=32):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x, z = rx * np.cos(t), rz * np.sin(t)
    c, s = math.cos(rot), math.sin(rot)
    return np.stack([cx + c * x - s * z, cz + s * x + c * z], axis=1)


def rect(x0, z0, x1, z1):
    return np.array([[x0, z0], [x1, z0], [x1, z1], [x0, z1]], float)


def transform(pts, x=0.0, z=0.0, rot=0.0, s=1.0):
    c, sn = math.cos(rot), math.sin(rot)
    p = np.asarray(pts, float) * s
    return np.stack([p[:, 0] * c - p[:, 1] * sn + x, p[:, 0] * sn + p[:, 1] * c + z], axis=1)


# ---------------------------------------------------------------- кости
BONES = {
    "hips": (None, (0.0, 1.08), (-0.75, 1.0)),
    "chest": (None, (0.0, 1.08), (0.62, 1.12)),
    "neck": ("chest", (0.62, 1.12), (0.95, 1.42)),
    "head": ("neck", (0.95, 1.42), (1.5, 1.62)),
    "ear_n": ("head", (0.86, 2.12), (0.68, 2.48)),
    "ear_f": ("head", (1.62, 2.14), (1.8, 2.46)),
    "tail1": ("hips", (-0.78, 1.05), (-1.13, 1.16)),
    "tail2": ("tail1", (-1.13, 1.16), (-1.31, 1.4)),
    "tail3": ("tail2", (-1.31, 1.4), (-1.36, 1.68)),
    "tail4": ("tail3", (-1.36, 1.68), (-1.26, 1.95)),
}
FAR = np.array([0.14, 0.05])
FRONT = [(0.52, 0.95), (0.48, 0.5), (0.55, 0.15), (0.68, 0.09)]
HIND = [(-0.5, 1.0), (-0.38, 0.58), (-0.62, 0.3), (-0.42, 0.09)]
LEGS = ("hln", "fln", "hlf", "flf")


def _leg_bones(prefix, parent, pts):
    for i in range(len(pts) - 1):
        BONES[f"{prefix}{i}"] = (parent, tuple(pts[i]), tuple(pts[i + 1]))


_leg_bones("fln", "chest", FRONT)
_leg_bones("flf", "chest", [tuple(np.add(p, FAR)) for p in FRONT])
_leg_bones("hln", "hips", HIND)
_leg_bones("hlf", "hips", [tuple(np.add(p, FAR)) for p in HIND])
REST = {k: (np.array(h, float), np.array(t, float)) for k, (_, h, t) in BONES.items()}
PAW0 = {leg: REST[leg + "2"][1].copy() for leg in LEGS}   # точки лап в покое (у пола)


def ang(v):
    return math.atan2(v[1], v[0])


def M(tx=0.0, tz=0.0, rot=0.0, sx=1.0, sz=1.0):
    c, s = math.cos(rot), math.sin(rot)
    return np.array([[c * sx, -s * sz, tx], [s * sx, c * sz, tz], [0, 0, 1.0]])


def bone_matrix(h0, a0, head, a, stretch=1.0, squash=1.0):
    return M(*head) @ M(rot=a) @ M(sx=stretch, sz=squash) @ M(rot=-a0) @ M(-h0[0], -h0[1])


def apply(m, p):
    return np.asarray(p, float) @ m[:2, :2].T + m[:2, 2]


def D(a):
    return math.radians(a)


# ---------------------------------------------------------------- цвета (sRGB)
INKC = (0.15, 0.13, 0.14)
PALETTE = {
    "ink": (INKC, (1.0, 1.0, 1.0)),
    "far": (INKC, (0.88, 0.87, 0.86)),
    "line": (INKC, None),
    "nose": (INKC, (0.96, 0.58, 0.64)),
    "earpink": (None, (0.98, 0.76, 0.8)),
    "blush": (None, (1.0, 0.6, 0.66), 0.45),
    "iris": (None, (0.6, 0.76, 0.5)),
    "pupil": (None, (0.1, 0.09, 0.1)),
    "white": (None, (1.0, 1.0, 1.0)),
    "mouthin": (INKC, (0.78, 0.33, 0.4)),
    "shadow": (None, (0.0, 0.0, 0.0), 0.16),
    "laser": (None, (1.0, 0.05, 0.05)),
    "glow": (None, (1.0, 0.2, 0.2), 0.35),
    "wall": (None, (0.73, 0.85, 0.81)),
    "stripe": (None, (0.68, 0.81, 0.77)),
    "board": (INKC, (0.97, 0.95, 0.9)),
    "floor": (None, (0.82, 0.58, 0.38)),
    "plank": ((0.55, 0.36, 0.22), None),
    "rug": (INKC, (0.38, 0.5, 0.74)),
    "rug2": (None, (0.93, 0.89, 0.76)),
    "sky": (INKC, (0.64, 0.84, 0.96)),
    "frame": (INKC, (0.98, 0.96, 0.92)),
    "curtain": (INKC, (0.95, 0.72, 0.3)),
    "wood": (INKC, (0.58, 0.4, 0.24)),
    "fish": (INKC, (0.96, 0.6, 0.33)),
    "sofa": (INKC, (0.36, 0.48, 0.72)),
    "cushion": (INKC, (0.96, 0.82, 0.46)),
    "pot": (INKC, (0.8, 0.45, 0.3)),
    "leaf": (INKC, (0.42, 0.67, 0.36)),
    "cucumber": (INKC, (0.36, 0.62, 0.27)),
    "cuc_light": (None, (0.62, 0.82, 0.45)),
    "cuc_dark": (None, (0.2, 0.4, 0.15)),
    "steel": (INKC, (0.72, 0.78, 0.84)),
    "steel_dark": (INKC, (0.55, 0.62, 0.7)),
    "kibble": (INKC, (0.62, 0.4, 0.22)),
    "sleeve": (INKC, (0.86, 0.36, 0.36)),
    "cuff": (INKC, (0.72, 0.27, 0.28)),
    "skin": (INKC, (0.98, 0.8, 0.66)),
}


# ---------------------------------------------------------------- Флюк (покой)
# Милота по «детской схеме»: большая круглая голова, большие низкие глаза с огромными
# зрачками, крошечные нос и рот, румянец, короткие пухлые лапы, пушистый хвост.
HEAD_ITEMS = {"head", "ear_n", "ear_f"}


def cat_parts():
    body = catmull([(0.8, 0.9), (0.78, 1.24), (0.35, 1.4), (-0.3, 1.4), (-0.82, 1.26), (-0.99, 0.95),
                    (-0.86, 0.52), (-0.3, 0.4), (0.3, 0.41), (0.72, 0.55)], closed=True)
    head = catmull([(0.6, 1.7), (0.67, 1.98), (0.92, 2.2), (1.25, 2.27), (1.58, 2.2), (1.81, 2.0), (1.87, 1.72),
                    (1.95, 1.58), (1.83, 1.52), (1.78, 1.38), (1.56, 1.2), (1.25, 1.14), (0.95, 1.19),
                    (0.72, 1.33), (0.64, 1.47), (0.55, 1.53)], closed=True)
    tail = tube([(-0.78, 1.05), (-1.13, 1.16), (-1.31, 1.4), (-1.36, 1.68), (-1.26, 1.95)],
                [0.28, 0.26, 0.24, 0.22, 0.21])
    fleg = tube(FRONT, [0.32, 0.28, 0.24, 0.23])
    hleg = tube(HIND, [0.62, 0.42, 0.25, 0.23])
    P = [("hlf", hleg + FAR, False, "far", ["hips", "hlf0", "hlf1", "hlf2"], 1.0),
         ("flf", fleg + FAR, False, "far", ["chest", "flf0", "flf1", "flf2"], 1.0),
         ("tail", tail, False, "ink", ["hips", "tail1", "tail2", "tail3", "tail4"], 1.0),
         ("body", body, True, "ink", ["hips", "chest"], 1.1),
         ("hln", hleg, False, "ink", ["hips", "hln0", "hln1", "hln2"], 1.0),
         ("fln", fleg, False, "ink", ["chest", "fln0", "fln1", "fln2"], 1.0),
         ("ear_f", catmull([(1.42, 2.22), (1.76, 2.5), (1.86, 2.44), (1.85, 1.98)], n=8), False, "ink", ["ear_f"], 1.0),
         ("ear_f_in", catmull([(1.52, 2.2), (1.75, 2.39), (1.77, 2.07)], closed=True, n=6), True, "earpink", ["ear_f"], 0.0),
         ("ear_n", catmull([(0.68, 1.95), (0.62, 2.45), (0.73, 2.53), (1.1, 2.22)], n=8), False, "ink", ["ear_n"], 1.0),
         ("ear_n_in", catmull([(0.76, 2.08), (0.73, 2.4), (0.99, 2.21)], closed=True, n=6), True, "earpink", ["ear_n"], 0.0),
         ("head", head, True, "ink", ["head"], 1.1),
         ("tuft", catmull([(1.2, 2.25), (1.25, 2.31), (1.3, 2.25)], n=4), False, "line", ["head"], 0.45),
         ("blush_n", ellipse(0.86, 1.43, 0.11, 0.055), True, "blush", ["head"], 0.0),
         ("blush_f", ellipse(1.66, 1.45, 0.085, 0.048), True, "blush", ["head"], 0.0),
         ("nose", catmull([(1.2, 1.535), (1.34, 1.54), (1.27, 1.465)], closed=True, n=5), True, "nose", ["head"], 0.6)]
    for i, (ex, ez) in enumerate(((0.38, 1.5), (0.4, 1.39))):
        P.append((f"wl{i}", catmull([(0.86, 1.44), ((0.86 + ex) / 2, (1.44 + ez) / 2 + 0.015), (ex, ez)], n=6),
                  False, "line", ["head"], 0.45))
    for i, (ex, ez) in enumerate(((2.12, 1.52), (2.1, 1.41))):
        P.append((f"wr{i}", catmull([(1.66, 1.45), ((1.66 + ex) / 2, (1.45 + ez) / 2 + 0.015), (ex, ez)], n=6),
                  False, "line", ["head"], 0.45))
    return P


EYES_AT = [((0.98, 1.72), 0.155, 0.18), ((1.52, 1.74), 0.13, 0.165)]   # ближний и дальний


def _lid(cx, cz, rx, rz, level, sag=0.012):
    s = (level - cz) / (rz * 1.05)
    t0 = math.asin(max(-0.99, min(0.99, s)))
    t = np.linspace(math.pi - t0, t0, 24)
    arc = np.stack([cx + rx * 1.07 * np.cos(t), cz + rz * 1.08 * np.sin(t)], axis=1)
    return np.vstack([arc, catmull([arc[-1], (cx, level - sag), arc[0]], n=8)[1:-1]])


def eyes(state, look):
    """Состояния: cute, hunt (огромные зрачки), wide (испуг), half (фирменный прищур),
    squint (подозрение), closed (довольные дуги). Взгляд: cam, right, left, up, down."""
    out = []
    dx, dz = {"cam": (0, 0), "right": (0.28, 0), "left": (-0.28, 0), "up": (0.05, 0.22),
              "down": (0.05, -0.25)}[look]
    for k, ((cx, cz), rx, rz) in enumerate(EYES_AT):
        if state == "closed":
            out.append((f"lash{k}", catmull([(cx - rx, cz - 0.03), (cx - rx * 0.4, cz + 0.06), (cx + rx * 0.4, cz + 0.06),
                                             (cx + rx, cz - 0.03)], n=5), False, "line", ["head"], 1.1))
            continue
        if state == "wide":
            rx, rz = rx * 1.1, rz * 1.12
        ri = {"wide": 0.5, "hunt": 0.86}.get(state, 0.78) * rx
        ix, iz = cx + dx * rx, cz + dz * rz - 0.01
        pr = {"wide": 0.16, "hunt": 0.85, "squint": 0.5}.get(state, 0.66) * ri
        out += [(f"eye{k}", ellipse(cx, cz, rx, rz), True, "ink", ["head"], 0.9),
                (f"iris{k}", ellipse(ix, iz, ri, ri * 1.08), True, "iris", ["head"], 0.0),
                (f"pupil{k}", ellipse(ix, iz, pr, pr * 1.1), True, "pupil", ["head"], 0.0)]
        if state != "wide":
            out += [(f"hl{k}", ellipse(ix - ri * 0.35, iz + ri * 0.38, ri * 0.32, ri * 0.32, n=14), True, "white", ["head"], 0.0),
                    (f"hs{k}", ellipse(ix + ri * 0.35, iz - ri * 0.35, ri * 0.13, ri * 0.13, n=10), True, "white", ["head"], 0.0)]
        else:
            out.append((f"hl{k}", ellipse(ix - ri * 0.3, iz + ri * 0.3, ri * 0.14, ri * 0.14, n=10), True, "white", ["head"], 0.0))
        if state in ("half", "squint"):
            level = cz + (0.0 if state == "half" else -0.07)
            out.append((f"lid{k}", _lid(cx, cz, rx, rz, level), True, "ink", ["head"], 1.0))
    return out


def mouth(state):
    """cat (ω), open (мяу), flat, smile."""
    philtrum = ("philtrum", np.array([[1.27, 1.465], [1.27, 1.43]]), False, "line", ["head"], 0.6)
    if state == "open":
        return [philtrum, ("mouth", catmull([(1.19, 1.42), (1.27, 1.425), (1.35, 1.42), (1.31, 1.33), (1.23, 1.33)],
                                             closed=True, n=5), True, "mouthin", ["head"], 0.7)]
    if state == "flat":
        return [philtrum, ("mouth", np.array([[1.2, 1.415], [1.34, 1.415]]), False, "line", ["head"], 0.7)]
    lift = 0.012 if state == "smile" else 0.0
    return [philtrum, ("mouth", catmull([(1.17, 1.43 + lift), (1.22, 1.405), (1.27, 1.43), (1.32, 1.405),
                                         (1.37, 1.43 + lift)], n=4), False, "line", ["head"], 0.7)]


# ---------------------------------------------------------------- комната

def room():
    W = [(rect(-8, 0.55, 10, 6), True, "wall", 0.0)]
    for x in np.arange(-7.6, 10, 0.5):
        W.append((rect(x, 0.72, x + 0.18, 6), True, "stripe", 0.0))
    W.append((rect(-8, -1.5, 10, 0.55), True, "floor", 0.0))
    for z, off in ((0.38, 0.0), (0.12, 0.6), (-0.2, 0.25), (-0.5, 0.85), (-0.85, 0.4)):
        W.append((np.array([[-8, z], [10, z]]), False, "plank", 0.6))
        for x in np.arange(-7.5 + off, 10, 1.7):
            W.append((np.array([[x, z], [x - 0.05, z + 0.17]]), False, "plank", 0.5))
    W.append((rect(-8, 0.55, 10, 0.72), True, "board", 0.8))
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
    W.append((rect(0.55, 2.95, 1.6, 3.75), True, "wood", 1.0))
    W.append((rect(0.65, 3.05, 1.5, 3.65), True, "frame", 0.6))
    W.append((catmull([(0.82, 3.35), (1.05, 3.5), (1.28, 3.35), (1.05, 3.2)], closed=True, n=6), True, "fish", 0.6))
    W.append((catmull([(1.28, 3.35), (1.4, 3.46), (1.4, 3.24)], closed=True, n=3), True, "fish", 0.6))
    W.append((ellipse(0.93, 3.37, 0.018, 0.018, n=8), True, "pupil", 0.0))
    W.append((catmull([(4.55, 0.6), (4.6, 1.95), (4.85, 2.05), (6.5, 2.05), (6.6, 0.6)], closed=True, n=6), True, "sofa", 1.0))
    W.append((catmull([(4.4, 0.55), (4.35, 1.35), (4.55, 1.45), (4.8, 1.35), (4.8, 0.55)], closed=True, n=6), True, "sofa", 1.0))
    W.append((catmull([(4.85, 1.2), (4.95, 1.75), (5.55, 1.8), (5.6, 1.25)], closed=True, n=6), True, "cushion", 0.9))
    W.append((rect(4.8, 0.95, 6.6, 1.2), True, "sofa", 0.9))
    for lx, lz in ((-3.75, 2.0), (-3.35, 2.15), (-3.05, 1.9), (-3.55, 1.75), (-3.2, 1.6)):
        W.append((catmull([(-3.35, 1.2), (lx, lz), (lx + 0.12, lz - 0.05)], n=6), False, "leaf", 1.6))
        W.append((ellipse(lx + 0.05, lz - 0.02, 0.17, 0.08, math.atan2(lz - 1.2, lx + 3.35)), True, "leaf", 0.7))
    W.append((catmull([(-3.65, 1.25), (-3.05, 1.25), (-3.15, 0.75), (-3.55, 0.75)], closed=True, n=4), True, "pot", 0.9))
    W.append((ellipse(1.2, 0.0, 2.6, 0.33, n=48), True, "rug", 0.9))
    W.append((ellipse(1.2, 0.0, 2.15, 0.22, n=48), True, "rug2", 0.0))
    W.append((ellipse(1.2, 0.0, 1.75, 0.15, n=48), True, "rug", 0.0))
    return W


# ---------------------------------------------------------------- реквизит

def cucumber(x, z, rot=0.0, s=1.0):
    base = catmull([(-0.38, 0.0), (-0.3, 0.085), (0.0, 0.1), (0.3, 0.085), (0.4, 0.0), (0.3, -0.085),
                    (0.0, -0.1), (-0.3, -0.085)], closed=True, n=6)
    shine = catmull([(-0.25, 0.045), (0.0, 0.06), (0.25, 0.045)], n=5)
    out = [(transform(base, x, z, rot, s), True, "cucumber", 0.9),
           (transform(np.vstack([shine, shine[::-1] + [0, -0.02]]), x, z, rot, s), True, "cuc_light", 0.0)]
    for bx, bz in ((-0.2, -0.03), (-0.05, 0.02), (0.1, -0.04), (0.22, 0.03), (-0.3, 0.03)):
        out.append((transform(ellipse(bx, bz, 0.014, 0.014, n=8), x, z, rot, s), True, "cuc_dark", 0.0))
    out.append((transform(catmull([(0.39, 0.02), (0.47, 0.035), (0.46, -0.03), (0.39, -0.02)], closed=True, n=3),
                          x, z, rot, s), True, "wood", 0.5))
    return out


def bowl(x):
    return [(catmull([(x - 0.42, 0.33), (x - 0.25, 0.42), (x, 0.47), (x + 0.25, 0.42), (x + 0.42, 0.33)], n=5)
             .tolist() + [[x - 0.42, 0.33]], True, "kibble", 0.7),
            (np.array([[x - 0.48, 0.33], [x + 0.48, 0.33], [x + 0.34, 0.03], [x - 0.34, 0.03]]), True, "steel", 1.0),
            (ellipse(x, 0.33, 0.48, 0.055, n=28), True, "steel_dark", 0.8),
            (catmull([(x - 0.36, 0.34), (x - 0.15, 0.4), (x, 0.38), (x + 0.15, 0.41), (x + 0.36, 0.34)], n=5)
             .tolist() + [[x - 0.36, 0.34]], True, "kibble", 0.6)]


def hand(x, z, open_=0.0):
    """Рука сверху, точка хвата (x, z) — между пальцами."""
    out = [(rect(x - 0.17, z + 0.42, x + 0.17, z + 6), True, "sleeve", 1.0),
           (rect(x - 0.19, z + 0.36, x + 0.19, z + 0.5), True, "cuff", 1.0),
           (catmull([(x - 0.16, z + 0.38), (x - 0.19, z + 0.18), (x - 0.06, z + 0.02), (x + 0.08, z + 0.02),
                     (x + 0.19, z + 0.17), (x + 0.16, z + 0.38)], closed=True, n=5), True, "skin", 1.0)]
    spread = 0.04 + 0.08 * open_
    out.append((catmull([(x - 0.1, z + 0.18), (x - 0.1 - spread, z + 0.05), (x - 0.05 - spread, z - 0.04)], n=5),
                False, "line", 0.8))
    out.append((catmull([(x + 0.1, z + 0.18), (x + 0.1 + spread, z + 0.05), (x + 0.05 + spread, z - 0.04)], n=5),
                False, "line", 0.8))
    return out


def laser(x, z):
    return [(ellipse(x, z, 0.19, 0.08), True, "glow", 0.0), (ellipse(x, z, 0.07, 0.032), True, "laser", 0.0)]


# ---------------------------------------------------------------- кожа и анимация

def _seg_dist(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)


def weights(pts, bones):
    if len(bones) == 1:
        return np.ones((len(pts), 1))
    d = np.stack([_seg_dist(pts, *REST[b]) for b in bones], axis=1)
    w = 1 / (d + 0.02) ** 4
    return w / w.sum(axis=1, keepdims=True)


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


def at(seq, f):
    v = seq[0][1]
    for f0, s in seq:
        if f >= f0:
            v = s
    return v


DEFAULTS = {"root": (0, 0), "rot": 0, "scale": (1, 1), "flip": 1, "hips": 0, "chest": 0, "stretch": 1.0,
            "neck": 0, "head": 0, "ears": 0, "tail": (0.0, 1.0), "tail_amp": D(6), "tail_freq": 0.6,
            "wiggle": 0, "walk": 0, "ground": 1, "puff": 1.0,
            "hln": (0, 0), "fln": (0, 0), "hlf": (0, 0), "flf": (0, 0)}

STRIDE, LIFT, STANCE = 0.42, 0.13, 0.62
PHASE = {"hln": 0.0, "fln": 0.25, "hlf": 0.5, "flf": 0.75}   # шаг по боковой схеме


def _ik(s, t, l1, l2, sign):
    d = max(np.linalg.norm(t - s), 1e-6)
    k = max(1.0, d / (l1 + l2) * 1.0001)
    l1, l2 = l1 * k, l2 * k
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    u = (t - s) / d
    return s + u * a + sign * h * np.array([-u[1], u[0]])


def _sign(leg):
    s, j, t = REST[leg + "0"][0], REST[leg + "0"][1], REST[leg + "1"][1]
    return 1.0 if (t - s)[0] * (j - s)[1] - (t - s)[1] * (j - s)[0] > 0 else -1.0


SIGNS = {leg: _sign(leg) for leg in LEGS}


class Episode:
    """Раскадровка: A — дорожки, EYES / LOOK / MOUTH — смены по кадрам, props(f) — реквизит."""
    LAST = 192
    A = {}
    EYES = [(0, "cute")]
    LOOK = [(0, "cam")]
    MOUTH = [(0, "cat")]
    ONES = ()          # диапазоны кадров «по единицам»

    def ch(self, name, f):
        tr = self.A.get(name)
        return tr(f) if tr is not None else np.array(DEFAULTS[name], float)

    def props_back(self, f):
        return []

    def props_front(self, f):
        return []

    def camera(self, f):
        return (1.0, 2.0, 9.0)

    # ------------------------------------------------ поза
    def walk_phase(self, f):
        """Фаза шага по пройденному пути: лапы не скользят при любой скорости."""
        if not hasattr(self, "_dist"):
            self._dist, d = [0.0], 0.0
            for g in range(1, self.LAST + 2):
                if float(self.ch("walk", g)) > 0:
                    d += abs(float(self.ch("root", g)[0]) - float(self.ch("root", g - 1)[0]))
                self._dist.append(d)
        return self._dist[min(int(f), len(self._dist) - 1)] / (STRIDE / STANCE)

    def pose(self, f):
        rx, rz = self.ch("root", f)
        flip = float(self.ch("flip", f))
        sx, sz = self.ch("scale", f)
        walk = float(self.ch("walk", f))
        ph = self.walk_phase(f) if walk > 0 else 0.0
        bob = -0.035 * walk * (1 - math.cos(4 * math.pi * ph)) / 2
        G = M(rx, rz + bob, float(self.ch("rot", f)), sx * flip, sz)
        Gi = np.linalg.inv(G)
        st = float(self.ch("stretch", f))
        t = f / FPS
        wig = float(self.ch("wiggle", f))
        L = {}
        for b in ("hips", "chest"):
            h0, t0 = REST[b]
            rot = float(self.ch(b, f)) + (wig * D(5) * math.sin(2 * math.pi * 3 * t) if b == "hips" else 0)
            L[b] = bone_matrix(h0, ang(t0 - h0), h0, ang(t0 - h0) + rot, st, 1 / math.sqrt(st))
        tail_base, curl = self.ch("tail", f)
        amp, freq = float(self.ch("tail_amp", f)), float(self.ch("tail_freq", f))
        ears = float(self.ch("ears", f))
        local = {"neck": float(self.ch("neck", f)) + walk * D(2) * math.sin(4 * math.pi * ph),
                 "head": float(self.ch("head", f)), "ear_n": -ears, "ear_f": ears * 0.8}
        for i in range(1, 5):
            sway = amp * math.sin(2 * math.pi * freq * (t - i * 0.12)) + wig * D(14) * math.sin(2 * math.pi * 3 * (t - i * 0.05))
            local[f"tail{i}"] = (tail_base if i == 1 else 0) + D(-12) * (curl - 1) * (i - 1) / 3 + sway
        for b in ("neck", "head", "ear_n", "ear_f", "tail1", "tail2", "tail3", "tail4"):
            parent = BONES[b][0]
            h0, t0 = REST[b]
            ph0, pt0 = REST[parent]
            pm = L[parent]
            pa = ang(apply(pm, pt0) - apply(pm, ph0)) - ang(pt0 - ph0)
            L[b] = bone_matrix(h0, ang(t0 - h0), apply(pm, h0), ang(t0 - h0) + pa + local[b])
        ground = float(self.ch("ground", f))
        for leg in LEGS:  # лапы: IK в системе кота
            parent = BONES[leg + "0"][0]
            h0, j0, w0, p0 = REST[leg + "0"][0], REST[leg + "0"][1], REST[leg + "1"][1], REST[leg + "2"][1]
            dx, dz = self.ch(leg, f)
            if walk > 0:
                u = (ph + PHASE[leg]) % 1
                if u < STANCE:
                    wx, wz = STRIDE * (0.5 - u / STANCE), 0.0
                else:
                    s = (u - STANCE) / (1 - STANCE)
                    wx, wz = STRIDE * (-0.5 + s), LIFT * math.sin(math.pi * s)
                dx, dz = dx + walk * wx, dz + walk * wz
            # z лапы: при ground = 1 от пола (лапы стоят, когда кот приседает), при 0 — вместе с телом
            world = apply(G, np.array([p0[0] + dx, 0.0]))
            z_floor = p0[1] + dz
            z_body = apply(G, np.array([p0[0] + dx, p0[1] + dz]))[1]
            paw = apply(Gi, np.array([world[0], ground * z_floor + (1 - ground) * z_body]))
            shoulder = apply(L[parent], h0)
            wrist = paw - (p0 - w0)
            j = _ik(shoulder, wrist, np.linalg.norm(j0 - h0), np.linalg.norm(w0 - j0), SIGNS[leg])
            for i, (a, b, ra, rb) in enumerate(((shoulder, j, h0, j0), (j, wrist, j0, w0), (wrist, paw, w0, p0))):
                L[f"{leg}{i}"] = bone_matrix(ra, ang(rb - ra), a, ang(b - a), np.linalg.norm(b - a) / np.linalg.norm(rb - ra))
        return {b: G @ m for b, m in L.items()}, G

    # ------------------------------------------------ сборка
    def cat_items(self, f, cache, parts):
        W, G = self.pose(f)
        rx, rz = self.ch("root", f)
        items = [(ellipse(rx + 0.05 * float(self.ch("flip", f)), 0.02, 1.05 * (1 - 0.3 * min(max(0.0, rz), 1)), 0.09),
                  True, "shadow", 0.0)]

        def skin(key, pts, bones):
            if key not in cache:
                cache[key] = weights(pts, bones)
            w = cache[key]
            return sum(w[:, i:i + 1] * apply(W[b], pts) for i, b in enumerate(bones))

        puff = float(self.ch("puff", f))
        for name, pts, closed, m, bones, th in parts:
            if name == "tail" and puff != 1.0:  # распушённый хвост
                pts = tube([(-0.78, 1.05), (-1.13, 1.16), (-1.31, 1.4), (-1.36, 1.68), (-1.26, 1.95)],
                           np.array([0.28, 0.26, 0.24, 0.22, 0.21]) * puff)
                name = f"tail{puff:.2f}"
            items.append((skin(name, pts, bones), closed, m, th))
            if name == "head":
                st, lk, mo = at(self.EYES, f), at(self.LOOK, f), at(self.MOUTH, f)
                for en, ep, ec, em, eb, eth in eyes(st, lk) + mouth(mo):
                    items.append((skin(en + st + lk + mo, ep, eb), ec, em, eth))
        return items, W

    def drawing_frames(self):
        return [f for f in range(1, self.LAST + 1)
                if f % 2 == 1 or any(a <= f <= b for a, b in self.ONES)]


# ---------------------------------------------------------------- Blender

def srgb(c):
    return tuple(x ** 2.2 for x in c)


def build(ep, stills=None):
    import bpy
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, ep.LAST
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
    for f in range(1, ep.LAST + 1):
        x, z, w = ep.camera(f)
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
        # show_fill ненадёжен: у материала без заливки прозрачная заливка, иначе её видно
        g.fill_color = (*srgb(fill), alpha) if fill else (0, 0, 0, 0)
        mats[name] = m
    index = {n: i for i, n in enumerate(mats)}

    def gp_object(name, depth, boil):
        gp = bpy.data.grease_pencils.new(name)
        ob = bpy.data.objects.new(name, gp)
        ob.rotation_euler = (math.pi / 2, 0, 0)  # рисуем в XY объекта, Y смотрит вверх
        ob.location = (0, depth, 0)
        sc.collection.objects.link(ob)
        for m in mats.values():
            gp.materials.append(m)
        layer = gp.layers.new("ink")
        layer.use_lights = False  # плоские цвета
        noise = ob.modifiers.new("boil", "GREASE_PENCIL_NOISE")
        noise.factor, noise.factor_thickness, noise.noise_scale = boil, 0.25, 0.6
        noise.use_random, noise.step, noise.seed = True, 2, 3
        return layer

    def radius(n, closed, thick, seed):
        r = np.full(n, 0.0145 * thick)
        r *= 1 + 0.16 * np.sin(np.linspace(0, 6.0, n) + seed)
        if not closed:
            r *= np.clip(np.minimum(np.arange(n), np.arange(n)[::-1]) / 6, 0.25, 1)
        return r

    def draw(layer, frame, items):
        d = layer.frames.new(frame).drawing
        if not items:
            return
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

    draw(gp_object("room", 3.0, 0.008), 1, room())
    back, cat, front = gp_object("back", 1.0, 0.01), gp_object("fluk", 0.0, 0.012), gp_object("front", -1.0, 0.01)
    parts = cat_parts()
    cache = {}
    frames = sorted(set(stills)) if stills else ep.drawing_frames()
    for f in frames:
        items, _ = ep.cat_items(f, cache, parts)
        draw(cat, f, items)
        draw(back, f, ep.props_back(f))
        draw(front, f, ep.props_front(f))
    return sc


def run(ep, script_file):
    import bpy
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    stills = [int(x) for x in argv[argv.index("--stills") + 1].split(",")] if "--stills" in argv else None
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path(script_file).parent / "out"
    if "--expr" in argv:  # лист выражений: --expr cute:cam,half:cam,...
        sets = [e.split(":") for e in argv[argv.index("--expr") + 1].split(",")]
        ep.EYES = [(i * 10, s[0]) for i, s in enumerate(sets)]
        ep.LOOK = [(i * 10, s[1]) for i, s in enumerate(sets)]
        ep.MOUTH = [(i * 10, s[2] if len(s) > 2 else "cat") for i, s in enumerate(sets)]
        stills = [i * 10 + 1 for i in range(len(sets))]
    sc = build(ep, stills)
    out.mkdir(parents=True, exist_ok=True)
    if stills:
        for f in stills:
            sc.frame_set(f)
            sc.render.filepath = str(out / f"still_{f:03d}.png")
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(script_file).with_suffix(".blend")))
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = str(out / "frames" / "f_")
        bpy.ops.render.render(animation=True)
