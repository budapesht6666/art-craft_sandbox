"""Кадр со персонажами в духе Unknown Frequencies: Персей и голова Медузы.

python frame_scene.py  →  svg/scene_perseus.svg
"""
import math
import random

W, H = 1920, 1080
INK = "#20160c"
SKIN = "#fbf7ef"
STONE = "#a3a19a"
STONE_D = "#7c7a73"
random.seed(11)


def tube(points, width, color, outline=7):
    """Конечность: толстая линия с контуром (сначала чёрная, потом цветная)."""
    d = "M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in points[:1]) + (
        " Q" + " ".join(f"{x:.1f},{y:.1f}" for x, y in points[1:]) if len(points) == 3
        else " L" + " ".join(f"{x:.1f},{y:.1f}" for x, y in points[1:]))
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{width + outline * 2}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')


def hatch(x, y, w, h, n, angle=-35, color=INK, sw=3, opacity=0.55):
    """Короткая штриховка тени, как у рисованных каналов."""
    out = []
    dx = math.cos(math.radians(angle)) * h
    dy = math.sin(math.radians(angle)) * h
    for i in range(n):
        px = x + w * i / max(1, n - 1) + random.uniform(-2, 2)
        py = y + random.uniform(-3, 3)
        out.append(f'<path d="M{px:.1f},{py:.1f} l{dx:.1f},{dy:.1f}" stroke="{color}" stroke-width="{sw}" '
                   f'stroke-linecap="round" opacity="{opacity}"/>')
    return "".join(out)


def head(cx, cy, r, skin=SKIN, face=""):
    return (f'<path d="M{cx - r},{cy - r * 0.1} Q{cx - r},{cy - r * 1.1} {cx},{cy - r * 1.1} '
            f'Q{cx + r},{cy - r * 1.1} {cx + r},{cy - r * 0.1} Q{cx + r * 0.95},{cy + r} {cx},{cy + r} '
            f'Q{cx - r * 0.95},{cy + r} {cx - r},{cy - r * 0.1}Z" fill="{skin}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
            + face)


def tunic(x, top, hem, half_top, half_hem, fill, belt="#7b4a22"):
    """Хитон с рваным краем и поясом."""
    zig = []
    n = 7
    for i in range(n + 1):
        px = x + half_hem - 2 * half_hem * i / n
        zig.append(f"{px:.1f},{hem + (10 if i % 2 else 0):.1f}")
    d = f"M{x - half_top},{top} L{x + half_top},{top} L{x + half_hem},{hem} L" + " L".join(zig) + "Z"
    by = top + (hem - top) * 0.45
    return (f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M{x - half_top - 6},{by} Q{x},{by + 10} {x + half_top + 6},{by}" fill="none" stroke="{INK}" stroke-width="20" stroke-linecap="round"/>'
            f'<path d="M{x - half_top - 6},{by} Q{x},{by + 10} {x + half_top + 6},{by}" fill="none" stroke="{belt}" stroke-width="8" stroke-linecap="round"/>'
            + hatch(x - half_hem + 18, hem - 20, half_hem * 0.6, 26, 5))


