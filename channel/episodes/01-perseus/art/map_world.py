"""Карта путешествия Персея: Сериф → край света → горы Атлас → Эфиопия → Сериф. Стиль — как map.py.

python map_world.py  →  map/world_base.svg и map/world_leg{1..4}.svg (пунктир каждого плеча, прозрачный)
                        + map/world_leg{1..4}.json (точки кривой — по ним летит Персей) + world_places.json
Растр: VectorCraft open_file → export png (scale 1).
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
v = View(lon0=11.5, lat0=26.5, px_per_deg=33)
land_d = " ".join(v.paths(load_rings(), min_area=40))

PLACES = {   # (lon, lat) точки маршрута
    "seriphos": (24.47, 37.15),
    "edge": (-17.5, 26.0),        # край света: за Геракловыми столпами, в океане
    "atlas": (-6.5, 31.3),
    "ethiopia": (35.5, 15.5),
}
LEGS = [  # от, до, контрольные точки (lon, lat)
    ("seriphos", "edge", [(14.0, 36.0), (-4.0, 36.5)]),
    ("edge", "atlas", [(-15.0, 30.5), (-10.0, 32.5)]),
    ("atlas", "ethiopia", [(8.0, 24.0), (25.0, 18.0)]),
    ("ethiopia", "seriphos", [(33.0, 28.0), (28.0, 34.5)]),
]


def label(x, y, text, size, fill, stroke, spacing=6, rotate=0):
    common = (f'x="{x:.0f}" y="{y:.0f}" font-family="Arial Black" font-size="{size}" text-anchor="middle" '
              f'letter-spacing="{spacing}" transform="rotate({rotate} {x:.0f} {y:.0f})"')
    return (f'<text {common} fill="{stroke}" stroke="{stroke}" stroke-width="{size * 0.22:.1f}" '
            f'stroke-linejoin="round">{text}</text>\n<text {common} fill="{fill}">{text}</text>')


def city(x, y):
    return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="14" fill="#fff3d6" stroke="{INK}" stroke-width="6"/>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{INK}"/>')


def bez(p0, p1, p2, p3, n=30):
    out = []
    for i in range(n + 1):
        t, u = i / n, 1 - i / n
        out.append([round(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d, 1)
                    for a, b, c, d in zip(p0, p1, p2, p3)])
    return out


random.seed(5)
waves = "\n".join(
    f'<path d="M{x:.0f},{y:.0f} q12,-9 24,0 q12,9 24,0" fill="none" stroke="#7fb6ec" stroke-width="4" '
    f'stroke-linecap="round" opacity=".55"/>'
    for x, y in [(random.uniform(0, W), random.uniform(0, H)) for _ in range(80)])
P = {k: v.xy(*p) for k, p in PLACES.items()}
base = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><radialGradient id="sea" cx="50%" cy="45%" r="75%">
  <stop offset="0" stop-color="#3f86d6"/><stop offset="1" stop-color="#2459ad"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="url(#sea)"/>
{waves}
<path d="{land_d}" fill="none" stroke="#2e6fc4" stroke-width="44" stroke-linejoin="round"/>
<path d="{land_d}" fill="none" stroke="#5aa2e6" stroke-width="22" stroke-linejoin="round"/>
<path d="{land_d}" fill="none" stroke="#8cc4f0" stroke-width="8" stroke-linejoin="round"/>
<path d="{land_d}" transform="translate(0,7)" fill="#8f6a35"/>
<path d="{land_d}" fill="#dcc08a" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>
{''.join(city(*P[k]) for k in ('seriphos', 'atlas', 'ethiopia'))}
<circle cx="{P['edge'][0]:.0f}" cy="{P['edge'][1]:.0f}" r="26" fill="none" stroke="#fff3d6" stroke-width="6" stroke-dasharray="8 8"/>
{label(P['seriphos'][0] + 10, P['seriphos'][1] - 34, "SERIPHOS", 44, "#fff3d6", INK, 6)}
{label(P['edge'][0] + 170, P['edge'][1] + 80, "EDGE OF THE WORLD", 38, "#fff3d6", INK, 4)}
{label(P['atlas'][0] + 40, P['atlas'][1] - 36, "ATLAS MOUNTAINS", 40, "#fff3d6", INK, 4)}
{label(P['ethiopia'][0], P['ethiopia'][1] + 66, "ETHIOPIA", 46, "#fff3d6", INK, 8)}
{label(*v.xy(17.0, 34.0), "MEDITERRANEAN SEA", 34, "#cfe8ff", "#173f80", 10, -3)}
</svg>"""
out = HERE / "map"
out.mkdir(exist_ok=True)
(out / "world_base.svg").write_text(base, encoding="utf-8")
for i, (a, b, ctrl) in enumerate(LEGS, 1):
    p0, p3 = P[a], P[b]
    p1, p2 = v.xy(*ctrl[0]), v.xy(*ctrl[1])
    d = f"M{p0[0]:.0f},{p0[1]:.0f} C{p1[0]:.0f},{p1[1]:.0f} {p2[0]:.0f},{p2[1]:.0f} {p3[0]:.0f},{p3[1]:.0f}"
    leg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<path d="{d}" fill="none" stroke="{INK}" stroke-width="14" stroke-linecap="round" stroke-dasharray="1 26"/>
<path d="{d}" fill="none" stroke="#fff6e0" stroke-width="8" stroke-linecap="round" stroke-dasharray="1 26"/>
</svg>"""
    (out / f"world_leg{i}.svg").write_text(leg, encoding="utf-8")
    (out / f"world_leg{i}.json").write_text(json.dumps(bez(p0, p1, p2, p3)), encoding="utf-8")
(out / "world_places.json").write_text(json.dumps({k: [round(x), round(y)] for k, (x, y) in P.items()}), encoding="utf-8")
print({k: [round(x), round(y)] for k, (x, y) in P.items()})
