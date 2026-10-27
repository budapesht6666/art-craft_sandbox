"""Субтитры шота: python subs.py -> out/dont_look.en.srt (для загрузки на YouTube).

Текст — сценарий (как сказано в дубле 2), время — слова из voice/words_raw.json в
секундах шота: до точки вставки паузы t - T0, после — t - T0 + PAUSE (см. sound/mix.py).
"""
from pathlib import Path

HERE = Path(__file__).parent
T0, CUT, PAUSE = 24.35, 38.50, 1.4
LINES = [  # текст, начало и конец в секундах исходного дубля
    ("So, Perseus now owned the deadliest weapon in Greece:", 24.52, 28.82),
    ("a head that turned anyone who looked at it into stone.", 29.52, 33.52),
    ("The instructions were simple.", 34.94, 36.54),
    ("Don't look.", 37.28, 37.98),
    ("The guards... didn't read the instructions.", 39.08, 42.30),
]


def shot(t):
    return t - T0 + (PAUSE if t >= CUT else 0)


def ts(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


out = []
for i, (text, a, b) in enumerate(LINES, 1):
    out.append(f"{i}\n{ts(shot(a))} --> {ts(shot(b) + 0.3)}\n{text}\n")
(HERE / "out" / "dont_look.en.srt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
