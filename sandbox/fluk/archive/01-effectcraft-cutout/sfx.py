"""Звук пилота: все эффекты синтезированы здесь, без чужих сэмплов.

python sfx.py  ->  fluk_sfx.wav (48 кГц, моно, 40 с)

Времена совпадают с ключами в build_scene.js.
"""
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
DUR = 40.0
rng = np.random.default_rng(7)
mix = np.zeros(int(SR * DUR))


def put(sig, t, gain=1.0):
    i = int(t * SR)
    n = min(len(sig), len(mix) - i)
    mix[i:i + n] += sig[:n] * gain


def band(x, lo=None, hi=None, order=4):
    if lo and hi:
        sos = butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo:
        sos = butter(order, lo, "highpass", fs=SR, output="sos")
    else:
        sos = butter(order, hi, "lowpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def env(n, attack=0.002, decay=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def pluck(freq, dur=0.6):
    """Пиццикато по алгоритму Карплуса — Стронга."""
    n, p = int(dur * SR), int(SR / freq)
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.994
    return band(out, hi=3000) * env(n, 0.001, 0.25)


def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2,
             "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440 * 2 ** ((names[name[:-1]] + 12 * (int(name[-1]) - 4)) / 12)


def crunch():
    out = np.zeros(int(0.12 * SR))
    for k in range(3):
        b = band(noise(0.025), 1500, 5000) * env(int(0.025 * SR), 0.001, 0.006)
        i = int(k * 0.035 * SR)
        out[i:i + len(b)] += b * rng.uniform(0.5, 1.0)
    return out


def tap(freq_hi=4000):
    return band(noise(0.04), 300, freq_hi) * env(int(0.04 * SR), 0.0005, 0.008)


def purr(dur):
    t = np.arange(int(dur * SR)) / SR
    am = (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t)) ** 2
    fade = np.minimum(1, np.minimum(t / 0.3, (dur - t) / 0.4))
    return band(noise(dur), 40, 400) * am * fade


def sting():
    t = np.arange(int(1.3 * SR)) / SR
    chord = sum(np.sign(np.sin(2 * np.pi * f * t)) * 0.25 for f in (110, 116.5, 155.6, 233.1))
    crash = band(noise(1.3), 2000, 9000) * 0.5
    return (band(chord, hi=2500) + crash) * env(len(t), 0.003, 0.35)


def whistle(t0, f0, t1, f1, t2, f2):
    n = int((t2 - t0) * SR)
    t = np.arange(n) / SR
    f = np.interp(t, [0, t1 - t0, t2 - t0], [f0, f1, f2]) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    fade = np.minimum(1, np.minimum(t / 0.02, (n / SR - t) / 0.05))
    return np.sin(ph) * fade


def thump():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 75 - 30 * t / 0.45
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.12)
    return body + band(noise(0.45), hi=300) * env(n, 0.001, 0.05) * 0.6


def tick(freq):
    n = int(0.04 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env(n, 0.0005, 0.006) + tap(8000) * 0.4


def clink():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
               for f, a, d in ((1180, 0.6, 0.9), (2950, 0.35, 0.5), (4870, 0.2, 0.3))) * np.minimum(1, t / 0.001)


def cricket():
    out = np.zeros(int(0.5 * SR))
    for k in range(3):
        n = int(0.04 * SR)
        t = np.arange(n) / SR
        b = np.sin(2 * np.pi * 4600 * t) * np.sin(np.pi * t / (n / SR))
        i = int(k * 0.06 * SR)
        out[i:i + n] += b
    return out


def whoosh(dur=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = band(noise(dur), 400, 3000) * np.sin(np.pi * t / dur) ** 2
    return x


def glock(freq, dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.76 * t)) * env(n, 0.001, 0.35)


# 0–9.3: хруст на каждом опускании головы
t = 0.0
while t < 9.3:
    put(crunch(), t + 0.02, 0.35)
    t += 0.5
put(tap(9000), 3.0, 0.08)    # ухо дёрнулось

# 4.0–8.6: крадущееся пиццикато под шаги руки
for tt, nm in ((4.0, "A2"), (4.25, "C3"), (4.5, "E3"),
               (4.9, "B2"), (5.15, "D3"), (5.4, "F3"),
               (5.8, "C3"), (6.0, "D#3"), (6.2, "F#3"), (6.4, "A3"), (6.6, "C4")):
    put(pluck(note(nm)), tt, 0.55)
put(tap(), 6.62, 0.25)       # огурец лёг на пол
for tt, nm in ((7.4, "C4"), (7.55, "A3"), (7.7, "E3")):
    put(pluck(note(nm)), tt, 0.45)

put(purr(1.6), 10.0, 0.22)   # блаженство
put(tap(9000), 13.2, 0.08)   # ухо

put(sting(), 16.0, 0.55)     # «Что?!»
put(whistle(16.8, 500, 17.1, 1400, 17.4, 700), 16.8, 0.25)  # прыжок
put(thump(), 17.4, 0.9)      # приземление

for k, tt in enumerate(np.arange(18.3, 26.0, 1.0)):   # тиканье часов
    put(tick(2000 if k % 2 == 0 else 1600), tt, 0.25)

for tt, nm in ((26.0, "A2"), (26.35, "C3"), (26.7, "E3"), (27.05, "G3"), (27.4, "A3")):
    put(pluck(note(nm)), tt, 0.5)
put(tap(), 27.6, 0.2)        # взял огурец
for tt, nm in ((27.8, "E3"), (28.4, "A3"), (29.0, "C4")):
    put(pluck(note(nm)), tt, 0.45)
put(clink(), 29.4, 0.45)     # огурец в миске
for tt, nm in ((29.7, "C4"), (29.85, "A3"), (30.0, "E3")):
    put(pluck(note(nm)), tt, 0.4)

for tt in (32.0, 32.7, 33.4):    # неловкая тишина
    put(cricket(), tt, 0.12)
put(whoosh(), 35.8, 0.5)     # обиженно отвернулся

for tt, nm in ((37.4, "A2"), (37.6, "E3"), (37.8, "A3")):
    put(pluck(note(nm)), tt, 0.5)
for tt, nm in ((38.0, "C#5"), (38.15, "E5"), (38.3, "A5")):
    put(glock(note(nm)), tt, 0.25)

mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
wavfile.write("fluk_sfx.wav", SR, (mix * 32767).astype(np.int16))
print("ok", round(len(mix) / SR, 2), "s")
