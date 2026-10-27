"""Сценарий серии -> ключи для EffectCraft: python gen_ec.py -> ec/ep1_keys.json.

Тайминг тот же, что в ep1.py (кадры 24 к/с, кадр 1 = 0 с). Слои: комната, огурцы,
миски, позы-рисунки (каждая на своём отрезке), руки, крупные планы. Внутри поз —
булавки Puppet: неподвижные держат лапы и тело, подвижные качают голову и хвост.
Строит проект build_ec.js.
"""
import json
import math
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
CUT = HERE.parent / "art" / "cut"
ROOM = HERE.parent / "art" / "sheets" / "07_room.png"
FPS, LAST = 24, 620
W, H = 1920, 1080
FLOOR = 985
S = 85.0                                  # масштаб поз, %
CUC1, CUC2, BOWL_X, BOWL_LAND = 380, 1480, 915, 1690
TOUCH, X_TOUCH = 562, 735


def t(f):
    return round((f - 1) / FPS, 5)


def size(p):
    return Image.open(p).size


def sway(f, hz, amp, phase=0.0):
    return amp * math.sin(2 * math.pi * (hz * f / FPS + phase))


def twitch(f, hits, amp=12, dur=5):
    return sum(amp * math.sin(math.pi * (f - h) / dur) for h in hits if 0 <= f - h <= dur)


def breathe(f, hz=0.8, amp=0.012):
    b = math.sin(2 * math.pi * hz * f / FPS)
    return 1 - amp * 0.5 * b, 1 + amp * b


def rot_about(p, pivot, deg):
    a = math.radians(deg)
    dx, dy = p[0] - pivot[0], p[1] - pivot[1]
    return [pivot[0] + dx * math.cos(a) - dy * math.sin(a), pivot[1] + dx * math.sin(a) + dy * math.cos(a)]


def smooth(u):
    return u * u * (3 - 2 * u)


LAYERS = []


def layer(name, src, f0, f1, anchor, **kw):
    """f0..f1 — кадры, на которых слой виден (включительно)."""
    L = {"name": name, "src": str(src).replace("\\", "/"), "in": t(f0), "out": t(f1 + 1),
         "anchor": list(anchor), "pos": [], "scale": [], "rot": [], "pins": [], "parent": "cam",
         "motionBlur": False, "flip": False}
    L.update(kw)
    LAYERS.append(L)
    return L


def keys(L, frames, fn):
    """fn(f) -> dict(pos=(x,y), scale=(sx,sy) в %, rot=°)."""
    for f in frames:
        v = fn(f)
        if "pos" in v:
            L["pos"].append([t(f), *v["pos"]])
        if "scale" in v:
            sx, sy = v["scale"]
            L["scale"].append([t(f), -sx if L["flip"] else sx, sy])
        if "rot" in v:
            L["rot"].append([t(f), v["rot"]])


def pins(L, fixed, moving, frames):
    """fixed: неподвижные точки. moving: [(точка, опора, f -> угол°)]."""
    L["pins"] = [{"rest": list(p), "keys": []} for p in fixed]
    for p, pivot, ang in moving:
        L["pins"].append({"rest": list(p), "keys": [[t(f), *rot_about(p, pivot, ang(f))] for f in frames]})


def cut(g, i):
    return CUT / g / f"{g}_{i:02d}.png"


def every(f0, f1, step=2):
    out = list(range(f0, f1 + 1, step))
    if out[-1] != f1:
        out.append(f1)
    return out


# ---------------------------------------------------------------- фон и реквизит
rw, rh = size(ROOM)
layer("room", ROOM, 1, LAST, (rw / 2, rh / 2), pos=[[0, W / 2, H / 2]], scale=[[0, W / rw * 100, W / rw * 100]])

cuc = cut("props", 1)
cw, ch = size(cuc)
c1 = layer("cucumber1", cuc, 86, LAST, (cw / 2, ch), pos=[[0, CUC1, FLOOR - 6]], scale=[[0, 42, 42]])
c1["rot"] = [[0, 0]] + [[t(f), 8 * math.sin(math.pi * (f - 310) / 4) * math.exp(-(f - 310) / 8)] for f in range(310, 335)]
layer("cucumber2", cuc, 520, LAST, (cw / 2, ch), pos=[[0, CUC2, FLOOR - 6]], scale=[[0, 42, 42]])

bowl = cut("props", 3)
bw, bh = size(bowl)
layer("bowl_back", bowl, 97, 169, (bw / 2, bh), pos=[[0, BOWL_X, FLOOR + 8]], scale=[[0, 42, 42]])
empty = cut("props", 4)
ew, eh = size(empty)
eb = layer("bowl_flying", empty, 170, LAST, (ew / 2, eh / 2), scale=[[0, 42, 42]], motionBlur=True)
for f in range(170, 186):
    u = min(1.0, (f - 170) / 14)
    eb["pos"].append([t(f), BOWL_X + (BOWL_LAND - BOWL_X) * u, FLOOR - 40 - 300 * math.sin(math.pi * u) * (1 - 0.15 * u)])
    eb["rot"].append([t(f), 540 * u if u < 1 else 180])

