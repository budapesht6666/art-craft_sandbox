"""Шот «DON'T LOOK.» -> ключи для EffectCraft: python gen_shot.py -> ec/shot_keys.json.

Позы Gemini сменяют друг друга заменой, движение — шаги, «поп» при смене позы, дрожь,
камень снизу вверх (Linear Wipe поверх крика), тряска камеры. Строит build_shot.js.
Тайминг — по словам голоса (voice/words_raw.json, дубль 2, монтаж в sound/mix.py):
«a head» 5,17 с; «The instructions» 10,6; «don't» 12,93; «look,» конец 13,63;
вставленная пауза 14,15–15,55; «the guards» 16,1; «instructions.» конец 19,35.
"""
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).parent
ASSETS = HERE / "ec" / "assets"
BG = HERE.parent / "gemini" / "sheets" / "01_bg_lair_v2.png"
FPS, DUR = 24, 20.8
W, H = 1920, 1080
A = json.loads((ASSETS / "anchors.json").read_text(encoding="utf-8"))
K2 = 58.6                  # масштаб фигур листа 2, %
K0 = K2 * 0.549            # лист 0 нарисован крупнее
P_X, P_Y = 620, 928        # ступни Персея
S_X, S_Y = 1330, 907       # ступни воина
T_WALK = 3.0               # Персей дошёл
T_HOLD = 5.17              # «a head» — показывает голову
T_PUSH0, T_PUSH1 = 10.6, 12.9   # «The instructions were simple» — наезд
T_TITLE = 12.93            # «don't»
T_SCREAM = 13.75           # после «look,»
T_STONE, T_DONE = 14.4, 15.3
T_TITLE_OUT = 16.0         # перед «the guards»
T_WIN = 19.2               # после «instructions.»
random.seed(7)


def fr(t0, t1, step=1):
    return [round(f / FPS, 5) for f in range(round(t0 * FPS), round(t1 * FPS) + 1, step)]


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def pop(t, t0, k):
    """Сплющить-растянуть при смене позы: 0,25 с, затухающая пружина."""
    u = (t - t0) / 0.25
    if u < 0 or u > 1:
        return k, k
    s = 0.07 * math.cos(math.pi * 2 * u) * (1 - u)
    return k * (1 + s), k * (1 - s)


LAYERS = []


def layer(name, t0, t1, **kw):
    src = kw.pop("src", None) or ASSETS / f"{name}.png"
    L = {"name": name, "src": str(src).replace("\\", "/"), "in": t0, "out": t1, "anchor": None,
         "pos": [], "scale": [], "rot": [], "opacity": [], "wipe": None, "parent": "cam"}
    if name in A:
        L["anchor"] = A[name]["feet"]
    L.update(kw)
    LAYERS.append(L)
    return L


# фон
layer("bg", 0, DUR, src=BG, anchor=[1376, 768], pos=[[0, W / 2, H / 2]], scale=[[0, 69.767, 69.767]])

# Персей крадётся (шаги 2,5 в секунду), потом стоит и нервно дышит
L = layer("perseus_sneak", 0, T_HOLD)
for t in fr(0, T_HOLD):
    if t < T_WALK:
        u = t / T_WALK
        ph = 2 * math.pi * 2.5 * t
        L["pos"].append([t, 430 + (P_X - 430) * (1 - (1 - u) ** 2), P_Y - 9 * abs(math.sin(ph / 2))])
        L["rot"].append([t, 2.2 * math.sin(ph / 2) * (1 - u * 0.5)])
        L["scale"].append([t, K2, K2])
    else:
        b = math.sin(2 * math.pi * 1.4 * (t - T_WALK))
        L["pos"].append([t, P_X, P_Y])
        L["rot"].append([t, 0.6 * math.sin(2 * math.pi * 0.7 * (t - T_WALK))])
        L["scale"].append([t, K2 * (1 - 0.006 * b), K2 * (1 + 0.012 * b)])

