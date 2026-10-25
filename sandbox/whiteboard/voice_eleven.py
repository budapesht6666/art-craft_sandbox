"""Та же озвучка, что в voice.py, но голосом ElevenLabs.

Запуск: python sandbox/whiteboard/voice_eleven.py [путь к .env с ELEVENLABS_API_KEY]
Результат: voice_eleven.mp3 и timing_eleven.json рядом со скриптом.
Текст и метки берутся из voice.py. Время метки — начало первой буквы следующего слова
по посимвольным таймингам `/with-timestamps`.
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from voice import LEAD, SCRIPT

HERE = Path(__file__).parent
ENV = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\projects\claude\remotion-skill\.env")
# Голос и настройки как у композиции Whiteboard в remotion-skill.
VOICE_ID = "onwK4e9ZLuTAKqWW03F9"  # Daniel — Authoritative, Calm
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.6, "similarity_boost": 0.75, "style": 0.3, "use_speaker_boost": True}


def api_key():
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(f"ELEVENLABS_API_KEY не найден в {ENV}")


def main():
    cues, text = [], ""
    for part in re.split(r"(\{\w+\})", SCRIPT):
        m = re.fullmatch(r"\{(\w+)\}", part)
        if m:
            cues.append((m.group(1), len(text)))
        else:
            text += part

    body = json.dumps({"text": text, "model_id": MODEL, "voice_settings": SETTINGS}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps",
        data=body,
        headers={"xi-api-key": api_key(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs {e.code}: {e.read().decode(errors='replace')[:400]}")

    (HERE / "voice_eleven.mp3").write_bytes(base64.b64decode(data["audio_base64"]))
    al = data["alignment"]
    chars, starts = al["characters"], al["character_start_times_seconds"]
    if "".join(chars) != text:
        print("текст в ответе отличается от отправленного — тайминг может съехать")

    def time_at(i):
        # первая непробельная буква начиная с позиции метки
        while i < len(chars) - 1 and not chars[i].strip():
            i += 1
        return starts[min(i, len(starts) - 1)]

    timing = {name: round(LEAD + time_at(i), 2) for name, i in cues}
    timing["_end"] = round(LEAD + al["character_end_times_seconds"][-1] + 1.0, 2)
    timing["_lead"] = LEAD
    (HERE / "timing_eleven.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"символов: {len(text)}")
    print(json.dumps(timing, ensure_ascii=False))


if __name__ == "__main__":
    main()