# ---------------------------------------------------------------- Флюк по битам
# Б1: ест (миска перед мордой — отдельный слой выше)
L = layer("b1_eat", cut("extra", 2), 1, 96, (330, 340))
keys(L, every(1, 96, 4), lambda f: {"pos": (800, FLOOR), "scale": tuple(S * v for v in breathe(f))})
pins(L, [(150, 330), (470, 330), (300, 210)],
     [((450, 230), (330, 175), lambda f: sway(f, 2, 3)), ((80, 200), (200, 190), lambda f: sway(f, 0.6, 7))], every(1, 96))
layer("bowl_front", bowl, 1, 96, (bw / 2, bh), pos=[[0, BOWL_X, FLOOR + 8]], scale=[[0, 42, 42]])

# Б2: сел, облизывается
L = layer("b2_lick", cut("key", 1), 97, 144, (260, 515))
keys(L, every(97, 144, 4), lambda f: {"pos": (640, FLOOR), "scale": tuple(S * v for v in breathe(f))})
pins(L, [(150, 500), (380, 500), (250, 380)],
     [((300, 170), (290, 270), lambda f: sway(f, 1.5, 2)), ((60, 250), (150, 330), lambda f: sway(f, 0.5, 6))],
     every(97, 144))

# Б4: взрыв без замаха
L = layer("b4_jump", cut("key", 3), 169, 186, (330, 330), motionBlur=True)


def jump(f):
    u = (f - 169) / 17
    sx, sy = (0.9, 1.12) if f < 172 else ((1.0, 1.0) if f < 183 else (1.05, 0.95))
    return {"pos": (660 + 740 * u, (FLOOR - 270) - 340 * math.sin(math.pi * min(u * 1.1, 1))),
            "scale": (S * sx, S * sy), "rot": -6 + 12 * u}


keys(L, range(169, 187), jump)
pins(L, [(330, 330), (200, 450)], [((430, 100), (420, 230), lambda f: sway(f, 6, 10))], range(169, 187))

# Б5: приземлился и застыл
L = layer("b5_frozen", cut("key", 4), 187, 240, (300, 515))


def frozen(f):
    k = min(1.0, (f - 187) / 5)
    bx, by = breathe(f, 1.6, 0.015)
    return {"pos": (1400, FLOOR), "scale": (S * (1.12 - 0.12 * k) * bx, S * (0.86 + 0.14 * k) * by)}


keys(L, list(range(187, 193)) + every(194, 240, 3), frozen)
pins(L, [(150, 500), (450, 500), (300, 350)], [((510, 90), (430, 190), lambda f: twitch(f, [205, 216, 229]))],
     every(187, 240))

# Б6: крадётся — шажок, пауза (поза смотрит вправо, отражаем)
L = layer("b6_sneak", cut("key", 5), 241, 300, (330, 480), flip=True)
STEPS = [(241, 251, 1400, 1160), (268, 278, 1160, 920), (289, 298, 920, 700)]


def sneak(f):
    x, bob = 700, 0.0
    for f0, f1, x0, x1 in STEPS:
        if f < f0:
            x = x0
            break
        if f <= f1:
            u = (f - f0) / (f1 - f0)
            x, bob = x0 + (x1 - x0) * smooth(u), -10 * math.sin(math.pi * u)
            break
    return {"pos": (x, FLOOR + bob), "scale": (S, S)}


keys(L, range(241, 301), sneak)
pins(L, [(150, 470), (520, 470), (330, 300)],
     [((510, 170), (430, 260), lambda f: sway(f, 0.7, 2)), ((60, 220), (200, 230), lambda f: sway(f, 0.4, 5))],
     every(241, 300))

# Б6: тычок лапой
L = layer("b6_poke", cut("key", 6), 301, 326, (330, 600))
keys(L, range(301, 327), lambda f: {"pos": (680 - 28 * math.sin(math.pi * min(1, max(0, (f - 304) / 14))), FLOOR),
                                     "scale": (S, S)})
pins(L, [(200, 590), (500, 590), (350, 400)], [((620, 60), (550, 250), lambda f: sway(f, 1.2, 5))], every(301, 326))

# Б7: отпрыгнул назад
L = layer("b7_hop", cut("key", 4), 327, 342, (300, 515), motionBlur=True)
keys(L, range(327, 343), lambda f: {"pos": (680 + 260 * min(1, (f - 327) / 11), FLOOR - 130 * math.sin(math.pi * min(1, (f - 327) / 11))),
                                     "scale": (S * 1.1, S * 0.88) if f >= 338 else (S * 0.94, S * 1.08)})

# Б8: умывается как ни в чём не бывало
L = layer("b8_groom", cut("key", 7), 343, 432, (330, 570))
keys(L, every(343, 432, 4), lambda f: {"pos": (1180, FLOOR), "scale": tuple(S * v for v in breathe(f, 0.6))})
pins(L, [(150, 560), (450, 560), (300, 430)],
     [((390, 250), (320, 330), lambda f: sway(f, 2.4, 4) if (f - 343) % 36 < 26 else 0)], every(343, 432))