def perseus(x, y):
    """Персей смотрит влево от головы Медузы, зажмурился, руку с головой вытянул вправо."""
    hx, hy = x - 6, y - 395
    out = []
    # плащ за спиной
    out.append(f'<path d="M{x - 40},{y - 300} Q{x - 150},{y - 200} {x - 190},{y - 60} L{x - 120},{y - 90} L{x - 110},{y - 40} '
               f'L{x - 60},{y - 120} Q{x - 10},{y - 220} {x + 30},{y - 300}Z" fill="#c63b2e" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    out.append(hatch(x - 170, y - 120, 60, 30, 4))
    # ноги и сандалии
    for sx, fx in [(-18, -40), (18, 34)]:
        out.append(tube([(x + sx, y - 150), (x + fx, y - 20)], 22, SKIN))
        out.append(f'<path d="M{x + fx - 24},{y - 6} Q{x + fx},{y - 26} {x + fx + 26},{y - 6}Z" fill="#7b4a22" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
        out.append(f'<path d="M{x + fx - 12},{y - 60} l20,8 M{x + fx - 12},{y - 44} l20,8" stroke="#7b4a22" stroke-width="5"/>')
    out.append(tunic(x, y - 305, y - 140, 46, 66, "#e8dbbd"))
    # меч в ножнах
    out.append(f'<path d="M{x + 40},{y - 225} L{x + 80},{y - 120}" stroke="{INK}" stroke-width="22" stroke-linecap="round"/>'
               f'<path d="M{x + 40},{y - 225} L{x + 80},{y - 120}" stroke="#5b3a1e" stroke-width="10" stroke-linecap="round"/>')
    # рука к голове Медузы
    out.append(tube([(x + 38, y - 290), (x + 120, y - 300), (x + 200, y - 330)], 22, SKIN))
    # щит-зеркало на другой руке
    out.append(tube([(x - 38, y - 290), (x - 70, y - 230)], 22, SKIN))
    out.append(f'<circle cx="{x - 78}" cy="{y - 215}" r="74" fill="#d99a3a" stroke="{INK}" stroke-width="7"/>'
               f'<circle cx="{x - 78}" cy="{y - 215}" r="54" fill="#f1c36a" stroke="#a8691c" stroke-width="5"/>'
               f'<path d="M{x - 112},{y - 236} Q{x - 100},{y - 262} {x - 70},{y - 266}" stroke="#fff8e0" stroke-width="9" stroke-linecap="round" fill="none"/>'
               + hatch(x - 105, y - 165, 50, 22, 4, color="#7a4a10"))
    # голова: зажмурился, отвернулся, капля пота
    face = (f'<path d="M{hx - 40},{hy - 8} l18,9 l-18,9" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M{hx - 2},{hy - 8} l-18,9 l18,9" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M{hx - 50},{hy - 34} l26,10 M{hx + 6},{hy - 34} l-24,10" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M{hx - 34},{hy + 40} q12,-12 24,0" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M{hx + 40},{hy - 30} q12,20 0,30 q-12,-10 0,-30Z" fill="#8fd0f4" stroke="{INK}" stroke-width="4"/>')
    out.append(head(hx, hy, 70, face=face))
    # шлем с гребнем
    out.append(f'<path d="M{hx - 62},{hy - 70} Q{hx - 10},{hy - 200} {hx + 82},{hy - 96} Q{hx + 20},{hy - 104} {hx - 62},{hy - 70}Z" '
               f'fill="#c63b2e" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
               + hatch(hx - 30, hy - 110, 90, 18, 7, angle=-70, color="#7a1d14", sw=3, opacity=0.8))
    out.append(f'<path d="M{hx - 74},{hy - 16} Q{hx - 76},{hy - 84} {hx},{hy - 86} Q{hx + 76},{hy - 84} {hx + 74},{hy - 16} '
               f'L{hx + 56},{hy - 20} Q{hx + 50},{hy - 60} {hx},{hy - 62} Q{hx - 50},{hy - 60} {hx - 56},{hy - 20}Z" '
               f'fill="#d99a3a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    out.append(medusa(x + 215, y - 262))
    return "\n".join(out)


def medusa(cx, cy):
    """Отрубленная голова Медузы: висит за волосы-змей, злые глаза."""
    out = []
    for i, ang in enumerate([-150, -120, -95, -70, -45, -20, -170, 10]):
        a = math.radians(ang)
        x1, y1 = cx + math.cos(a) * 40, cy + math.sin(a) * 40
        x2, y2 = cx + math.cos(a) * 95, cy + math.sin(a) * 95 - 20
        bend = 26 if i % 2 else -26
        mx, my = (x1 + x2) / 2 + bend * math.sin(a), (y1 + y2) / 2 - bend * math.cos(a)
        out.append(tube([(x1, y1), (mx, my), (x2, y2)], 13, "#5fa043", outline=6))
        out.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="13" fill="#5fa043" stroke="{INK}" stroke-width="5"/>'
                   f'<circle cx="{x2 + 4:.1f}" cy="{y2 - 3:.1f}" r="3" fill="{INK}"/>')
    face = (f'<path d="M{cx - 34},{cy - 4} l20,8 M{cx + 34},{cy - 4} l-20,8" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
            f'<circle cx="{cx - 18}" cy="{cy + 12}" r="7" fill="#f2e04a" stroke="{INK}" stroke-width="4"/>'
            f'<circle cx="{cx + 18}" cy="{cy + 12}" r="7" fill="#f2e04a" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M{cx - 18},{cy + 40} q18,-10 36,0" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M{cx - 8},{cy + 36} l3,8 l3,-8" fill="#fff" stroke="{INK}" stroke-width="3"/>')
    out.append(head(cx, cy + 6, 48, skin="#9fcf7e", face=face))
    out.append(hatch(cx + 14, cy + 44, 26, 14, 4, color="#2f5d1f"))
    # рука держит змей
    out.append(f'<circle cx="{cx - 15}" cy="{cy - 68}" r="20" fill="{SKIN}" stroke="{INK}" stroke-width="7"/>')
    return "\n".join(out)


def soldier(x, y):
    """Воин посмотрел на голову и каменеет снизу вверх."""
    hx, hy = x + 4, y - 395
    out = []
    for sx, fx in [(-18, -36), (18, 30)]:
        out.append(tube([(x + sx, y - 150), (x + fx, y - 20)], 22, STONE))
        out.append(f'<path d="M{x + fx - 24},{y - 6} Q{x + fx},{y - 26} {x + fx + 26},{y - 6}Z" fill="{STONE_D}" stroke="{INK}" stroke-width="6"/>')
    out.append(tunic(x, y - 305, y - 140, 46, 66, STONE, belt=STONE_D))
    out.append(f'<path d="M{x - 30},{y - 160} l14,-30 l-6,-24 M{x + 22},{y - 230} l-12,22 l10,18 M{x + 8},{y - 100} l-10,30" '
               f'fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    # камень дошёл до груди: верх хитона ещё цветной
    out.append(f'<path d="M{x - 46},{y - 305} L{x + 46},{y - 305} L{x + 52},{y - 262} Q{x + 20},{y - 248} {x},{y - 268} '
               f'Q{x - 26},{y - 246} {x - 52},{y - 262}Z" fill="#4f7fc4" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    # руки в ужасе вверх, копьё выпало
    out.append(tube([(x - 40, y - 290), (x - 100, y - 340), (x - 96, y - 420)], 22, SKIN))
    out.append(tube([(x + 40, y - 290), (x + 100, y - 340), (x + 104, y - 420)], 22, SKIN))
    face = (f'<circle cx="{hx - 24}" cy="{hy - 4}" r="20" fill="#fff" stroke="{INK}" stroke-width="6"/>'
            f'<circle cx="{hx + 24}" cy="{hy - 4}" r="20" fill="#fff" stroke="{INK}" stroke-width="6"/>'
            f'<circle cx="{hx - 30}" cy="{hy - 2}" r="5" fill="{INK}"/><circle cx="{hx + 18}" cy="{hy - 2}" r="5" fill="{INK}"/>'
            f'<path d="M{hx - 46},{hy - 44} l20,-10 M{hx + 46},{hy - 44} l-20,-10" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
            f'<ellipse cx="{hx - 4}" cy="{hy + 44}" rx="16" ry="22" fill="#5b1d16" stroke="{INK}" stroke-width="6"/>')
    out.append(head(hx, hy, 70, face=face))
    out.append(f'<path d="M{hx - 72},{hy - 20} Q{hx - 74},{hy - 88} {hx},{hy - 90} Q{hx + 74},{hy - 88} {hx + 72},{hy - 20} '
               f'L{hx + 60},{hy - 28} Q{hx + 50},{hy - 66} {hx},{hy - 66} Q{hx - 50},{hy - 66} {hx - 60},{hy - 28}Z" '
               f'fill="#8c8f96" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
    out.append(f'<path d="M{x + 150},{y - 8} L{x + 330},{y - 70}" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>'
               f'<path d="M{x + 150},{y - 8} L{x + 330},{y - 70}" stroke="#7b4a22" stroke-width="6" stroke-linecap="round"/>'
               f'<path d="M{x + 326},{y - 86} L{x + 372},{y - 86} L{x + 334},{y - 58}Z" fill="#c9ccd2" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    # дрожь
    out.append(f'<path d="M{hx - 110},{hy - 60} q-14,14 0,28 M{hx + 110},{hy - 60} q14,14 0,28" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    return "\n".join(out)


def statue(x, y, s, arms):
    """Окаменевший прежний гость на заднем плане: силуэт серым."""
    a = [(x - 20 * s, y - 120 * s), arms[0]], [(x + 20 * s, y - 120 * s), arms[1]]
    return (f'<g opacity=".95">'
            + tube([(x - 10 * s, y - 70 * s), (x - 18 * s, y)], 14 * s, "#9a9690", outline=5)
            + tube([(x + 10 * s, y - 70 * s), (x + 18 * s, y)], 14 * s, "#9a9690", outline=5)
            + f'<path d="M{x - 28 * s},{y - 130 * s} L{x + 28 * s},{y - 130 * s} L{x + 36 * s},{y - 60 * s} L{x - 36 * s},{y - 60 * s}Z" fill="#9a9690" stroke="{INK}" stroke-width="5"/>'
            + tube(a[0], 14 * s, "#9a9690", outline=5) + tube(a[1], 14 * s, "#9a9690", outline=5)
            + f'<circle cx="{x}" cy="{y - 165 * s}" r="{40 * s}" fill="#a8a49e" stroke="{INK}" stroke-width="5"/>'
            + f'<ellipse cx="{x - 12 * s}" cy="{y - 168 * s}" rx="{7 * s}" ry="{9 * s}" fill="{INK}"/><ellipse cx="{x + 12 * s}" cy="{y - 168 * s}" rx="{7 * s}" ry="{9 * s}" fill="{INK}"/>'
            + f'<ellipse cx="{x}" cy="{y - 142 * s}" rx="{7 * s}" ry="{10 * s}" fill="{INK}"/>'
            + f'<path d="M{x - 30 * s},{y - 100 * s} l18,-12 l-4,20" fill="none" stroke="{INK}" stroke-width="3"/></g>')


def background():
    out = [f'''<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#e98b54"/><stop offset=".6" stop-color="#f6c97f"/><stop offset="1" stop-color="#f9e2a8"/>
</linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>''']
    # солнце и дальние скалы
    out.append(f'<circle cx="1500" cy="380" r="120" fill="#fff0c4" opacity=".8"/>')
    out.append(f'<path d="M0,560 L120,430 L210,470 L330,330 L470,420 L560,380 L700,520 L1920,520 L1920,1080 L0,1080Z" fill="#b77b6d" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    out.append(f'<path d="M1100,560 L1250,410 L1340,450 L1480,300 L1600,400 L1720,350 L1920,470 L1920,1080 L1100,1080Z" fill="#a8695e" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    out.append(hatch(250, 470, 200, 40, 9, color="#6d3c33", opacity=0.6) + hatch(1430, 420, 220, 40, 9, color="#5f3229", opacity=0.6))
    # земля
    out.append(f'<path d="M0,700 Q480,660 960,690 Q1440,720 1920,680 L1920,1080 L0,1080Z" fill="#d9c08f" stroke="{INK}" stroke-width="7"/>')
    for _ in range(26):
        px, py = random.uniform(0, W), random.uniform(760, 1060)
        r = random.uniform(5, 14)
        out.append(f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{r * 1.6:.0f}" ry="{r:.0f}" fill="#bfa271" stroke="{INK}" stroke-width="4"/>')
    # колонна
    out.append(f'<path d="M180,760 L180,520 L250,520 L250,760Z" fill="#e9dfca" stroke="{INK}" stroke-width="7"/>'
               f'<path d="M160,520 L270,520 L262,490 L168,490Z" fill="#e9dfca" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
               f'<path d="M203,530 L203,750 M227,530 L227,750" stroke="#b9ab90" stroke-width="5"/>'
               + hatch(232, 600, 14, 30, 3))
    out.append(f'<path d="M1720,780 L1720,640 L1736,628 L1748,646 L1764,620 L1776,640 L1790,632 L1790,780Z" fill="#e9dfca" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
               f'<path d="M1743,660 L1743,770 M1767,660 L1767,770" stroke="#b9ab90" stroke-width="5"/>')
    # окаменевшие на заднем плане
    out.append(statue(470, 720, 0.9, [(400, 520), (520, 530)]))
    out.append(statue(1240, 712, 0.75, [(1180, 650), (1290, 560)]))
    return "\n".join(out)


def caption(text, x, y, size):
    common = f'x="{x}" y="{y}" font-family="Impact" font-size="{size}" text-anchor="middle" letter-spacing="4"'
    return (f'<text {common} fill="{INK}" stroke="{INK}" stroke-width="{size * 0.16:.0f}" stroke-linejoin="round">{text}</text>'
            f'<text {common} fill="#fff3d6">{text}</text>')


svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{background()}
<ellipse cx="760" cy="930" rx="230" ry="26" fill="{INK}" opacity=".22"/>
<ellipse cx="1420" cy="930" rx="200" ry="24" fill="{INK}" opacity=".22"/>
{perseus(720, 920)}
{soldier(1420, 920)}
{caption("DON'T LOOK.", 960, 1040, 120)}
</svg>"""

open("svg/scene_perseus.svg", "w", encoding="utf-8").write(svg)
print("svg/scene_perseus.svg", len(svg) // 1024, "KB")
