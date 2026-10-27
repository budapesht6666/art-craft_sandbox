"""Карта к кадру 7: ящик плывёт из Аргоса на Сериф. Стиль — как sandbox/history/vectorcraft/frame_map.py.

python map.py  →  map/map_base.svg (карта с подписями) и map/map_route.svg (только пунктир, прозрачный)
Растр: VectorCraft open_file → export png (scale 1), путь пунктира проявляется Linear Wipe в EffectCraft.
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[3] / "sandbox" / "history" / "vectorcraft"))   # geo.py
from geo import View, load_rings  # noqa: E402

W, H = 1920, 1080
INK = "#2b1d0e"
v = View(lon0=23.45, lat0=37.45, px_per_deg=560)
land_d = " ".join(v.paths(load_rings(), min_area=30))

ARGOS = (22.73, 37.63)
SERIPHOS = (24.47, 37.15)
# Пунктир: из Арголидского залива на юг, потом на восток к Серифу
route = [v.xy(22.80, 37.50), v.xy(22.95, 36.95), v.xy(23.95, 36.90), v.xy(24.36, 37.12)]
(x0, y0), (x1, y1), (x2, y2), (x3, y3) = route
route_d = f"M{x0:.0f},{y0:.0f} C{x1:.0f},{y1:.0f} {x2:.0f},{y2:.0f} {x3:.0f},{y3:.0f}"


def label(x, y, text, size, fill, stroke, spacing=6, rotate=0):
    common = (f'x="{x:.0f}" y="{y:.0f}" font-family="Arial Black" font-size="{size}" text-anchor="middle" '
              f'letter-spacing="{spacing}" transform="rotate({rotate} {x:.0f} {y:.0f})"')
    return (f'<text {common} fill="{stroke}" stroke="{stroke}" stroke-width="{size * 0.22:.1f}" '
            f'stroke-linejoin="round">{text}</text>\n<text {common} fill="{fill}">{text}</text>')


def city(x, y):
    return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="16" fill="#fff3d6" stroke="{INK}" stroke-width="6"/>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{INK}"/>')


random.seed(3)
waves = "\n".join(
    f'<path d="M{x:.0f},{y:.0f} q12,-9 24,0 q12,9 24,0" fill="none" stroke="#7fb6ec" stroke-width="4" '
    f'stroke-linecap="round" opacity=".55"/>'
    for x, y in [(random.uniform(0, W), random.uniform(0, H)) for _ in range(70)])

ax, ay = v.xy(*ARGOS)
sx, sy = v.xy(*SERIPHOS)
base = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="sea" cx="50%" cy="45%" r="75%">
    <stop offset="0" stop-color="#3f86d6"/><stop offset="1" stop-color="#2459ad"/>
  </radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#sea)"/>
{waves}
<path d="{land_d}" fill="none" stroke="#2e6fc4" stroke-width="70" stroke-linejoin="round"/>
<path d="{land_d}" fill="none" stroke="#5aa2e6" stroke-width="34" stroke-linejoin="round"/>
<path d="{land_d}" fill="none" stroke="#8cc4f0" stroke-width="12" stroke-linejoin="round"/>
<path d="{land_d}" transform="translate(0,9)" fill="#8f6a35"/>
<path d="{land_d}" fill="#dcc08a" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
{city(ax, ay)}
{city(sx, sy)}
{label(ax - 10, ay - 40, "ARGOS", 64, "#fff3d6", INK, 10)}
{label(sx + 10, sy - 48, "SERIPHOS", 56, "#fff3d6", INK, 8)}
{label(*v.xy(24.0, 36.62), "AEGEAN SEA", 46, "#cfe8ff", "#173f80", 12, -4)}
</svg>"""

route_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<path d="{route_d}" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-dasharray="1 30"/>
<path d="{route_d}" fill="none" stroke="#fff6e0" stroke-width="9" stroke-linecap="round" stroke-dasharray="1 30"/>
</svg>"""

out = HERE / "map"
out.mkdir(exist_ok=True)
(out / "map_base.svg").write_text(base, encoding="utf-8")
(out / "map_route.svg").write_text(route_svg, encoding="utf-8")
# Точки кривой — чтобы ящик в EffectCraft плыл ровно по пунктиру
pts = []
for i in range(25):
    t, u = i / 24, 1 - i / 24
    pts.append([round(u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3, 1),
                round(u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3, 1)])
(out / "route_points.json").write_text(json.dumps(pts), encoding="utf-8")
print("map/map_base.svg", len(base) // 1024, "KB; Argos", (round(ax), round(ay)), "Seriphos", (round(sx), round(sy)))
