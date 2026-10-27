"""Клон голоса пользователя в ElevenLabs: подготовка образца, создание клона, пробная озвучка.

python clone.py prepare <запись>   — чистка образца -> channel/local/voice/sample_clean.mp3 (только локально)
python clone.py create             — создать Instant Voice Clone «Pretty Much History narrator» (нужен Starter+)
python clone.py test               — глава 1 серии 1 клоном на нескольких моделях -> channel/local/voice/test_<модель>.mp3

Ключ — ELEVENLABS_API_KEY из remotion-skill/.env, не печатается. Сменить тариф через API нельзя:
это оплата на elevenlabs.io (Upgrade -> Starter). Подробности и памятка по записи — README.md рядом.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).parent
LOCAL = HERE.parent / "local" / "voice"            # голос пользователя — только локально
ENV = Path(r"C:\projects\claude\remotion-skill\.env")
NAME = "Pretty Much History narrator"
API = "https://api.elevenlabs.io"
EPISODE = HERE.parent / "episodes" / "01-perseus"
MODELS = ["eleven_multilingual_v2", "eleven_v3", "eleven_v4"]


def key():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("нет ELEVENLABS_API_KEY")


def call(path, data=None, headers=None, raw=False):
    k = key()
    req = urllib.request.Request(API + path, data=data, headers={"xi-api-key": k, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = r.read()
            return body if raw else json.loads(body)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:400].replace(k, '<KEY>')}")


def prepare(src):
    """Срез низа, мягкое шумоподавление, паузы длиннее 0,7 с -> 0,4 с, громкость −20 LUFS, пик −3 dBTP
    (ElevenLabs советует RMS −23…−18 dB и пик ниже −3 dB)."""
    LOCAL.mkdir(parents=True, exist_ok=True)
    out = LOCAL / "sample_clean.mp3"
    af = ("highpass=f=80,afftdn=nr=10:nf=-40,"
          "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.7:stop_threshold=-45dB:stop_silence=0.4,"
          "loudnorm=I=-20:TP=-3:LRA=7")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(src), "-af", af, "-ac", "1", "-ar", "44100",
                    "-b:a", "192k", str(out)], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                             capture_output=True, text=True).stdout)
    print(f"{out}  {d:.0f} с" + ("  (меньше минуты: клон будет слабее, лучше 1–2 мин)" if d < 60 else ""))


def create():
    sub = call("/v1/user/subscription")
    if not sub.get("can_use_instant_voice_cloning"):
        sys.exit(f"тариф {sub.get('tier')}: клонирование недоступно — нужен Starter (elevenlabs.io → Upgrade)")
    voices = call("/v1/voices")["voices"]
    old = [v["voice_id"] for v in voices if v["name"] == NAME]
    if old:
        sys.exit(f"голос «{NAME}» уже есть: {old[0]}")
    sample = LOCAL / "sample_clean.mp3"
    b = uuid.uuid4().hex
    parts = []
    for k, v in {"name": NAME, "description": "Channel narrator, cloned from the owner's own voice (consent: owner).",
                 "remove_background_noise": "false"}.items():
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="files"; filename="{sample.name}"\r\n'
                 f"Content-Type: audio/mpeg\r\n\r\n".encode() + sample.read_bytes() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    r = call("/v1/voices/add", data=b"".join(parts), headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    print("клон создан:", r.get("voice_id"))


def test():
    voices = call("/v1/voices")["voices"]
    vid = next((v["voice_id"] for v in voices if v["name"] == NAME), None)
    if not vid:
        sys.exit(f"нет голоса «{NAME}» — сначала create")
    sys.path.insert(0, str(EPISODE))
    from voice import script_lines        # noqa: E402
    L = script_lines()
    text = " ".join(" ".join(L[n]) for n in range(4, 11))      # глава 1
    LOCAL.mkdir(parents=True, exist_ok=True)
    for m in MODELS:
        audio = call(f"/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                     data=json.dumps({"text": text, "model_id": m}).encode(),
                     headers={"Content-Type": "application/json"}, raw=True)
        (LOCAL / f"test_{m}.mp3").write_bytes(audio)
        print("готово:", LOCAL / f"test_{m}.mp3")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"prepare": lambda: prepare(Path(sys.argv[2])), "create": create, "test": test}.get(cmd, lambda: print(__doc__))()
