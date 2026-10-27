"""Звук теста «лазер»: python sfx_test.py -> sfx_test.wav (9 с ролика + 2,5 с титра). Кадры 24 к/с, как в fluk2d.py.

Живые голоса кота — CC0, Kerzoven, opengameart.org/content/cat-purr-meow (лежат в sounds_dl/).
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, resample_poly, sosfilt

SR, DUR = 48000, 11.5
rng = np.random.default_rng(11)
mix = np.zeros(int(SR * DUR))


def put(sig, frame, gain=1.0):
    i = int(frame / 24 * SR)
    n = min(len(sig), len(mix) - i)
    mix[i:i + n] += sig[:n] * gain


def band(x, lo=None, hi=None):
    kind, f = ("bandpass", [lo, hi]) if lo and hi else (("highpass", lo) if lo else ("lowpass", hi))
    return sosfilt(butter(4, f, kind, fs=SR, output="sos"), x)


def env(n, a=0.002, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def pluck(freq, dur=0.6):
    n, p = int(dur * SR), int(SR / freq)
    buf, out = rng.uniform(-1, 1, p), np.empty(int(dur * SR))
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.994
    return band(out, hi=3000) * env(n, 0.001, 0.25)


def glide(f0, f1, dur, vib=0.0):
    t = np.arange(int(dur * SR)) / SR
    f = np.linspace(f0, f1, len(t)) * (1 + vib * np.sin(2 * np.pi * 6 * t))
    fade = np.minimum(1, np.minimum(t / 0.01, (dur - t) / 0.04))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * fade


def thump():
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(70 - 25 * t / 0.4) / SR) * env(n, 0.002, 0.1) \
        + band(rng.standard_normal(n), hi=300) * env(n, 0.001, 0.04) * 0.5


def purr(dur):
    t = np.arange(int(dur * SR)) / SR
    am = (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t)) ** 2
    return band(rng.standard_normal(len(t)), 40, 400) * am * np.minimum(1, np.minimum(t / 0.3, (dur - t) / 0.4))


def whoosh(dur):
    t = np.arange(int(dur * SR)) / SR
    return band(rng.standard_normal(len(t)), 500, 4000) * np.sin(np.pi * t / dur) ** 2


def rattle(dur):
    out = np.zeros(int(dur * SR))
    for k in np.arange(0, dur, 1 / 12):
        b = band(rng.standard_normal(int(0.02 * SR)), 2000, 7000) * env(int(0.02 * SR), 0.0005, 0.004)
        i = int(k * SR)
        out[i:i + len(b)] += b[:len(out) - i]
    return out


def clip(name, t0, t1, fade=0.03):
    """Кусок живой записи (44,1 кГц) -> 48 кГц, с плавными краями, пик 1."""
    sr, x = wavfile.read(f"sounds_dl/{name}.wav")
    x = x[int(t0 * sr):int(t1 * sr)].astype(float)
    x = resample_poly(x, 160, 147)
    n = int(fade * SR)
    ramp = np.linspace(0, 1, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x / np.max(np.abs(x))


N = {"A2": 110.0, "C3": 130.8, "D3": 146.8, "E3": 164.8, "F3": 174.6, "A3": 220.0, "C4": 261.6, "E4": 329.6, "A4": 440.0}
put(glide(700, 1300, 0.18), 12, 0.25)                       # лазер появился
put(clip("cat_mewfood", 0.58, 0.86), 27, 0.55)               # «чирик» на добычу
for f, n in ((36, "A2"), (44, "C3"), (52, "D3")):             # пригнулся
    put(pluck(N[n]), f, 0.55)
put(rattle(1.1), 60, 0.25)                                   # виляет попой
for f, n in ((60, "E3"), (66, "F3"), (72, "E3"), (78, "F3"), (84, "E3")):
    put(pluck(N[n], 0.3), f, 0.4)
put(whoosh(0.4), 92, 0.6)                                    # прыжок
put(glide(450, 1300, 0.25, 0.02), 92, 0.18)
put(glide(1300, 650, 0.25, 0.02), 98, 0.18)
put(thump(), 106, 0.9)                                       # приземление
put(clip("cat_purractive_loop", 1.0, 2.6, 0.2), 114, 0.5)     # живое мурчание
put(glide(500, 900, 0.22), 146, 0.15)                        # лапа вверх
put(clip("cat_softmew", 0.33, 1.23), 158, 0.6)               # «мяу?» — под лапой пусто
put(glide(700, 1300, 0.18), 174, 0.25)                       # точка на спине
put(glide(900, 600, 0.3), 182, 0.12)                         # глаза ползут назад
put(clip("cat_mewfood", 0.0, 0.37), 190, 0.75)               # испуганный «мяв»
put(pluck(N["A2"]), 191, 0.6)
put(pluck(N["E3"] * 1.06), 191, 0.4)
for k, n in enumerate(("A3", "C4", "E4", "A4")):              # джингл под титр
    put(pluck(N[n]), 216 + 6 + k * 4, 0.45)

mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
wavfile.write("sfx_test.wav", SR, (mix * 32767).astype(np.int16))
print("ok")
