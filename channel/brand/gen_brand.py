"""Оформление канала Pretty Much History: ведущий Barnaby the Bard и аватары.

Генерация через Gemini API тем же стилем, что серии (библия и call() — из эпизода 01-perseus).

python gen_brand.py              — все задания, у которых ещё нет out/<name>.png
python gen_brand.py avatar_a     — одно задание (старое уходит в local/_old/)
python gen_brand.py --dry        — только показать промпты
"""
import base64
import json
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
EP = HERE.parent / "episodes" / "01-perseus" / "art"
sys.path.insert(0, str(EP))
import gen as ep                                     # noqa: E402  key(), BIBLE, MODELS, API

OUT = HERE / "out"
STYLE_REF = EP / "sheets" / "10_cast_model_v2.png"
MODEL_SHEET = OUT / "barnaby_model.png"

BARNABY = ("BARNABY THE BARD, the narrator and host of the channel: a middle-aged wandering storyteller. "
           "Same white egg-shaped head as the cast, two small solid black oval dot eyes, very thick expressive "
           "dark-brown eyebrows, a short scruffy dark-brown beard and moustache drawn as simple flat shapes, "
           "a slightly crooked green laurel wreath on his bald head. Mustard-yellow knee-length tunic with a "
           "brown belt and a small leather satchel, a dark teal travelling cloak pinned at the shoulder, "
           "brown sandals. Always carries a small wooden lyre. Personality: a cheeky, slightly tired know-it-all "
           "who has seen every myth go wrong and finds it all hilarious.")

AVATAR = ("Square 1:1 image. YouTube channel profile picture (it will be cropped to a circle and shown very "
          "small, so it must read at 48 pixels). Head-and-shoulders close-up of Barnaby the Bard, the same "
          "character as in the attached model sheet: keep identical head shape, eyes, eyebrows, beard, laurel "
          "wreath, colors and line style. His head is large and centered, filling about 60% of the image height, "
          "everything important stays inside the central circle; nothing touches the edges. "
          "Bold thick black outlines, flat colors, very light cross-hatching only, high contrast, no gradients, "
          "no text, no letters, no logo, no watermark, no frame, no border.")

JOBS = [
    {"name": "barnaby_model", "aspect": "16:9", "refs": [STYLE_REF],
     "prompt": "\n".join([
         "Wide 16:9 landscape image. Character model sheet for a hand-drawn 2D animated YouTube video about "
         "history and mythology.",
         "The attached image shows other characters of this channel, for style only: draw the new character in "
         "exactly the same drawing style (line weight, egg-shaped white heads, dot eyes, flat colors). Do not "
         "draw the characters from that image.",
         ep.BIBLE["cast_style"], BARNABY, ep.BIBLE["eyes_rule"], ep.BIBLE["sheet_style"],
         ep.layout(4, 4, 1),
         "Row 1: (1) Barnaby standing facing the viewer, neutral, lyre in one hand; (2) Barnaby smirking with "
         "one eyebrow raised, pointing one finger up as if saying 'well, technically'; (3) Barnaby shrugging "
         "with both palms up, 'eh, pretty much'; (4) Barnaby strumming the lyre, eyes half closed, singing."])},
    {"name": "avatar_a", "aspect": "1:1", "refs": [MODEL_SHEET],
     "prompt": AVATAR + " Expression: knowing smirk, one eyebrow raised high. The lyre peeks in at the bottom "
                        "corner. Background: one flat warm mustard-yellow color (#F2B632)."},
    {"name": "avatar_b", "aspect": "1:1", "refs": [MODEL_SHEET],
     "prompt": AVATAR + " Expression: cheeky grin, raising one finger next to his face as if about to tell a "
                        "juicy secret. Background: one flat terracotta red-orange color (#D9572B)."},
    {"name": "avatar_c", "aspect": "1:1", "refs": [MODEL_SHEET],
     "prompt": AVATAR + " Expression: amused, eyebrows raised, a small shrug, the laurel wreath slipping to one "
                        "side. Background: one flat deep teal color (#1F7A7A)."},
    {"name": "banner_bg", "aspect": "16:9", "refs": [EP / "sheets" / "bg_hills.png"],
     "prompt": "\n".join([
         "Wide 16:9 landscape image. Banner background painting for a hand-drawn 2D animated YouTube history "
         "channel, in the same painting style as the attached image.",
         "Scene: one continuous sunny panoramic landscape that blends famous places of world history from left "
         "to right along a single horizon: Egyptian pyramids in the desert, a Greek temple on a hill by the sea "
         "with a trireme, the Roman Colosseum, a Viking longship in a fjord, a piece of the Great Wall of China "
         "on green hills, a medieval castle. All landmarks are small and sit on a low horizon in the middle "
         "third of the image height; the top 40% is a calm, simple light-blue sky with a few soft clouds; the "
         "bottom is plain grass and sand. The middle of the image between 35% and 75% of the width has an "
         "open, quiet sky area above the horizon, free of objects, for a title.",
         ep.BIBLE["bg_style"]])},
]


def call(model, prompt, images, aspect, k):
    parts = [{"text": prompt}]
    for p in images:
        parts.append({"inline_data": {"mime_type": "image/png",
                                      "data": base64.b64encode(Path(p).read_bytes()).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                 "imageConfig": {"aspectRatio": aspect, "imageSize": "2K"}}}
    req = urllib.request.Request(ep.API.format(model), data=json.dumps(body).encode(),
                                 headers={"x-goog-api-key": k, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def run(job, k):
    out = OUT / f"{job['name']}.png"
    for model in ep.MODELS:
        t0 = time.time()
        try:
            res = call(model, job["prompt"], job["refs"], job["aspect"], k)
        except urllib.error.HTTPError as e:
            print(f"  {model}: HTTP {e.code} {e.read().decode().replace(k, '<KEY>')[:300]}")
            if e.code in (400, 404):
                continue
            raise SystemExit(1)
        img = [p for p in res["candidates"][0]["content"]["parts"] if "inlineData" in p]
        if not img:
            print(f"  {model}: картинки нет, ответ: {json.dumps(res)[:300]}")
            continue
        if out.exists():
            (HERE / "local" / "_old").mkdir(parents=True, exist_ok=True)
            shutil.move(out, HERE / "local" / "_old" / f"{job['name']}_{int(out.stat().st_mtime)}.png")
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
        [j for j in JOBS if not (OUT / f"{j['name']}.png").exists()]
    if "--dry" in sys.argv:
        for j in jobs:
            print(f"=== {j['name']}  refs={[Path(p).name for p in j['refs']]}\n{j['prompt']}\n")
        return
    OUT.mkdir(exist_ok=True)
    k = ep.key()
    for j in jobs:
        print(j["name"])
        run(j, k)


if __name__ == "__main__":
    main()