# Персей протягивает голову: поп, мелкая нервная дрожь
L = layer("perseus_hold", T_HOLD, T_WIN, pos=[[0, P_X, P_Y]])
for t in fr(T_HOLD, T_WIN):
    sx, sy = pop(t, T_HOLD, K2)
    L["scale"].append([t, sx, sy])
    L["rot"].append([t, 0.8 * math.sin(2 * math.pi * 7 * t)])

# Персей торжествует
L = layer("perseus_win", T_WIN, DUR, pos=[[0, P_X + 10, P_Y]])
for t in fr(T_WIN, DUR):
    sx, sy = pop(t, T_WIN, K2)
    b = 1 + 0.012 * math.sin(2 * math.pi * 1.2 * (t - T_WIN))
    L["scale"].append([t, sx, sy * b])

# Воин хмуро стоит и дышит
L = layer("soldier_idle", 0, T_SCREAM, pos=[[0, S_X, S_Y]])
for t in fr(0, T_SCREAM, 2):
    b = math.sin(2 * math.pi * 0.9 * t)
    L["scale"].append([t, K0 * (1 - 0.006 * b), K0 * (1 + 0.012 * b)])

# Воин кричит: поп и дрожь до начала окаменения
shake = {t: (random.uniform(-5, 5), random.uniform(-3, 3)) for t in fr(T_SCREAM, T_STONE)}
L = layer("soldier_scream", T_SCREAM, T_DONE + 0.1)
for t in fr(T_SCREAM, T_DONE + 0.1):
    dx, dy = shake.get(t, (0, 0))
    L["pos"].append([t, S_X + dx, S_Y + dy])
    sx, sy = pop(t, T_SCREAM, K2)
    L["scale"].append([t, sx, sy])

# Камень поднимается снизу вверх поверх крика
layer("soldier_stone", T_STONE, DUR, pos=[[0, S_X, S_Y]], scale=[[0, K2, K2]],
      wipe={"angle": 180, "feather": 40, "keys": [[T_STONE, 100], [T_DONE, 0]]})

SOLIDS = [  # вспышка взгляда Медузы
    {"name": "flash", "color": [1.0, 0.92, 0.55], "in": T_STONE - 0.05, "out": T_STONE + 0.4,
     "opacity": [[T_STONE - 0.05, 0], [T_STONE, 25], [T_STONE + 0.35, 0]]},
]

TEXTS = [
    {"text": "DON'T LOOK.", "in": T_TITLE, "out": T_TITLE_OUT + 0.3, "size": 100, "pos": [W / 2, 1040],
     "scale": [[T_TITLE, 150, 150], [T_TITLE + 0.12, 94, 94], [T_TITLE + 0.22, 100, 100]],
     "opacity": [[T_TITLE_OUT, 100], [T_TITLE_OUT + 0.3, 0]]},
]

# камера: медленный наезд, рывок на «a head», наезд на «instructions», тряска, отъезд на финале
cam = {"anchor": [980, 760], "pos": [], "scale": []}
for t in fr(0, DUR):
    if t < T_HOLD:
        s = 100 + 2 * t / T_HOLD
    elif t < T_WIN:
        s = 102 + 3 * smooth((t - T_HOLD) / 0.12) + 5 * smooth((t - T_PUSH0) / (T_PUSH1 - T_PUSH0))
    else:
        s = 110 - 5 * smooth((t - T_WIN) / 0.6)
    cam["scale"].append([t, s, s])
    dx = dy = 0
    if T_STONE <= t <= T_DONE:
        k = 1 - (t - T_STONE) / (T_DONE - T_STONE) * 0.6
        dx, dy = random.uniform(-7, 7) * k, random.uniform(-5, 5) * k
    cam["pos"].append([t, 980 + dx, 760 + dy])

data = {"fps": FPS, "duration": DUR, "size": [W, H], "cam": cam, "layers": LAYERS,
        "solids": SOLIDS, "texts": TEXTS}
(HERE / "ec" / "shot_keys.json").write_text(json.dumps(data), encoding="utf-8")
print("layers", len(LAYERS), "keys", sum(len(L["pos"]) + len(L["scale"]) + len(L["rot"]) for L in LAYERS))
