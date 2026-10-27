"""Голос -> время каждого слова: python transcribe.py voice.m4a [out.json] [--model small.en] [--prompt "..."]

faster-whisper (pip install faster-whisper), работает локально, звук никуда не уходит.
Ловушка faster-whisper 1.2.1: не открывает файлы сам (av.open() ... metadata_errors),
поэтому звук декодирует ffmpeg в 16 кГц моно и передаёт numpy-массив.

Два прогона полезны оба:
  без --prompt — так слышит зритель без контекста (проверка акцента: «head» -> «hat»);
  с --prompt "Greek mythology. Perseus, Medusa..." — точный текст и время для монтажа.
Пишет [{start, end, text, words: [{w, s, e, p}]}], печатает сегменты и паузы > 0,25 с.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def opt(name, default):
    if name in sys.argv:
        i = sys.argv.index(name)
        val = sys.argv[i + 1]
        del sys.argv[i:i + 2]
        return val
    return default


def main():
    model = opt("--model", "small.en")
    prompt = opt("--prompt", None)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name("words.json")
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(src), "-ar", "16000", "-ac", "1",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio, word_timestamps=True, language="en", initial_prompt=prompt)
    data, prev = [], None
    for s in segs:
        words = [{"w": x.word.strip(), "s": round(x.start, 2), "e": round(x.end, 2), "p": round(x.probability, 2)}
                 for x in s.words]
        print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}")
        for w in words:
            if prev is not None and w["s"] - prev > 0.25:
                print(f"          пауза {w['s'] - prev:.2f} с перед «{w['w']}» ({w['s']:.2f})")
            prev = w["e"]
        data.append({"start": s.start, "end": s.end, "text": s.text.strip(), "words": words})
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("->", out)


if __name__ == "__main__":
    main()
