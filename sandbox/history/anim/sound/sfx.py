"""Звуки шота через ElevenLabs Sound Effects: python sfx.py [имя] -> sound/<имя>.mp3.

Ключ ELEVENLABS_API_KEY из remotion-skill/.env, не печатается. Уже готовые файлы не трогает.
Бесплатный тариф ElevenLabs — без коммерческой лицензии: для демо, не для монетизации.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ENV = Path(r"C:\projects\claude\remotion-skill\.env")
SFX = {
    "scream": ("short comedic cartoon man scream of terror, high pitched, panicked, no music", 1.4),
    "stone": ("magical petrification: stone cracking and grinding upward, crackling rock, deep rumble", 1.6),
    "flash": ("magical whoosh flash, eerie shimmering zap of a curse, short", 0.8),
    "title": ("deep cinematic impact thud with short reverb tail, single hit", 0.7),
    "hiss": ("many snakes hissing angrily at once, close and menacing, no music", 3),
    "wind": ("gentle evening wind on a barren rocky island near the sea, distant waves, calm ambience, no music", 10),
}


def key():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("нет ELEVENLABS_API_KEY")


def main():
    k = key()
    names = sys.argv[1:] or list(SFX)
    for n in names:
        out = HERE / f"{n}.mp3"
        if out.exists() and not sys.argv[1:]:
            continue
        text, dur = SFX[n]
        body = {"text": text, "duration_seconds": dur, "prompt_influence": 0.5}
        req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation", data=json.dumps(body).encode(),
                                     headers={"xi-api-key": k, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out.write_bytes(r.read())
            print(n, "ok", out.stat().st_size // 1024, "КБ")
        except urllib.error.HTTPError as e:
            print(n, e.code, e.read().decode().replace(k, "<KEY>")[:300])


if __name__ == "__main__":
    main()
