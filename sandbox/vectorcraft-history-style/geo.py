"""Береговая линия Natural Earth (через world-atlas, TopoJSON) → пути SVG в пикселях кадра."""
import json
import math

WORLD_ATLAS = r"C:/projects/cursor/earth3D/node_modules/world-atlas/land-10m.json"


def load_rings(path=WORLD_ATLAS):
    """Все кольца суши в градусах [(lon, lat), ...]."""
    topo = json.load(open(path))
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        out = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return out

    rings = []
    for g in topo["objects"]["land"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        for poly in polys:
            for r in poly:
                rings.append(ring(r))
    return rings


class View:
    """Равнопромежуточная проекция с поправкой cos(широты) по центру кадра."""

    def __init__(self, lon0, lat0, px_per_deg, w=1920, h=1080):
        self.lon0, self.lat0, self.k, self.w, self.h = lon0, lat0, px_per_deg, w, h
        self.c = math.cos(math.radians(lat0))

    def xy(self, lon, lat):
        return (self.w / 2 + (lon - self.lon0) * self.k * self.c,
                self.h / 2 - (lat - self.lat0) * self.k)

    def paths(self, rings, margin=200, min_step=2.5, min_area=60):
        """Кольца в кадре → строки d. Точки за полями прижимаются к рамке, мелочь отбрасывается."""
        lo_x, hi_x = -margin, self.w + margin
        lo_y, hi_y = -margin, self.h + margin
        out = []
        for r in rings:
            pts = [self.xy(*p) for p in r]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if max(xs) < lo_x or min(xs) > hi_x or max(ys) < lo_y or min(ys) > hi_y:
                continue
            kept = []
            for x, y in pts:
                x = min(max(x, lo_x), hi_x)
                y = min(max(y, lo_y), hi_y)
                if kept and abs(x - kept[-1][0]) + abs(y - kept[-1][1]) < min_step:
                    continue
                kept.append((x, y))
            if len(kept) < 4:
                continue
            area = 0.5 * abs(sum(kept[i][0] * kept[i - 1][1] - kept[i - 1][0] * kept[i][1]
                                 for i in range(len(kept))))
            if area < min_area:
                continue
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in kept) + "Z")
        return out
