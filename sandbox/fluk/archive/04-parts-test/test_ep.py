"""Тест «Огурец» из нарисованных деталей: python test_ep.py OUT_DIR -> кадры f_0001.png …

Флюк стоит с фирменным «ну и?» → рука сзади кладёт огурец → оглядывается → испуг,
хвост ёршиком, прыжок → приземление → шипит на огурец → злобный взгляд в камеру.
"""
import math
import sys
from pathlib import Path

from PIL import Image

import fluk
import rig

from rig import Track

FPS, LAST = 24, 200
OUT = Path(sys.argv[1])
ROOMIMG = rig.room()
FLOOR = 985                          # пол под лапами Флюка, пиксели кадра
CUC_X = 560                          # где ляжет огурец

A = {
    "x": Track((0, 1060), (118, 1060), (140, 1380, "out"), (200, 1380)),
    "lift": Track((0, 0), (114, 0), (118, -18), (129, 230, "out"), (140, 0, "in"), (146, -22, "out"), (154, 0)),
    "squash": Track((0, (1, 1)), (114, (1, 1)), (118, (1.08, 0.9)), (122, (0.9, 1.14)), (136, (0.96, 1.05)),
                    (140, (1.14, 0.86), "out"), (150, (1, 1))),
    "rot": Track((0, 0), (118, 0), (126, math.radians(-7)), (138, math.radians(4)), (146, 0)),
    "head_rot": Track((0, 0), (30, 0), (40, 6), (90, 6), (100, -4), (110, 8), (146, 0), (156, 6), (200, 6)),
    "tail_dir": Track((0, -8), (200, -8)),
    "legs": Track((0, (0, 0, 0, 0)), (118, (0, 0, 0, 0)), (124, (-22, -18, 24, 20)), (136, (-14, -10, 14, 12)),
                  (140, (0, 0, 0, 0))),
    "hand_y": Track((0, -700), (36, -700), (48, 300), (54, 300), (66, 620), (72, 620), (84, 975), (96, 975),
                    (122, -700, "in")),
}
HEADS = [(0, None), (40, 2), (100, 4), (104, None), (110, 7), (118, 3), (146, 9), (164, 8)]  # None — голова из листа 4
HEAD_FLIP = [(0, False), (106, True), (156, False)]   # True — смотрит назад, на огурец
TAIL = [(0, "calm"), (118, "puff"), (170, "calm")]
HAND = [(0, 1), (90, 2), (96, 3)]                     # 1 держит огурец, 2 отпускает, 3 пустая


def at(seq, f):
    v = seq[0][1]
    for f0, s in seq:
        if f >= f0:
            v = s
    return v


def frame(f):
    c = ROOMIMG.copy()
    if f >= 96:  # огурец на полу (раньше он ещё в руке)
        cuc = rig.sprite("props", 1)
        rig.place(c, cuc, (cuc.width / 2, cuc.height), (CUC_X, FLOOR - 6), 0, 0.42, 0.42)
    t = f / FPS
    sway = math.sin(2 * math.pi * 0.5 * t) * 8
    fn, ff, hn, hf = A["legs"](f)
    head = at(HEADS, f)
    fluk.draw(c, (A["x"](f), FLOOR - A["lift"](f)), scale=0.74, squash=tuple(A["squash"](f)), rot=float(A["rot"](f)),
              head=head, head_rot=float(A["head_rot"](f)), head_flip=at(HEAD_FLIP, f),
              tail=at(TAIL, f), tail_dir=float(A["tail_dir"](f)), tail_curl=25 + sway,
              legs={"fn": fn, "ff": ff, "hn": hn, "hf": hf})
    hy = float(A["hand_y"](f))
    if hy > -650:
        h = at(HAND, f)
        src = rig.extend_top("hands", h, 900)
        # точка хвата — низ кисти, руку ставим так, чтобы огурец оказался у пола в CUC_X
        rig.place(c, src, (src.width * 0.42, src.height - 10), (CUC_X + 40, hy), 0, 0.62, 0.62)
    return c.convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    last = None
    for f in (only or range(1, LAST + 1)):
        ones = 114 <= f <= 156
        if only or ones or f % 2 == 1 or last is None:
            last = frame(f)                  # рисунки по двойкам, прыжок по единицам
        last.save(OUT / f"f_{f:04d}.png")
    print("ok")
