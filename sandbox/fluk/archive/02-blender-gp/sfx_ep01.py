"""Звук «Fluk — Episode 1: The Cucumber»: python sfx_ep01.py -> sfx_ep01.wav (27,5 с + 2,5 с титра).

Кадры 24 к/с, как в ep01_cucumber.py. Движения — синтез, голос Флюка — живые записи CC0
(Kerzoven, opengameart.org/content/cat-purr-meow, лежат в sounds_dl/).
"""
import numpy as np
from scipy.io import wavfile

import sfx_test as S   # общие синтезаторы; сам модуль при импорте пишет sfx_test.wav

SR, DUR = S.SR, 30.0
mix = np.zeros(int(SR * DUR))
rng = np.random.default_rng(5)


def put(sig, frame, gain=1.0):
    i = int(frame / 24 * SR)
    n = min(len(sig), len(mix) - i)
    mix[i:i + n] += sig[:n] * gain


def crunch():
    out = np.zeros(int(0.12 * SR))
    for k in range(3):
        b = S.band(rng.standard_normal(int(0.025 * SR)), 1500, 5000) * S.env(int(0.025 * SR), 0.001, 0.006)
        i = int(k * 0.035 * SR)
        out[i:i + len(b)] += b * rng.uniform(0.5, 1.0)
    return out


def sniff():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return S.band(rng.standard_normal(n), 800, 4000) * np.sin(np.pi * t / (n / SR)) ** 2


def tok():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 520 * t) + 0.5 * np.sin(2 * np.pi * 1340 * t)) * S.env(n, 0.0005, 0.03)


def rumble(dur):
    t = np.arange(int(dur * SR)) / SR
    return S.band(rng.standard_normal(len(t)), 60, 400) * np.sin(np.pi * t / dur)


def sting():
    t = np.arange(int(1.2 * SR)) / SR
    chord = sum(np.sign(np.sin(2 * np.pi * f * t)) * 0.25 for f in (110, 116.5, 155.6, 233.1))
    crash = S.band(rng.standard_normal(len(t)), 2000, 9000) * 0.5
    return (S.band(chord, hi=2500) + crash) * S.env(len(t), 0.003, 0.3)


N = S.N
# 0–150: ест — хруст на каждом «кивке» (шея качается с периодом 12 кадров)
for f in range(3, 150, 12):
    put(crunch(), f, 0.35)
# рука крадётся ступеньками
for f, n in ((40, "A2"), (46, "C3"), (52, "E3"), (60, "D3"), (66, "F3"), (72, "A3"), (80, "C3"), (86, "E3"),
             (92, "A3"), (96, "C4")):
    put(S.pluck(N[n]), f, 0.5)
put(tok(), 97, 0.25)                                         # огурец лёг на пол
for f, n in ((104, "C4"), (110, "A3"), (116, "E3")):
    put(S.pluck(N[n]), f, 0.4)
put(S.clip("cat_purractive_loop", 1.0, 3.0, 0.25), 160, 0.5)  # сытое мурчание
put(S.glide(500, 900, 0.15), 216, 0.08)                      # ухо дёрнулось
put(S.glide(700, 520, 0.3), 224, 0.12)                       # оглядывается
put(sting(), 246, 0.5)                                       # «Что?!»
put(S.clip("cat_mewfood", 0.0, 0.37), 247, 0.8)
put(S.whoosh(0.4), 254, 0.5)
put(S.glide(450, 1400, 0.45, 0.02), 254, 0.2)
put(S.thump(), 276, 0.9)
for f in range(300, 330, 6):                                 # напряжение
    put(S.pluck(N["A2"], 0.25), f, 0.35)
put(S.whoosh(0.2), 332, 0.35)                                # развернулся
for f in list(range(340, 385, 10)) + list(range(408, 450, 10)):   # крадётся
    put(S.pluck(N["E3"] if (f // 10) % 2 else N["C3"], 0.35), f, 0.35)
for f in (462, 471, 480, 489):                               # нюхает
    put(sniff(), f, 0.35)
put(tok(), 514, 0.5)                                         # тычок
put(rumble(0.6), 515, 0.35)                                  # огурец откатился
put(S.clip("cat_mewfood", 0.58, 0.86), 515, 0.6)
put(S.clip("cat_softmew", 1.32, 2.06), 536, 0.45)            # «ну и?»
for f, n in ((566, "A3"), (575, "C4"), (584, "E4"), (593, "C4"), (602, "E4")):   # гордо уходит
    put(S.pluck(N[n], 0.35), f, 0.4)
put(rumble(0.5), 604, 0.3)                                   # огурец катится следом
put(tok(), 614, 0.35)
put(sting(), 616, 0.35)
put(S.clip("cat_mewpurr", 0.0, 1.0), 617, 0.6)
put(S.whoosh(0.35), 624, 0.6)                                # удирает
for k, n in enumerate(("E4", "C4", "A3", "E3")):
    put(S.pluck(N[n], 0.3), 624 + k * 3, 0.4)
for k, n in enumerate(("A3", "C4", "E4", "A4")):              # джингл под титр
    put(S.pluck(N[n]), 666 + k * 4, 0.45)

mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
wavfile.write("sfx_ep01.wav", SR, (mix * 32767).astype(np.int16))
print("ok")
