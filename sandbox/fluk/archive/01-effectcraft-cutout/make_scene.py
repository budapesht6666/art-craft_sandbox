"""Реквизит пилота: фон, миска на подставке, огурец, рука, тень.

python make_scene.py  ->  parts/scene/*.svg

Фон и миска нарисованы прямо в координатах кадра 1920×1080, поэтому встают на место
без сдвигов. Огурец и рука — на своих холстах, их ставит скрипт сборки.
"""
from pathlib import Path

INK = "#1d1d1f"


def svg(content, w=1920, h=1080):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{content}</svg>')


def background():
    planks = "".join(f'<path d="M 0 {y} L 1920 {y}" stroke="{INK}" stroke-opacity="0.18" stroke-width="3"/>'
                     for y in (880, 960, 1050))
    seams = "".join(f'<path d="M {x} {y1} L {x} {y2}" stroke="{INK}" stroke-opacity="0.18" stroke-width="3"/>'
                    for x, y1, y2 in ((300, 822, 880), (1100, 822, 880), (700, 880, 960), (1500, 880, 960),
                                      (180, 960, 1050), (980, 960, 1050), (1760, 960, 1050)))
    # Картина с рыбой на стене — подмигивание
    picture = (f'<rect x="1440" y="230" width="230" height="170" rx="6" fill="#fbf6ec" stroke="#8a6a48" stroke-width="12"/>'
               f'<path d="M 1500 315 C 1530 280 1590 280 1615 315 C 1590 350 1530 350 1500 315 Z '
               f'M 1615 315 L 1645 290 L 1645 340 Z" fill="#9cc3d5" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
               f'<circle cx="1525" cy="309" r="5" fill="{INK}"/>')
    return svg(f'<rect width="1920" height="822" fill="#f2e8d5"/>'
               f'<rect y="822" width="1920" height="258" fill="#dcc39b"/>{planks}{seams}'
               f'<rect x="-10" y="790" width="1940" height="32" fill="#fbf8f1" stroke="{INK}" stroke-width="6"/>'
               f'{picture}')


def feeder():
    """Миска на деревянной подставке перед котом, центр по x = 820."""
    return svg(
        f'<path d="M 700 790 L 940 790 L 925 1010 L 715 1010 Z" fill="#c98f5a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
        f'<path d="M 712 840 L 928 840" stroke="{INK}" stroke-opacity="0.3" stroke-width="4"/>'
        f'<text x="820" y="935" font-family="Arial Black, Arial" font-weight="bold" font-size="64" '
        f'text-anchor="middle" fill="#fbf6ec" stroke="{INK}" stroke-width="3">FLUK</text>'
        # миска: задний край, корм, передняя стенка
        f'<ellipse cx="820" cy="752" rx="135" ry="26" fill="#6e8ea1" stroke="{INK}" stroke-width="7"/>'
        f'<path d="M 705 752 Q 745 735 780 748 Q 815 732 850 747 Q 890 733 935 752" fill="#9a6a3c" stroke="{INK}" stroke-width="5"/>'
        f'<path d="M 685 752 Q 690 800 730 800 L 910 800 Q 950 800 955 752 Q 900 780 820 780 Q 740 780 685 752 Z" '
        f'fill="#8fb3c9" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')


def cucumber():
    """Огурец по центру холста 400×160 (центр 200, 80)."""
    bumps = "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#2f5f22"/>'
                    for x, y in ((110, 70), (150, 92), (190, 66), (235, 90), (275, 70), (305, 92)))
    return svg(f'<path d="M 75 80 C 75 52 110 48 200 48 C 290 48 330 54 330 80 C 330 106 290 112 200 112 '
               f'C 110 112 75 108 75 80 Z" fill="#5c9a3c" stroke="{INK}" stroke-width="7"/>'
               f'<path d="M 110 62 C 160 56 250 56 300 62" fill="none" stroke="#a9d47f" stroke-width="7" stroke-linecap="round"/>'
               f'{bumps}<path d="M 330 80 L 348 74 L 350 88 Z" fill="#7a5a2a" stroke="{INK}" stroke-width="4"/>',
               400, 160)


def hand():
    """Рука сверху, точка хвата в (300, 1300) холста 600×1400."""
    return svg(f'<rect x="235" y="-20" width="130" height="1180" fill="#5f7fbf" stroke="{INK}" stroke-width="7"/>'
               f'<rect x="228" y="1135" width="144" height="50" rx="10" fill="#4c69a6" stroke="{INK}" stroke-width="7"/>'
               f'<path d="M 250 1185 C 240 1230 250 1275 285 1300 L 330 1300 C 360 1270 362 1220 350 1185 Z" '
               f'fill="#f2c9a5" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
               # большой и указательный пальцы держат огурец
               f'<path d="M 262 1250 C 250 1280 262 1318 282 1322" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
               f'<path d="M 340 1250 C 352 1282 340 1318 320 1322" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>',
               600, 1400)


def shadow():
    return svg('<ellipse cx="200" cy="40" rx="190" ry="30" fill="#000" fill-opacity="0.16"/>', 400, 80)


def main():
    out = Path(__file__).parent / "parts" / "scene"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("bg", background), ("feeder", feeder), ("cucumber", cucumber),
                     ("hand", hand), ("shadow", shadow)):
        (out / f"{name}.svg").write_text(fn(), encoding="utf-8")


if __name__ == "__main__":
    main()
