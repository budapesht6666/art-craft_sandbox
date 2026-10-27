"""Баннер и логотип канала из сгенерированных картинок (out/) и шрифта (fonts/).

python compose.py  ->  out/banner.png (2560x1440), out/watermark.png (150x150),
                       local/banner_zones.png (что видно на телефоне / ПК / ТВ)
Нужен local/cut/barnaby_02.png: slice_sheet.py out/barnaby_model.png local/cut --grid 2x4 --prefix barnaby
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
OUT, LOCAL = HERE / "out", HERE / "local"
FONT = HERE / "fonts" / "LuckiestGuy-Regular.ttf"
W, H = 2560, 1440
SAFE = (507, 508, 2053, 931)          # видно везде (телефон); ПК — вся ширина, та же высота
INK = (43, 30, 22)                    # тёмно-коричневый контур, как линия в рисунках


def text(img, xy, s, size, fill, stroke, anchor="lm"):
    f = ImageFont.truetype(str(FONT), size)
    d = ImageDraw.Draw(img)
    sh = Image.new("RGBA", img.size, 0)   # мягкая тень под надписью
    ImageDraw.Draw(sh).text((xy[0] + size // 18, xy[1] + size // 14), s, font=f, fill=(0, 0, 0, 120),
                            anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(size // 25)))
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=INK)


def fit(s, width, stroke):
    """Самый крупный кегль, при котором строка с обводкой влезает в width."""
    size = 200
    while ImageFont.truetype(str(FONT), size).getlength(s) + 2 * stroke > width:
        size -= 2
    return size


def banner():
    img = Image.open(OUT / "banner_bg.png").convert("RGBA").resize((W, H), Image.LANCZOS)
    bard = Image.open(LOCAL / "cut" / "barnaby_02.png").convert("RGBA")
    k = 560 / bard.height
    bard = bard.resize((round(bard.width * k), 560), Image.LANCZOS)
    img.alpha_composite(bard, (540, 535))
    x0, x1 = 980, SAFE[2] - 25                      # надписи целиком внутри зоны телефона
    title = fit("PRETTY MUCH HISTORY", x1 - x0, 10)
    tag = fit("The whole story. Pretty much.", (x1 - x0) * 0.8, 7)
    text(img, ((x0 + x1) // 2, 655), "PRETTY MUCH HISTORY", title, (255, 255, 255), 10, "mm")
    text(img, ((x0 + x1) // 2, 790), "The whole story. Pretty much.", tag, (242, 182, 50), 7, "mm")
    img.convert("RGB").save(OUT / "banner.png", optimize=True)
    img.convert("RGB").save(OUT / "banner.jpg", quality=92)      # PNG ~5,7 МБ при лимите 6 МБ
    return img


def zones(img):
    z = img.convert("RGB").copy()
    d = ImageDraw.Draw(z)
    d.rectangle((0, SAFE[1], W - 1, SAFE[3]), outline=(0, 200, 255), width=6)        # ПК
    d.rectangle(SAFE, outline=(255, 40, 40), width=8)                                  # телефон
    z.resize((1280, 720), Image.LANCZOS).save(LOCAL / "banner_zones.png")
    z.crop((0, SAFE[1], W, SAFE[3])).resize((1280, 212), Image.LANCZOS).save(LOCAL / "banner_desktop.png")


def watermark():
    av = Image.open(OUT / "avatar_c.png").convert("RGBA").resize((600, 600), Image.LANCZOS)
    m = Image.new("L", (600, 600), 0)
    ImageDraw.Draw(m).ellipse((6, 6, 594, 594), fill=255)
    av.putalpha(m)
    av.resize((150, 150), Image.LANCZOS).save(OUT / "watermark.png", optimize=True)


if __name__ == "__main__":
    zones(banner())
    watermark()
