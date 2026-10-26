"""Общие звуки Флюка: синтез (щипки, свист, удар, шорох, мурчание) и куски живых записей.

Живые голоса кота — CC0, Kerzoven, opengameart.org/content/cat-purr-meow, лежат в cc0/.
"""
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, resample_poly, sosfilt

SR = 48000
CC0 = Path(__file__).parent / "cc0"
rng = np.random.default_rng(11)


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
    sr, x = wavfile.read(CC0 / f"{name}.wav")
    x = x[int(t0 * sr):int(t1 * sr)].astype(float)
    x = resample_poly(x, 160, 147)
    n = int(fade * SR)
    ramp = np.linspace(0, 1, n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x / np.max(np.abs(x))


N = {"A2": 110.0, "C3": 130.8, "D3": 146.8, "E3": 164.8, "F3": 174.6, "A3": 220.0, "C4": 261.6, "E4": 329.6, "A4": 440.0}
