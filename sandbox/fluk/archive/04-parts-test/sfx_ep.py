"""Звук теста: python sfx_ep.py -> sfx_ep.wav (200 кадров = 8,33 с + 2,5 с титра)."""
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "sound"))
import synth as S  # noqa: E402

SR, DUR = S.SR, 10.9
mix = np.zeros(int(SR * DUR))
rng = np.random.default_rng(3)


def put(sig, frame, gain=1.0):
    i = int(frame / 24 * SR)
    n = min(len(sig), len(mix) - i)
    mix[i:i + n] += sig[:n] * gain


def hiss(dur=0.7):
    t = np.arange(int(dur * SR)) / SR
    return S.band(rng.standard_normal(len(t)), 2500, 9000) * np.minimum(1, t / 0.03) * np.exp(-t / 0.35)


def tok():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 520 * t) + 0.5 * np.sin(2 * np.pi * 1340 * t)) * S.env(n, 0.0005, 0.03)


N = S.N
for f, n in ((36, "A2"), (42, "C3"), (48, "E3"), (54, "D3"), (60, "F3"), (66, "A3"), (72, "C3"), (78, "E3"),
             (84, "A3")):
    put(S.pluck(N[n]), f, 0.5)                      # рука крадётся
put(tok(), 95, 0.35)                                # огурец на полу
for f, n in ((100, "C4"), (104, "A3"), (108, "E3")):
    put(S.pluck(N[n]), f, 0.35)
put(S.glide(500, 900, 0.18), 110, 0.12)            # заметил
put(S.clip("cat_mewfood", 0.0, 0.37), 118, 0.85)   # испуганный «мяв»
put(S.whoosh(0.35), 120, 0.5)
put(S.glide(450, 1300, 0.3, 0.02), 120, 0.18)
put(S.thump(), 140, 0.9)
put(hiss(), 146, 0.6)                               # шипит на огурец
put(S.pluck(N["A2"]), 164, 0.6)                     # злой взгляд в камеру
for k, n in enumerate(("A3", "C4", "E4", "A4")):     # джингл под титр
    put(S.pluck(N[n]), 206 + k * 4, 0.45)
mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
wavfile.write(HERE / "sfx_ep.wav", SR, (mix * 32767).astype(np.int16))
print("ok")
