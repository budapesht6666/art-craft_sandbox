"""Fluk — Episode 1: The Cucumber (сценарий EPISODE1.md, версия 2).

python ep1.py OUT_DIR [кадры через запятую]  ->  OUT_DIR/f_0001.png …
Позы — целые рисунки из листов 3, 8, 9; внутри позы качаются голова и хвост, кот дышит.
"""
import math
import sys
from pathlib import Path

from PIL import Image

import rig
from rig import Track

FPS, LAST = 24, 620
W, H = 1920, 1080
FLOOR = 985
S = 0.85                       # масштаб поз
ROOM = rig.room()
ROOM_SRC = Image.open(rig.ROOM).convert("RGBA")
CUC1, CUC2 = 380, 1480         # первый огурец сзади, второй — прямо перед носом
TOUCH = 562                    # кадр, где Флюк задом упирается в первый огурец
X_TOUCH = 735                  # где он в этот момент стоит
BOWL_X = 915


def at(seq, f):
    v = seq[0][1]
    for f0, x in seq:
        if f >= f0:
            v = x
    return v


def sway(f, hz, amp, phase=0.0):
    return amp * math.sin(2 * math.pi * (hz * f / FPS + phase))


def twitch(f, hits, amp=12, dur=5):
    """Резкие подёргивания в заданных кадрах."""
    return sum(amp * math.sin(math.pi * (f - h) / dur) for h in hits if 0 <= f - h <= dur)


def breathe(f, hz=0.8, amp=0.012):
    b = math.sin(2 * math.pi * hz * f / FPS)
    return 1 - amp * 0.5 * b, 1 + amp * b


def hand(c, f, ytrack, seq, x):
    y = float(ytrack(f))
    if y < -650:
        return
    src = rig.extend_top("hands", at(seq, f), 900)
    rig.place(c, src, (src.width * 0.42, src.height - 10), (x + 40, y), 0, 0.62, 0.62)


def cucumber(c, x, rot=0.0):
    src = rig.sprite("props", 1)
    rig.place(c, src, (src.width / 2, src.height), (x, FLOOR - 6), rot, 0.42, 0.42)


BOWL_LAND = 1690


def bowl(c, f=0):
    """Миска. В панике Флюк её задевает: она кувырком улетает к креслу и падает вверх дном."""
    if f < 170:
        src = rig.sprite("props", 3)
        rig.place(c, src, (src.width / 2, src.height), (BOWL_X, FLOOR + 8), 0, 0.42, 0.42)
        return
    u = min(1.0, (f - 170) / 14)
    x = BOWL_X + (BOWL_LAND - BOWL_X) * u
    y = FLOOR - 40 - 300 * math.sin(math.pi * u) * (1 - 0.15 * u)
    rot = math.radians(540 * u) if u < 1 else math.pi
    src = rig.sprite("props", 4)                     # пустая: корм разлетелся
    rig.place(c, src, (src.width / 2, src.height / 2), (x, y), rot, 0.42, 0.42)


HAND1_Y = Track((0, -700), (30, -700), (42, 250), (48, 250), (60, 600), (66, 600), (78, 975), (88, 975),
                (110, -700, "in"))
HAND1 = [(0, 1), (82, 2), (86, 3)]
HAND2_Y = Track((0, -700), (484, -700), (494, 300), (500, 300), (512, 975), (522, 975), (544, -700, "in"))
HAND2 = [(0, 1), (516, 2), (520, 3)]


