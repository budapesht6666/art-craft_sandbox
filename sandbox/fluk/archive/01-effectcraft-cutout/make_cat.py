"""Кот пилота: SVG по частям и лист эмоций.

python make_cat.py  ->  parts/cat.svg (поза по умолчанию, части по группам)
                        parts/sheet.svg (лист: четыре эмоции и наклон головы)

Веко, зрачок и рот задаются параметрами, поэтому одни и те же части годятся и для
листа, и для перекладки в EffectCraft.
"""
import math
from pathlib import Path

INK = "#1d1d1f"
FUR = "#ffffff"
EYE = "#f3f4ee"
IRIS = "#9db29a"
PINK = "#f2a1ab"
EAR_PINK = "#f6c9cf"
BG = "#e9e6df"

EYES = {"l": (430, 350), "r": (572, 350)}
RX, RY = 44, 32


def tail():
    return (f'<g id="tail" fill="{FUR}" stroke="{INK}" stroke-width="8" stroke-linejoin="round">'
            '<path d="M 700 860 C 800 875 875 815 850 725 C 840 690 800 688 806 722 '
            'C 822 790 785 822 705 815 Z"/></g>')


def body():
    return (f'<g id="body" fill="{FUR}" stroke="{INK}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round">'
            '<path d="M 365 470 C 290 560 250 700 268 830 C 280 902 362 915 500 915 '
            'C 638 915 720 902 732 830 C 750 700 710 560 635 470 Z"/>'
            # пушистая грудь
            '<path d="M 456 506 q 10 16 22 4 q 11 17 23 2 q 11 17 23 -2 q 9 13 20 0" '
            'fill="none" stroke-width="5"/>'
            '</g>')


def paws():
    return (f'<g id="paws" fill="{FUR}" stroke="{INK}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round">'
            '<path d="M 388 905 C 388 880 412 868 440 868 C 470 868 492 882 492 905 C 492 925 388 925 388 905 Z"/>'
            '<path d="M 512 905 C 512 880 534 868 562 868 C 592 868 616 882 616 905 C 616 925 512 925 512 905 Z"/>'
            '<path d="M 428 895 L 428 912 M 452 895 L 452 912 M 550 895 L 550 912 M 574 895 L 574 912" '
            'fill="none" stroke-width="5"/></g>')


def ears():
    return (f'<g id="ear_l" stroke="{INK}" stroke-width="8" stroke-linejoin="round">'
            f'<path d="M 352 285 C 340 230 338 180 348 150 C 385 165 420 190 445 218 Z" fill="{FUR}"/>'
            f'<path d="M 368 250 C 362 220 362 198 366 182 C 386 194 402 208 414 222 Z" fill="{EAR_PINK}" stroke="none"/></g>'
            f'<g id="ear_r" stroke="{INK}" stroke-width="8" stroke-linejoin="round">'
            f'<path d="M 648 285 C 662 230 664 180 654 150 C 615 165 580 190 555 218 Z" fill="{FUR}"/>'
            f'<path d="M 632 250 C 640 220 640 198 636 182 C 616 194 600 208 588 222 Z" fill="{EAR_PINK}" stroke="none"/></g>')


def head():
    return (f'<g id="head" fill="{FUR}" stroke="{INK}" stroke-width="8" stroke-linejoin="round">'
            '<path d="M 322 372 C 312 262 400 205 500 205 C 600 205 688 262 678 372 C 692 392 690 412 676 424 '
            'C 690 440 674 466 650 474 C 600 506 400 506 350 474 C 326 466 310 440 324 424 '
            'C 310 412 308 392 322 372 Z"/>'
            '<path d="M 482 214 C 488 196 498 192 500 205 C 504 190 516 194 518 212" fill="none" '
            'stroke-width="6" stroke-linecap="round"/></g>')


def lid(cx, cy, opened, sag=8):
    """Верхнее веко: часть эллипса глаза над линией века. opened 1 — открыт, 0 — закрыт."""
    if opened >= 1:
        return ""
    y = cy - RY + (1 - opened) * 2 * RY
    t = max(-1.0, min(1.0, (y - cy) / RY))
    dx = RX * math.sqrt(max(0.0, 1 - t * t))
    if dx < 1:  # веко закрыто целиком
        return (f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" fill="{FUR}" stroke="{INK}" stroke-width="7"/>'
                f'<path d="M {cx - RX + 6} {cy + 2} Q {cx} {cy + 18} {cx + RX - 6} {cy + 2}" fill="none" '
                f'stroke="{INK}" stroke-width="7" stroke-linecap="round"/>')
    large = 1 if y > cy else 0
    return (f'<path d="M {cx - dx:.1f} {y:.1f} A {RX} {RY} 0 {large} 1 {cx + dx:.1f} {y:.1f} '
            f'Q {cx} {y + sag:.1f} {cx - dx:.1f} {y:.1f} Z" fill="{FUR}" stroke="{INK}" '
            f'stroke-width="7" stroke-linejoin="round"/>')


def eye(side, opened=0.5, look=(-16, 6), pupil=13):
    cx, cy = EYES[side]
    # Зрачок опускается вместе с веком, иначе при прищуре он прячется целиком
    px, py = cx + look[0], cy + look[1] + max(0.0, 0.5 - opened) * 30
    # Радужка обрезается по белку. В EffectCraft то же даст альфа-маска по слою белка
    out = [f'<g id="eye_{side}">',
           f'<clipPath id="clip_{side}"><ellipse cx="{cx}" cy="{cy}" rx="{RX - 3}" ry="{RY - 3}"/></clipPath>',
           f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" fill="{EYE}" stroke="{INK}" stroke-width="7"/>',
           f'<g id="pupil_{side}" clip-path="url(#clip_{side})"><circle cx="{px}" cy="{py}" r="20" fill="{IRIS}"/>'
           f'<circle cx="{px - 3}" cy="{py + 1}" r="{pupil}" fill="{INK}"/>'
           f'<circle cx="{px - 9}" cy="{py - 7}" r="4.5" fill="{FUR}"/></g>',
           f'<g id="lid_{side}">{lid(cx, cy, opened, sag=8 if opened >= 0.5 else 2)}</g>',
           '</g>']
    return "".join(out)


