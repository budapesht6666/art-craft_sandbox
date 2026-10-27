"""Фигуры из нарезки Gemini -> ассеты шота: тон заката, тень под ногами, точка опоры у ног.

python make_assets.py -> ec/assets/*.png и ec/assets/anchors.json
"""
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).parent
CUT = HERE.parent / "gemini" / "cut"
OUT = HERE / "ec" / "assets"
TINT = (228, 200, 182)    # тёплый сумеречный свет, снят с земли фона
PAD = 60                  # запас снизу и по бокам под тень

FIGURES = {
    "perseus_sneak": CUT / "cast" / "cast_02.png",
    "perseus_hold": CUT / "cast" / "cast_01.png",
    "perseus_win": CUT / "cast" / "cast_03.png",
    "soldier_idle": CUT / "model" / "model_04.png",
    "soldier_scream": CUT / "cast" / "cast_04.png",
    "soldier_stone": CUT / "cast" / "cast_06.png",
    "medusa_cu": CUT / "closeup" / "cu_01.png",
}


def feet(a):
    """Середина ступней: столбцы с альфой в нижних 6 % рисунка."""
    w, h = a.size
    band = a.crop((0, int(h * 0.94), w, h)).point(lambda v: 255 if v > 128 else 0)
    cols = [x for x in range(w) if band.crop((x, 0, x + 1, band.height)).getbbox()]
    return (cols[0] + cols[-1]) / 2, cols[0], cols[-1]


NO_SHADOW = {"medusa_cu"}     # крупный план: голова в воздухе, тени нет
anchors = {}
for name, src in FIGURES.items():
    im = Image.open(src).convert("RGBA")
    a = im.getchannel("A")
    rgb = ImageChops.multiply(im.convert("RGB"), Image.new("RGB", im.size, TINT))
    fig = rgb.convert("RGBA")
    fig.putalpha(a)
    fx, x0, x1 = feet(a)
    w, h = im.size
    canvas = Image.new("RGBA", (w + 2 * PAD, h + PAD), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    half = max((x1 - x0) * 0.62, w * 0.18)
    cx, cy = fx + PAD, h - 4
    ImageDraw.Draw(sh).ellipse((cx - half, cy - 22, cx + half, cy + 20), fill=(20, 10, 10, 120))
    if name not in NO_SHADOW:
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    canvas.alpha_composite(fig, (PAD, 0))
    canvas.save(OUT / f"{name}.png")
    anchors[name] = {"size": [w + 2 * PAD, h + PAD], "feet": [cx, h], "height": h}
    print(name, canvas.size, "feet", (round(cx), h))

(OUT / "anchors.json").write_text(json.dumps(anchors, indent=1), encoding="utf-8")
