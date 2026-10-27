"""Кадр-карта в духе Historically: «Тысяча кораблей плывёт к Трое».

python frame_map.py  →  svg/map_troy.svg
"""
import math
import random

from geo import View, load_rings

W, H = 1920, 1080
INK = "#2b1d0e"
random.seed(7)

v = View(lon0=24.6, lat0=38.9, px_per_deg=235)
land = v.paths(load_rings())
land_d = " ".join(land)


def poly(pts):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in (v.xy(*p) for p in pts)) + "Z"


# Области: где суша красится цветом царства (в градусах)
GREECE = [(18.5, 40.2), (20.6, 40.5), (21.8, 40.1), (22.9, 40.45), (23.9, 40.6), (24.9, 38.9),
          (24.7, 37.4), (23.6, 36.0), (21.0, 35.5), (18.5, 36.0)]
TROAD = [(25.9, 40.1), (26.7, 40.25), (27.5, 40.1), (27.7, 39.6), (26.9, 39.25), (25.9, 39.35)]


def wobble(region, step=0.12, amp=0.06):
    """Ломаная границы с мелкими изгибами, чтобы граница не была линейкой."""
    out = []
    for (a, b), (c, d) in zip(region, region[1:] + region[:1]):
        n = max(1, int(math.hypot(c - a, d - b) / step))
        for i in range(n):
            t = i / n
            out.append((a + (c - a) * t + random.uniform(-amp, amp), b + (d - b) * t + random.uniform(-amp, amp)))
    return out


GREECE, TROAD = wobble(GREECE), wobble(TROAD)


def territory(name, region, fill, dark):
    """Цветная часть суши: обрезка по области, своя «толщина» и граница."""
    clip = f'<clipPath id="c_{name}"><path d="{poly(region)}"/></clipPath>'
    return clip + f"""
<g clip-path="url(#c_{name})">
  <path d="{land_d}" transform="translate(0,9)" fill="{dark}"/>
  <path d="{land_d}" fill="{fill}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
</g>
<g clip-path="url(#c_land)">
  <path d="{poly(region)}" fill="none" stroke="{dark}" stroke-width="10" stroke-linejoin="round" opacity=".8"/>
  <path d="{poly(region)}" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>
</g>"""


def ship(x, y, s=1.0, flip=False):
    sx = -s if flip else s
    return f"""<g transform="translate({x:.1f},{y:.1f}) scale({sx:.2f},{s:.2f})">
  <ellipse cx="0" cy="12" rx="26" ry="5" fill="#1d4f97" opacity=".55"/>
  <path d="M-26,0 L26,0 Q22,11 14,12 L-16,12 Q-24,8 -26,0Z" fill="#7b4a22" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M-30,-4 Q-27,0 -24,1" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
  <line x1="0" y1="0" x2="0" y2="-40" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
  <path d="M-15,-36 Q0,-40 15,-36 L13,-8 Q0,-11 -13,-8Z" fill="#f3e6c8" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M-14,-24 Q0,-27 14,-24 L13.5,-18 Q0,-21 -13.6,-18Z" fill="#c8402e"/>
</g>"""


def sword(x, y, s=1.0):
    return f"""<g transform="translate({x:.1f},{y:.1f}) scale({s:.2f})">
  <ellipse cx="0" cy="2" rx="13" ry="5" fill="{INK}" opacity=".35"/>
  <path d="M-9,0 Q0,-9 9,0 Q0,5 -9,0Z" fill="#6b4322" stroke="{INK}" stroke-width="2.5"/>
  <path d="M-4,-6 L-5,-62 L0,-74 L5,-62 L4,-6Z" fill="#c9ccd2" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M0,-10 L0,-64" stroke="#8d929b" stroke-width="2"/>
</g>"""


def crowd(cx, cy, rx, ry, color, n_swords=3):
    """Армия: овал из точек-голов и мечи-значки, как у Historically."""
    out = [f'<ellipse cx="{cx}" cy="{cy + 4}" rx="{rx + 6}" ry="{ry + 5}" fill="{INK}" opacity=".25"/>']
    step = 11
    for j in range(-int(ry / step), int(ry / step) + 1):
        for i in range(-int(rx / step), int(rx / step) + 1):
            x = cx + i * step + (j % 2) * step / 2 + random.uniform(-1.5, 1.5)
            y = cy + j * step * 0.8 + random.uniform(-1.5, 1.5)
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{color}" stroke="{INK}" stroke-width="1.6"/>')
    for k in range(n_swords):
        a = (k + 0.5) / n_swords
        out.append(sword(cx - rx * 0.7 + a * rx * 1.4, cy - ry * 0.2 + random.uniform(-6, 6), 0.9))
    return "\n".join(out)


def fortress(x, y, s=1.0):
    def tower(tx):
        return f"""<rect x="{tx - 22}" y="-92" width="44" height="92" fill="#d9b98a" stroke="{INK}" stroke-width="4"/>
  <path d="M{tx - 22},-70 L{tx + 22},-70" stroke="#a88758" stroke-width="3"/>
  <path d="M{tx - 30},-90 L{tx},-130 L{tx + 30},-90Z" fill="#9b5a2c" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>
  <rect x="{tx - 6}" y="-60" width="12" height="18" rx="6" fill="{INK}"/>"""
    merlons = "".join(f'<rect x="{-60 + i * 20}" y="-66" width="12" height="12" fill="#e4c99c" stroke="{INK}" stroke-width="3.5"/>'
                      for i in range(6))
    return f"""<g transform="translate({x:.1f},{y:.1f}) scale({s:.2f})">
  <ellipse cx="0" cy="6" rx="110" ry="16" fill="{INK}" opacity=".3"/>
  {merlons}
  <rect x="-66" y="-56" width="132" height="56" fill="#e4c99c" stroke="{INK}" stroke-width="4"/>
  <path d="M-66,-30 L66,-30 M-30,-56 L-30,-30 M20,-30 L20,0 M-48,-30 L-48,0 M44,-56 L44,-30" stroke="#b8976a" stroke-width="3"/>
  <path d="M-16,0 L-16,-26 Q0,-42 16,-26 L16,0Z" fill="#6b4322" stroke="{INK}" stroke-width="4"/>
  {tower(-80)}{tower(80)}
</g>"""


