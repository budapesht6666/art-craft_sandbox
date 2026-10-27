"""Флюк из деталей: раскладка в координатах торса (пиксели исходника) и поза."""
import math

import numpy as np

import rig

# детали: (группа, номер, точка крепления в детали)
TORSO = ("parts", 1, (330, 215))
HEAD = ("parts", 2, (268, 445))
LEG_FN, LEG_FF = ("parts", 3, (100, 70)), ("parts", 4, (110, 70))
LEG_HN, LEG_HF = ("parts", 5, (190, 130)), ("parts", 6, (150, 130))
TAIL, TAIL_PUFF = ("parts", 7, (470, 200)), ("parts", 8, (150, 545))
EXPR_PIVOT = (295, 470)            # шея у голов из листа выражений (≈590×510)

# где детали крепятся к торсу (пиксели торса)
J = {"head": (545, 140), "fn": (505, 300), "ff": (548, 285), "hn": (185, 303), "hf": (228, 292),
     "tail": (40, 205), "tail_puff": (70, 160)}
LEG_SCALE, HEAD_SCALE, TAIL_SCALE = 0.66, 0.85, 0.72
GROUND = 518                       # линия пола в пикселях торса


def to_canvas(G, p):
    """Пиксель торса -> пиксель кадра. G = (pos, scale, rot, flip, squash)."""
    pos, scale, rot, flip, (sx, sy) = G
    x, y = (p[0] - TORSO[2][0]) * flip * sx, (p[1] - GROUND) * sy
    c, s = math.cos(rot), math.sin(rot)
    return np.array([pos[0] + (x * c - y * s) * scale, pos[1] + (x * s + y * c) * scale])


def draw(canvas, pos, scale=1.0, flip=1, rot=0.0, squash=(1.0, 1.0), head=None, head_rot=0.0, head_flip=False,
         tail="calm", tail_dir=0.0, tail_curl=0.0, legs=None):
    """pos — точка на полу под центром торса. legs: углы лап {fn, ff, hn, hf} в градусах."""
    legs = legs or {}
    G = (pos, scale, rot, flip, squash)
    sx, sy = squash
    fl = flip < 0

    def part(spec, joint, extra_rot=0.0, k=1.0, override=None, pivot=None):
        g, i, pv = spec
        src = rig.sprite(g, i, fl) if override is None else override
        if pivot is not None:
            pv = pivot
        if fl:
            pv = (src.width - pv[0], pv[1])
        rig.place(canvas, src, pv, to_canvas(G, joint), rot + math.radians(extra_rot) * flip,
                  scale * k * sx, scale * k * sy)

    part(LEG_HF, J["hf"], legs.get("hf", 0), LEG_SCALE)
    part(LEG_FF, J["ff"], legs.get("ff", 0), LEG_SCALE)
    if tail == "puff":
        part(TAIL_PUFF, J["tail_puff"], tail_dir, TAIL_SCALE)
    else:  # спокойный хвост гнётся сеткой
        src = rig.sprite("parts", 7, fl)
        base = (src.width - TAIL[2][0], TAIL[2][1]) if fl else TAIL[2]
        grid = rig.bend_grid(src, base, math.degrees(rot) + tail_dir * flip, tail_curl * flip,
                             scale * TAIL_SCALE, to_canvas(G, J["tail"]))
        rig.warp(canvas, src, grid)
    part(TORSO, (TORSO[2][0], TORSO[2][1]))
    part(LEG_HN, J["hn"], legs.get("hn", 0), LEG_SCALE)
    part(LEG_FN, J["fn"], legs.get("fn", 0), LEG_SCALE)
    # голова может смотреть назад (зеркально), не разворачивая тело
    hf = fl != head_flip
    spec = HEAD if head is None else ("expr", head, EXPR_PIVOT)
    src = rig.sprite(spec[0], spec[1], hf)
    pv = spec[2] if not hf else (src.width - spec[2][0], spec[2][1])
    k = HEAD_SCALE * (1 if head is None else 0.92)
    rig.place(canvas, src, pv, to_canvas(G, J["head"]), rot + math.radians(head_rot) * flip * (-1 if head_flip else 1),
              scale * k * sx, scale * k * sy)