# Б9: «ты ничего не видел»
L = layer("b9_sideeye", cut("key", 8), 433, 519, (250, 570))
keys(L, every(433, 519, 4), lambda f: {"pos": (1180, FLOOR), "scale": tuple(S * v for v in breathe(f, 0.5))})
pins(L, [(120, 560), (420, 560), (250, 430)], [((260, 180), (250, 300), lambda f: sway(f, 0.3, 1.5))], every(433, 519, 3))

# Б10: пятится… упирается в первый огурец
L = layer("b10_back", cut("extra", 1), 520, TOUCH + 6, (330, 410))


def back(f):
    u = min(1.0, max(0.0, (f - 528) / (TOUCH - 528)))
    return {"pos": (1180 - (1180 - X_TOUCH) * u, FLOOR - (6 * abs(math.sin(math.pi * 3 * u)) if f < TOUCH else 0)),
            "scale": (S, S)}


keys(L, every(520, TOUCH + 6, 2), back)
pins(L, [(200, 400), (560, 400), (400, 250)],
     [((50, 190), (180, 190), lambda f: sway(f, 0.5, 4) if f < TOUCH else 18)], every(520, TOUCH + 6))

# третий испуг — вверх из кадра
L = layer("b10_out", cut("key", 3), TOUCH + 7, TOUCH + 18, (330, 330), motionBlur=True)
keys(L, range(TOUCH + 7, TOUCH + 19), lambda f: {"pos": (X_TOUCH + 60, FLOOR - 270 - 1100 * ((f - TOUCH - 7) / 11) ** 1.3),
                                                  "scale": (S * 0.9, S * 1.15), "rot": 8})

# ---------------------------------------------------------------- руки


def hand_layers(prefix, x, track, seq):
    """seq: [(кадр с, кадр по, номер рисунка)]; track(f) -> y хвата."""
    for f0, f1, i in seq:
        p = CUT / "hands_ext" / f"hands_ext_{i:02d}.png"
        w, h = size(p)
        L = layer(f"{prefix}_{i}", p, f0, f1, (w * 0.42, h - 10), scale=[[0, 62, 62]])
        for f in range(f0, f1 + 1):
            L["pos"].append([t(f), x + 40, track(f)])


def ytrack(points):
    def fn(f):
        for (f0, y0), (f1, y1) in zip(points, points[1:]):
            if f <= f1:
                return y0 + (y1 - y0) * smooth((f - f0) / (f1 - f0)) if f1 > f0 else y1
        return points[-1][1]
    return fn


hand_layers("hand1", CUC1, ytrack([(30, -700), (42, 250), (48, 250), (60, 600), (66, 600), (78, 975), (88, 975), (110, -700)]),
            [(30, 81, 1), (82, 85, 2), (86, 110, 3)])
hand_layers("hand2", CUC2, ytrack([(484, -700), (494, 300), (500, 300), (512, 975), (522, 975), (544, -700)]),
            [(484, 515, 1), (516, 519, 2), (520, 544, 3)])

# ---------------------------------------------------------------- крупные планы (без камеры)
k = W / 1700
layer("close_bg", ROOM, 145, 168, (rw / 2, rh / 2), parent=None,
      pos=[[0, (rw / 2 - 700) * k, (rh / 2 - 300) * k]], scale=[[0, k * 100, k * 100]])
# морды — векторные (VectorCraft imageTrace, режим logo): в 2,5 раза крупнее без мыла
VEC = HERE / "ec" / "vector"
L = layer("close_look", VEC / "extra_04.svg", 145, 157, (260, 470), parent=None, svg=True,
          pos=[[0, 980, 1110]], scale=[[0, 150, 150]])
L["rot"] = [[t(145), -3], [t(157), 1]]
layer("close_take", VEC / "extra_06.svg", 158, 168, (276, 396), parent=None, svg=True, pos=[[0, 960, 1100]],
      scale=[[t(158), 260, 260], [t(161), 240, 240]])

# камера: медленный наезд в Б9 (вокруг точки морды)
q, c0 = (1180, 700), (960, 540)
cam = {"pos": [[t(440), *c0]], "scale": [[t(440), 100, 100]]}
for f in range(441, 521, 3):
    z = 1 + 0.22 * min(1, (f - 440) / 50) if f <= 519 else 1
    cam["pos"].append([t(f), q[0] - z * (q[0] - c0[0]), q[1] - z * (q[1] - c0[1])])
    cam["scale"].append([t(f), z * 100, z * 100])
cam["pos"].append([t(520), *c0])
cam["scale"].append([t(520), 100, 100])

json.dump({"fps": FPS, "duration": LAST / FPS, "size": [W, H], "cam": cam, "layers": LAYERS},
          open(HERE / "ec" / "ep1_keys.json", "w", encoding="utf-8"))
print("слоёв:", len(LAYERS), "булавок:", sum(len(L["pins"]) for L in LAYERS),
      "ключей булавок:", sum(len(p["keys"]) for L in LAYERS for p in L["pins"]))