def label(x, y, text, size, fill, stroke, spacing=6, rotate=0):
    common = (f'x="{x}" y="{y}" font-family="Arial Black" font-size="{size}" text-anchor="middle" '
              f'letter-spacing="{spacing}" transform="rotate({rotate} {x} {y})"')
    return (f'<text {common} fill="{stroke}" stroke="{stroke}" stroke-width="{size * 0.22:.1f}" '
            f'stroke-linejoin="round">{text}</text>\n<text {common} fill="{fill}">{text}</text>')


# Путь флота: Авлида → мимо Лемноса → берег у Трои
route = [v.xy(23.75, 38.45), v.xy(24.2, 39.35), v.xy(25.0, 39.85), v.xy(25.95, 39.95)]
(x0, y0), (x1, y1), (x2, y2), (x3, y3) = route
route_d = f"M{x0:.0f},{y0:.0f} C{x1:.0f},{y1:.0f} {x2:.0f},{y2:.0f} {x3:.0f},{y3:.0f}"


def bez(t):
    u = 1 - t
    return (u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
            u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3)


ships = []
for t, dx, dy, s in [(0.78, 30, -30, 1.0), (0.80, 90, 10, 0.95), (0.76, -20, 50, 1.05), (0.83, 40, 60, 0.9),
                     (0.58, 100, -60, 0.9), (0.64, -50, 70, 1.0), (0.70, -40, -60, 0.9), (0.52, 90, 70, 1.0),
                     (0.48, 20, 80, 0.95), (0.40, 10, -30, 0.9), (0.36, -70, -20, 0.85), (0.86, 100, -40, 0.9),
                     (0.44, 70, -60, 0.85), (0.74, 120, -10, 0.95), (0.67, 130, 60, 0.9), (0.50, -30, -38, 0.9), (0.53, 34, -14, 1.0), (0.56, -10, 24, 1.05), (0.60, 52, 36, 0.95),
                     (0.62, 8, -46, 0.85), (0.66, 64, -10, 1.0), (0.69, 22, 30, 1.1), (0.73, 70, 40, 0.9),
                     (0.46, -60, 10, 0.95), (0.42, -40, 50, 0.85)]:
    x, y = bez(t)
    ships.append((y + dy, ship(x + dx, y + dy, s)))
ships = "\n".join(s for _, s in sorted(ships))

troy_x, troy_y = v.xy(26.35, 39.93)

random.seed(3)
waves = "\n".join(
    f'<path d="M{x:.0f},{y:.0f} q12,-9 24,0 q12,9 24,0" fill="none" stroke="#7fb6ec" stroke-width="4" '
    f'stroke-linecap="round" opacity=".55"/>'
    for x, y in [(random.uniform(0, W), random.uniform(0, H)) for _ in range(70)])

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="sea" cx="50%" cy="45%" r="75%">
    <stop offset="0" stop-color="#3f86d6"/><stop offset="1" stop-color="#2459ad"/>
  </radialGradient>
</defs>
<clipPath id="c_land"><path d="{land_d}"/></clipPath>
<rect width="{W}" height="{H}" fill="url(#sea)"/>
{waves}
<path d="{land_d}" fill="none" stroke="#2e6fc4" stroke-width="70" stroke-linejoin="round"/>
<path d="{land_d}" fill="none" stroke="#5aa2e6" stroke-width="34" stroke-linejoin="round"/>
<path d="{land_d}" fill="none" stroke="#8cc4f0" stroke-width="12" stroke-linejoin="round"/>
<path d="{land_d}" transform="translate(0,9)" fill="#8f6a35"/>
<path d="{land_d}" fill="#dcc08a" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
{territory("greece", GREECE, "#f2c53d", "#a57f12")}
{territory("troy", TROAD, "#d8352f", "#8b1b18")}
<path d="{route_d}" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-dasharray="1 30"/>
<path d="{route_d}" fill="none" stroke="#fff6e0" stroke-width="9" stroke-linecap="round" stroke-dasharray="1 30"/>
{ships}
{crowd(troy_x + 175, troy_y + 85, 95, 42, "#d8352f", 4)}
{fortress(troy_x + 20, troy_y + 8, 0.95)}
{label(*v.xy(22.0, 38.75), "GREECE", 64, "#fff3d6", INK, 10)}
{label(*v.xy(25.15, 38.2), "AEGEAN SEA", 46, "#cfe8ff", "#173f80", 12, -8)}
{label(troy_x + 20, troy_y - 150, "TROY", 58, "#fff3d6", INK, 10)}
{label(W / 2, H - 70, "A THOUSAND SHIPS", 92, "#fff3d6", INK, 8)}
</svg>"""

open("svg/map_troy.svg", "w", encoding="utf-8").write(svg)
print("svg/map_troy.svg", len(svg) // 1024, "KB,", len(land), "rings")