MOUTHS = {
    "smirk": "M 501 427 L 501 440 M 501 440 Q 486 452 470 444 M 501 440 Q 518 450 536 438",
    "o": "M 501 427 L 501 436 M 490 446 C 490 436 512 436 512 446 C 512 458 490 458 490 446 Z",
    "w": "M 501 427 L 501 438 M 501 438 Q 488 452 474 440 M 501 438 Q 514 452 528 440",
    "flat": "M 501 427 L 501 438 M 478 444 L 524 444",
}


def face(mouth="smirk"):
    return (f'<g id="nose" fill="{PINK}" stroke="{INK}" stroke-width="6" stroke-linejoin="round">'
            '<path d="M 482 404 Q 501 396 520 404 Q 512 424 501 427 Q 490 424 482 404 Z"/></g>'
            f'<g id="mouth" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{MOUTHS[mouth]}"/></g>'
            f'<g id="whiskers" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linecap="round">'
            '<path d="M 440 422 Q 380 410 318 418 M 440 432 Q 382 432 322 446 M 444 442 Q 392 452 340 474"/>'
            '<path d="M 560 422 Q 620 410 682 418 M 560 432 Q 618 432 678 446 M 556 442 Q 608 452 660 474"/></g>')


def cat(opened=0.5, look=(-16, 6), pupil=13, mouth="smirk", tilt=0.0):
    head_parts = ears() + head() + eye("l", opened, look, pupil) + eye("r", opened, look, pupil) + face(mouth)
    return (tail() + body() + paws() +
            f'<g id="head_rig" transform="rotate({tilt} 500 480)">{head_parts}</g>')


def svg(content, w=1000, h=1000):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect id="bg" width="{w}" height="{h}" fill="{BG}"/>{content}</svg>')


POSES = [
    ("Ну и?", dict(opened=0.5, look=(-16, 6), mouth="smirk", tilt=-8)),
    ("Что?!", dict(opened=1.0, look=(0, 0), pupil=8, mouth="o", tilt=0)),
    ("Блаженство", dict(opened=0.0, mouth="w", tilt=6)),
    ("Подозрение", dict(opened=0.38, look=(16, 0), mouth="flat", tilt=-3)),
]


LID_STATES = {"75": 0.75, "50": 0.5, "38": 0.38, "20": 0.2, "0": 0.0}


def part_svg(content):
    """Часть рига: прозрачный холст 1000×1000, координаты общие для всех частей."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" '
            f'viewBox="0 0 1000 1000">{content}</svg>')


def rig_parts():
    """Части для перекладки в EffectCraft: имя слоя -> SVG."""
    parts = {"tail": tail(), "body": body(), "paws": paws(), "head": head()}
    ear = ears().split('</g>')
    parts["ear_l"], parts["ear_r"] = ear[0] + '</g>', ear[1] + '</g>'
    for side, (cx, cy) in EYES.items():
        parts[f"white_{side}"] = (f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" fill="{EYE}" '
                                  f'stroke="{INK}" stroke-width="7"/>')
        # Маска для радужки и зрачка: белок без обводки
        parts[f"matte_{side}"] = f'<ellipse cx="{cx}" cy="{cy}" rx="{RX - 4}" ry="{RY - 4}" fill="#000"/>'
        parts[f"iris_{side}"] = f'<circle cx="{cx}" cy="{cy}" r="20" fill="{IRIS}"/>'
        parts[f"pupil_{side}"] = (f'<circle cx="{cx - 3}" cy="{cy + 1}" r="13" fill="{INK}"/>'
                                  f'<circle cx="{cx - 9}" cy="{cy - 7}" r="4.5" fill="{FUR}"/>')
        for name, opened in LID_STATES.items():
            parts[f"lid_{side}_{name}"] = lid(cx, cy, opened, sag=8 if opened >= 0.5 else 2)
    f = face("smirk").split('</g>')
    parts["nose"], parts["whiskers"] = f[0] + '</g>', f[2] + '</g>'
    for m, d in MOUTHS.items():
        parts[f"mouth_{m}"] = (f'<path d="{d}" fill="{"#7a3b43" if m == "o" else "none"}" stroke="{INK}" '
                               f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    return parts


def main():
    here = Path(__file__).parent / "parts"
    here.mkdir(exist_ok=True)
    rig = here / "rig"
    rig.mkdir(exist_ok=True)
    for name, content in rig_parts().items():
        (rig / f"{name}.svg").write_text(part_svg(content), encoding="utf-8")
    (here / "cat.svg").write_text(svg(cat()), encoding="utf-8")
    cells = []
    for i, (title, kw) in enumerate(POSES):
        x = i * 1000
        cells.append(f'<g transform="translate({x} 0)">{cat(**kw)}</g>'
                     f'<text x="{x + 500}" y="980" font-family="Arial" font-size="52" '
                     f'text-anchor="middle" fill="{INK}">{title}</text>')
    (here / "sheet.svg").write_text(svg("".join(cells), 4000, 1000), encoding="utf-8")


if __name__ == "__main__":
    main()
