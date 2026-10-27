"""Серия «Персей»: копия sandbox/history/gemini/gen.py, плюс подписанные эталоны и style_refs (образец только стиля).

Генерация листов через Gemini API: промпты собираются из prompts/bible.json и prompts/jobs.json.

python gen.py                 — все задания, у которых ещё нет sheets/<name>.png
python gen.py 03_cast_test    — одно задание (перезапишет, старое уходит в sheets/_old/)
python gen.py --dry           — только показать собранные промпты

Виды заданий:
  sheet — лист поз на белом: chars (ключи библии), grid [столбцы, строки], rows (текст ячеек
          по строкам). Эталоны персонажей прикладываются сами (bible.refs).
  bg    — фон 16:9: scene (описание места), стиль фона из библии.
  edit  — правка готовой картинки: src + prompt (+ refs — приложить образцы).
Ключ: переменная GEMINI_API_KEY, иначе remotion-skill/.env. Ключ нигде не печатается.
Каждый вызов пишется в gen_log.jsonl (модель, токены, время).
"""
import base64
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
SHEETS = HERE / "sheets"
BIBLE = json.loads((HERE / "prompts" / "bible.json").read_text(encoding="utf-8"))
JOBS = json.loads((HERE / "prompts" / "jobs.json").read_text(encoding="utf-8"))
ENV = Path(r"C:\projects\claude\remotion-skill\.env")
MODELS = ["gemini-nano-banana-2.1", "gemini-3.1-flash-image"]   # первая доступная
API = "https://generativelanguage.googleapis.com/v1/models/{}:generateContent"


def key():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if k:
        return k
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("нет GEMINI_API_KEY")


def layout(n, c, r):
    return (f"Layout: exactly {n} separate full-body drawings arranged in an invisible grid of {c} columns "
            f"and {r} rows. Each drawing sits fully inside its own cell, centered, with wide empty white "
            "gutters between cells. Nothing overlaps, touches or crosses into another cell. All figures at the "
            "same scale; figures in one row share the same baseline. No text, no numbers, no labels, no "
            "captions, no grid lines, no frames, no borders, no ground lines, no watermark.")


def build(job):
    """-> (текст промпта, [пути картинок])"""
    if job["kind"] == "edit":                 # refs — образцы после правимой картинки (например, стиль лиц)
        return job["prompt"], [job["src"]] + job.get("refs", [])
    if job["kind"] == "bg":
        return ("Wide 16:9 landscape image. Background painting for a hand-drawn 2D animated YouTube video "
                "about Greek mythology, in the style of a modern adult cartoon history channel.\n"
                f"Scene: {job['scene']}\n{BIBLE['bg_style']}"), job.get("refs", []) + job.get("style_refs", [])
    chars = job["chars"]
    refs, labels = [], []                     # эталоны по порядку, у каждого подпись в промпте
    for c in chars:
        p = BIBLE["refs"].get(c)
        if not p:
            continue
        if p in refs:
            labels[refs.index(p)] += " and " + c.replace("_", " ").title()
        else:
            refs.append(p)
            labels.append(c.replace("_", " ").title())
    lines = ["Wide 16:9 landscape image. Character pose sheet for a hand-drawn 2D animated YouTube video "
             "about Greek mythology."]
    if refs:
        order = "; ".join(f"image {i + 1}: {l}" for i, l in enumerate(labels))
        lines.append(f"Attached reference images ({order}). These are the same characters: keep identical "
                     "proportions, head shape, eye design, colors, clothing, helmets and line style.")
    if job.get("style_refs"):
        refs += job["style_refs"]
        lines.append("The last attached image shows other characters of this channel, for style only: draw "
                     "the new characters in exactly the same drawing style (line weight, egg-shaped white heads, "
                     "dot eyes, flat colors). Do not draw the characters from that image.")
    lines += [BIBLE["cast_style"]] + [BIBLE["characters"][c] for c in chars]
    lines += [BIBLE["eyes_rule"], BIBLE["sheet_style"]]
    c, r = job["grid"]
    lines.append(layout(c * r, c, r))
    lines += [f"Row {i + 1}: {row}" for i, row in enumerate(job["rows"])]
    return "\n".join(lines), refs


def call(model, prompt, images, k):
    parts = [{"text": prompt}]
    for p in images:
        data = (HERE / p).read_bytes()
        parts.append({"inline_data": {"mime_type": "image/png", "data": base64.b64encode(data).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                 "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}}}
    req = urllib.request.Request(API.format(model), data=json.dumps(body).encode(),
                                 headers={"x-goog-api-key": k, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def run(job, k):
    prompt, images = build(job)
    out = SHEETS / f"{job['name']}.png"
    for model in [job.get("model")] if job.get("model") else MODELS:
        t0 = time.time()
        try:
            res = call(model, prompt, images, k)
        except urllib.error.HTTPError as e:
            msg = e.read().decode().replace(k, "<KEY>")[:300]
            print(f"  {model}: HTTP {e.code} {msg}")
            if e.code in (400, 404):
                continue                      # модели нет на этом ключе — следующая
            raise SystemExit(1)
        img = [p for p in res["candidates"][0]["content"]["parts"] if "inlineData" in p]
        if not img:
            print(f"  {model}: картинки нет, ответ: {json.dumps(res)[:300]}")
            continue
        if out.exists():
            (SHEETS / "_old").mkdir(exist_ok=True)
            shutil.move(out, SHEETS / "_old" / f"{job['name']}_{int(out.stat().st_mtime)}.png")
        out.write_bytes(base64.b64decode(img[0]["inlineData"]["data"]))
        log = {"name": job["name"], "model": model, "sec": round(time.time() - t0, 1),
               "usage": res.get("usageMetadata"), "at": time.strftime("%Y-%m-%d %H:%M")}
        with open(HERE / "gen_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log) + "\n")
        print(f"  {model}: {out.name} за {log['sec']} с")
        return
    raise SystemExit("ни одна модель не ответила картинкой")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    jobs = [j for j in JOBS if j["name"] in args] if args else \
        [j for j in JOBS if not (SHEETS / f"{j['name']}.png").exists()]
    if "--dry" in sys.argv:
        for j in jobs:
            p, imgs = build(j)
            print(f"=== {j['name']}  refs={imgs}\n{p}\n")
        return
    k = key()
    for j in jobs:
        print(j["name"])
        run(j, k)


if __name__ == "__main__":
    main()
