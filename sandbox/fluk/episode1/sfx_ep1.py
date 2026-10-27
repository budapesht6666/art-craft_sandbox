"""Звук «Fluk — Episode 1: The Cucumber» (ep1.py): python sfx_ep1.py -> sfx_ep1.wav.

620 кадров (25,8 с) + 2,5 с титра. Кадры 24 к/с. Движения — синтез (sound/synth.py),
голос Флюка — живые записи CC0 (sound/cc0).
"""
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "sound"))
import synth as S  # noqa: E402

SR, DUR = S.SR, 28.6
STEMS = {k: np.zeros(int(SR * DUR)) for k in ("foley", "voice", "music", "ambience")}
mix = STEMS["music"]
rng = np.random.default_rng(9)
_stem = "music"


def stem(name):
    """Дальнейшие put() идут в дорожку name."""
    global _stem
    _stem = name


def put(sig, frame, gain=1.0):
    track = STEMS[_stem]
    i = int(frame / 24 * SR)
    n = min(len(sig), len(track) - i)
    track[i:i + n] += sig[:n] * gain


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def crunch():
    out = np.zeros(int(0.12 * SR))
    for k in range(3):
        b = S.band(noise(0.025), 1500, 5000) * S.env(int(0.025 * SR), 0.001, 0.006)
        i = int(k * 0.035 * SR)
        out[i:i + len(b)] += b * rng.uniform(0.5, 1.0)
    return out


def tok():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 520 * t) + 0.5 * np.sin(2 * np.pi * 1340 * t)) * S.env(n, 0.0005, 0.03)


def clang():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
               for f, a, d in ((610, 0.6, 0.6), (1530, 0.4, 0.35), (2480, 0.25, 0.2), (3900, 0.15, 0.12)))


def sting():
    t = np.arange(int(1.0 * SR)) / SR
    chord = sum(np.sign(np.sin(2 * np.pi * f * t)) * 0.25 for f in (110, 116.5, 155.6, 233.1))
    return (S.band(chord, hi=2500) + S.band(noise(1.0), 2000, 9000) * 0.5) * S.env(len(t), 0.003, 0.25)


def lick():
    n = int(0.06 * SR)
    return S.band(noise(0.06), 1200, 5000) * np.sin(np.pi * np.arange(n) / n) ** 2


def cricket():
    out = np.zeros(int(0.5 * SR))
    for k in range(3):
        n = int(0.04 * SR)
        t = np.arange(n) / SR
        out[int(k * 0.06 * SR):int(k * 0.06 * SR) + n] += np.sin(2 * np.pi * 4600 * t) * np.sin(np.pi * t / (n / SR))
    return out


N = S.N
# Б1: ест, рука крадётся
for f in range(4, 97, 12):
    stem("foley")
    put(crunch(), f, 0.35)
for f, n in ((30, "A2"), (36, "C3"), (42, "E3"), (48, "D3"), (54, "F3"), (60, "A3"), (66, "C3"), (72, "E3"),
             (78, "A3")):
    stem("music")
    put(S.pluck(N[n]), f, 0.5)
stem("foley")
put(tok(), 85, 0.3)
for f, n in ((90, "C4"), (95, "A3"), (100, "E3")):
    stem("music")
    put(S.pluck(N[n]), f, 0.35)
# Б2: облизывается, мурчит
stem("voice")
put(S.clip("cat_purractive_loop", 1.0, 2.8, 0.25), 100, 0.5)
# Б3: оглянулся — пауза — «тейк»
stem("music")
put(S.glide(600, 480, 0.25), 146, 0.08)
stem("music")
put(S.pluck(N["A4"]), 158, 0.55)
# Б4: взрыв
stem("music")
put(sting(), 169, 0.45)
stem("voice")
put(S.clip("cat_mewfood", 0.0, 0.37), 169, 0.85)
stem("foley")
put(S.whoosh(0.35), 170, 0.5)
stem("foley")
put(clang(), 171, 0.35)
stem("foley")
put(clang(), 185, 0.45)
stem("foley")
put(S.thump(), 187, 0.9)
# Б5: застыл — неловкая тишина
for f in (205, 221):
    stem("ambience")
    put(cricket(), f, 0.12)
# Б6: крадётся, тычок
for f in (241, 268, 289):
    stem("music")
    put(S.pluck(N["E3"], 0.3), f, 0.35)
stem("foley")
put(tok(), 310, 0.5)
stem("voice")
put(S.clip("cat_mewfood", 0.58, 0.86), 312, 0.5)
# Б7: отпрыгнул
stem("foley")
put(S.whoosh(0.25), 327, 0.4)
stem("foley")
put(S.thump(), 338, 0.5)
# Б8: умывается
for start in range(343, 432, 36):
    for k in range(0, 26, 5):
        stem("foley")
        put(lick(), start + k, 0.35)
# Б9: «ты ничего не видел»
stem("music")
put(S.pluck(N["A2"]), 440, 0.55)
# Б10: второй огурец, пятится — тишина, потом джингл под титр
for f, n in ((486, "A2"), (494, "C3"), (502, "E3"), (510, "A3")):
    stem("music")
    put(S.pluck(N[n]), f, 0.45)
stem("foley")
put(tok(), 519, 0.3)
stem("foley")
put(tok(), 562, 0.4)                                         # упёрся в первый огурец
stem("music")
put(sting(), 569, 0.5)                                       # третий испуг
stem("voice")
put(S.clip("cat_mewpurr", 0.0, 1.0), 569, 0.8)
stem("music")
put(S.glide(500, 1600, 0.45, 0.03), 569, 0.2)
for k, n in enumerate(("A3", "C4", "E4", "A4")):
    stem("music")
    put(S.pluck(N[n]), 626 + k * 4, 0.45)

peak = max(np.max(np.abs(v)) for v in STEMS.values())
(HERE / "stems").mkdir(exist_ok=True)
for name, v in STEMS.items():   # общий масштаб: соотношения дорожек сохраняются, сводит SoundCraft
    wavfile.write(HERE / "stems" / f"{name}.wav", SR, (v * 10 ** (-1 / 20) / peak * 32767).astype(np.int16))
total = sum(STEMS.values())
wavfile.write(HERE / "sfx_ep1.wav", SR, (total * 10 ** (-1 / 20) / np.max(np.abs(total)) * 32767).astype(np.int16))
print("ok")