def wide(f):
    c = ROOM.copy()
    if f >= 86:  # первый огурец лежит; после тычка качается
        rock = 8 * math.sin(math.pi * (f - 310) / 4) * math.exp(-(f - 310) / 8) if 310 <= f <= 334 else 0
        cucumber(c, CUC1, math.radians(rock))
    if f >= 520:
        cucumber(c, CUC2)
    if f <= 96:                                # Б1: ест
        bx, by = breathe(f)
        rig.pose(c, "extra", 2, (330, 340), (800, FLOOR), S, sx=bx, sy=by,
                 regions=[((330, 175), (450, 230), 170, sway(f, 2, 3)),
                          ((200, 190), (80, 200), 170, sway(f, 0.6, 7))])
        bowl(c, f)                                # миска поверх морды
    elif f <= 144:                             # Б2: сел, облизывается
        bx, by = breathe(f)
        bowl(c, f)                                # миска уже за котом
        rig.pose(c, "key", 1, (260, 515), (640, FLOOR), S, sx=bx, sy=by,
                 regions=[((290, 270), (300, 170), 160, sway(f, 1.5, 2)),
                          ((150, 330), (60, 250), 170, sway(f, 0.5, 6))])
    elif 169 <= f <= 186:                      # Б4: взрыв, без замаха
        u = (f - 169) / 17
        x = 660 + (1400 - 660) * u
        y = (FLOOR - 270) - 340 * math.sin(math.pi * min(u * 1.1, 1))
        sx, sy = (0.9, 1.12) if f < 172 else ((1.0, 1.0) if f < 183 else (1.05, 0.95))
        bowl(c, f)
        rig.pose(c, "key", 3, (330, 330), (x, y), S, sx=sx, sy=sy, rot=math.radians(-6 + 12 * u),
                 regions=[((420, 230), (430, 100), 150, sway(f, 6, 10))])
    elif f <= 240:                             # Б5: приземлился и застыл
        k = min(1.0, (f - 187) / 5)
        sx, sy = 1.12 - 0.12 * k, 0.86 + 0.14 * k
        bx, by = breathe(f, 1.6, 0.015)
        bowl(c, f)
        rig.pose(c, "key", 4, (300, 515), (1400, FLOOR), S, sx=sx * bx, sy=sy * by,
                 regions=[((430, 190), (510, 90), 170, twitch(f, [205, 216, 229]))])
    elif f <= 300:                             # Б6: крадётся — шажок, пауза
        steps = [(241, 251, 1400, 1160), (268, 278, 1160, 920), (289, 298, 920, 700)]
        x, bob = 700, 0.0
        for f0, f1, x0, x1 in steps:
            if f < f0:
                x = x0
                break
            if f <= f1:
                u = (f - f0) / (f1 - f0)
                x, bob = x0 + (x1 - x0) * (u * u * (3 - 2 * u)), -10 * math.sin(math.pi * u)
                break
        bowl(c, f)
        rig.pose(c, "key", 5, (330, 480), (x, FLOOR + bob), S, flip=True,
                 regions=[((430, 260), (510, 170), 170, sway(f, 0.7, 2)),
                          ((200, 230), (60, 220), 180, sway(f, 0.4, 5))])
    elif f <= 326:                             # Б6: тычок лапой
        reach = -28 * math.sin(math.pi * min(1, max(0, (f - 304) / 14)))
        bowl(c, f)
        rig.pose(c, "key", 6, (330, 600), (680 + reach, FLOOR), S,
                 regions=[((550, 250), (620, 60), 190, sway(f, 1.2, 5))])
    elif f <= 342:                             # Б7: отпрыгнул назад
        u = min(1, (f - 327) / 11)
        x = 680 + 260 * u
        y = FLOOR - 130 * math.sin(math.pi * u)
        sx, sy = (1.1, 0.88) if f >= 338 else (0.94, 1.08)
        bowl(c, f)
        rig.pose(c, "key", 4, (300, 515), (x, y), S, sx=sx, sy=sy, regions=[((430, 190), (510, 90), 170, 14)])
    elif f <= 432:                             # Б8: умывается как ни в чём не бывало
        bx, by = breathe(f, 0.6)
        lick = sway(f, 2.4, 4) if (f - 343) % 36 < 26 else 0
        bowl(c, f)
        rig.pose(c, "key", 7, (330, 570), (1180, FLOOR), S, sx=bx, sy=by,
                 regions=[((320, 330), (390, 250), 200, lick)])
    elif f <= 519:                             # Б9: «ты ничего не видел»
        bx, by = breathe(f, 0.5)
        bowl(c, f)
        rig.pose(c, "key", 8, (250, 570), (1180, FLOOR), S, sx=bx, sy=by,
                 regions=[((250, 300), (260, 180), 170, sway(f, 0.3, 1.5))])
    elif f <= TOUCH + 6:                       # Б10: второй огурец — пятится… и упирается в первый
        u = min(1.0, max(0.0, (f - 528) / (TOUCH - 528)))
        x = 1180 - (1180 - X_TOUCH) * u
        bob = -6 * abs(math.sin(math.pi * 3 * u)) if f < TOUCH else 0
        bowl(c, f)
        rig.pose(c, "extra", 1, (330, 410), (x, FLOOR + bob), S,
                 regions=[((180, 190), (50, 190), 170, sway(f, 0.5, 4) if f < TOUCH else 18)])
    elif f <= TOUCH + 18:                      # третий испуг — с воплем вверх из кадра
        u = (f - TOUCH - 7) / 11
        bowl(c, f)
        rig.pose(c, "key", 3, (330, 330), (X_TOUCH + 60, FLOOR - 270 - 1100 * u ** 1.3), S,
                 sx=0.9, sy=1.15, rot=math.radians(8), regions=[((420, 230), (430, 100), 150, sway(f, 6, 10))])
    else:                                      # пустая комната, два огурца, перевёрнутая миска
        bowl(c, f)
    hand(c, f, HAND1_Y, HAND1, CUC1)
    hand(c, f, HAND2_Y, HAND2, CUC2)
    return c


def closeup(f):
    """Б3: крупно — оглядывается через плечо, потом глаза на пол-лица."""
    c = ROOM_SRC.crop((700, 300, 2400, 1256)).resize((W, H), Image.LANCZOS)
    if f < 158:
        u = (f - 145) / 13
        rig.pose(c, "extra", 4, (260, 470), (980, H + 30), 1.45, rot=math.radians(-3 + 4 * u))
    else:
        s = 1.45 * (1.06 if f < 161 else 1.0)   # «тейк»: голова дёргается крупнее
        rig.pose(c, "extra", 6, (265, 470), (980, H + 230), s * 1.15)
    return c


def push_in(img, f):
    """Б9: медленный наезд на морду."""
    if not 440 <= f <= 519:
        return img
    z = 1 + 0.22 * min(1, (f - 440) / 50)
    cx, cy = 1180, 700
    w, h = W / z, H / z
    x0, y0 = min(max(cx - w / 2, 0), W - w), min(max(cy - h / 2, 0), H - h)
    return img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS)


def frame(f):
    img = closeup(f) if 145 <= f <= 168 else wide(f)
    return push_in(img.convert("RGB"), f)


ONES = [(160, 200), (300, 345), (560, 584)]              # быстрые места по единицам
CUTS = (145, 158, 169, 187, 343, 433, 520, 562, 569)   # смены поз рисуются в свой кадр

if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    last = None
    for f in (only or range(1, LAST + 1)):
        if only or last is None or f % 2 == 1 or f in CUTS or any(a <= f <= b for a, b in ONES):
            last = frame(f)
        last.save(out / f"f_{f:04d}.png")
    print("ok")
