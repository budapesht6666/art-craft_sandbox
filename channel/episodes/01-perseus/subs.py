"""Субтитры серии на всех языках: текст сегментов + время voice/edl.json -> out/subs/perseus.<язык>.srt.

python subs.py

Английский — из script.md, остальные — subs/<язык>.json ({"реплика.сегмент": текст}). Перевод хранится по
сегментам голоса, поэтому после новой записи время пересчитывается само. Сегмент режется на титры не
длиннее MAX знаков по знакам препинания, время делится пропорционально длине текста.
Загрузка: YouTube Studio → Субтитры → Добавить язык → Загрузить файл → «С временными кодами».
"""
import json
import re
from pathlib import Path

from voice import script_lines

HERE = Path(__file__).parent
EDL = json.loads((HERE / "voice" / "edl.json").read_text(encoding="utf-8"))
OUT = HERE / "out" / "subs"
NAME = "perseus"
MAX = 42


def chunks(text):
    parts = re.split(r"(?<=[.!?:,;…।»“\"])\s+", text)
    out, cur = [], ""
    for p in [p for p in parts if p]:
        if cur and len(cur) + 1 + len(p) > MAX:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur:
        out.append(cur)
    res = []                              # слишком длинные куски — пополам по словам
    for c in out:
        while len(c) > MAX + 12:
            ws = c.split()
            half = len(ws) // 2
            res.append(" ".join(ws[:half]))
            c = " ".join(ws[half:])
        res.append(c)
    return res


def ts(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write(lang, text_of):
    cues = []
    for s in EDL["segments"]:
        text = text_of(s["line"], s["seg"])
        a, b = s["t"], s["t"] + s["b"] - s["a"]
        parts = chunks(text)
        total = sum(len(p) for p in parts)
        t = a
        for p in parts:
            d = (b - a) * len(p) / total
            cues.append((t, t + d, p))
            t += d
    srt = [f"{i}\n{ts(a)} --> {ts(b + 0.25 if i == len(cues) or cues[i][0] > b + 0.3 else b)}\n{p}\n"
           for i, (a, b, p) in enumerate(cues, 1)]
    (OUT / f"{NAME}.{lang}.srt").write_text("\n".join(srt), encoding="utf-8")
    return len(cues)


OUT.mkdir(parents=True, exist_ok=True)
lines = script_lines()
print("en", write("en", lambda n, k: lines[n][k]))
for f in sorted((HERE / "subs").glob("*.json")):
    tr = json.loads(f.read_text(encoding="utf-8"))
    missing = [f"{n}.{k}" for n, segs in lines.items() for k in range(len(segs)) if f"{n}.{k}" not in tr]
    if missing:
        raise SystemExit(f"{f.name}: нет перевода сегментов {missing}")
    print(f.stem, write(f.stem, lambda n, k: tr[f"{n}.{k}"]))
