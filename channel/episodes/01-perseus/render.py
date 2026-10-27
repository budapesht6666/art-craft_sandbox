"""Рендер серии: каждая склейка — свой mp4 (EffectCraft CLI), потом склейка ffmpeg и звук.

python render.py sheet          — лист проверки: по кадру из середины каждой склейки -> local/check_sheet.jpg
python render.py shots [S12..]  — рендер склеек в local/shots/ (все или по префиксу)
python render.py join           — local/shots/*.mp4 + sound/mix.wav -> out/video/perseus.mp4 (+ local/perseus_preview.mp4, 720p)

Проект local/ec/episode.ecproj собирает build_episode.js (MCP run_script), его нужно сохранить до рендера.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).parent
CLI = r"C:\Program Files\EffectCraft\effectcraft-cli.exe"
LOCAL = HERE / "local"                 # рабочие файлы, в git не идут
PROJ = LOCAL / "ec" / "episode.ecproj"
EP = json.loads((LOCAL / "ec" / "episode.json").read_text(encoding="utf-8"))
OUT = HERE / "out"
SHOTS = LOCAL / "shots"


def sheet(names):
    tmp = LOCAL / "frames"
    tmp.mkdir(parents=True, exist_ok=True)
    comps = [c for c in EP["comps"] if not names or any(c["name"].startswith(n) for n in names)]

    def one(c):
        p = tmp / f"{c['name']}.png"
        t = c.get("check", c["duration"] * 0.6)
        subprocess.run([CLI, "render-frame", "--project", str(PROJ), "--comp", c["name"], "--time", f"{t:.2f}",
                        "--max-side", "640", "--out", str(p)], check=True, capture_output=True)
        return c, p

    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, comps))
    cols = 5
    w, h = 640, 360
    rows = (len(res) + cols - 1) // cols
    S = Image.new("RGB", (cols * w, rows * h), "black")
    d = ImageDraw.Draw(S)
    for i, (c, p) in enumerate(res):
        x, y = (i % cols) * w, (i // cols) * h
        S.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y))
        d.rectangle((x, y, x + 120, y + 30), fill="black")
        d.text((x + 6, y + 6), c["name"], fill="yellow")
    S.save(LOCAL / "check_sheet.jpg", quality=82)
    print("local/check_sheet.jpg", len(res))


def shots(names):
    SHOTS.mkdir(parents=True, exist_ok=True)
    comps = [c for c in EP["comps"] if not names or any(c["name"].startswith(n) for n in names)]

    def one(c):
        p = SHOTS / f"{c['name']}.mp4"
        r = subprocess.run([CLI, "render", "--project", str(PROJ), "--comp", c["name"], "--out", str(p),
                            "--format", "h264"], capture_output=True, text=True)
        return c["name"], r.returncode, r.stderr[-300:]

    with ThreadPoolExecutor(3) as ex:
        for name, code, err in ex.map(one, comps):
            print(name, "ok" if code == 0 else f"ОШИБКА {err}")


def join():
    lst = SHOTS / "list.txt"
    lst.write_text("".join(f"file '{c['name']}.mp4'\n" for c in EP["comps"]), encoding="utf-8")
    video = LOCAL / "_video.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(video)], check=True)
    mix = HERE / "sound" / "mix.wav"
    (OUT / "video").mkdir(parents=True, exist_ok=True)
    final = OUT / "video" / "perseus.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(video), "-i", str(mix), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)], check=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(final), "-vf", "scale=1280:720", "-c:v", "libx264",
                    "-crf", "25", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", str(LOCAL / "perseus_preview.mp4")], check=True)
    print(final)


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    {"sheet": sheet, "shots": shots, "join": lambda r: join()}[cmd](rest)
