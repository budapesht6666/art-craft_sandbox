"""Серия по раскадровке: storyboard.json + voice/edl.json -> local/ec/episode.json (+ local/ec/assets/, sound/cues.json).

python gen_episode.py           — все склейки
python gen_episode.py S11 S12   — только эти (по префиксу id), остальное в episode.json не трогается

Обобщение ../anim/gen_shot.py. Каждая склейка — своя композиция EffectCraft (собирает
build_episode.js, рендер — render.py). Всё пересобираемое — в local/ (в git не идёт). Время задаётся словами голоса:
  "8:horse#2"     — начало второго слова horse в реплике 8
  "12:look$+0.75" — конец слова look плюс 0,75 с;  "12:start", "12:end" — начало и конец реплики
  "start", "end"  — начало и конец склейки
Фигуры: рисунок с листа × тон локации, тень под ногами, точка опоры у ступней. «_stone»
(окаменевшая версия) делается из рисунка кодом: серый камень с трещинами того же размера,
поэтому превращение — Linear Wipe без подгонки.
"""
import json
import math
import random
import re
import shutil
import unicodedata
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

HERE = Path(__file__).parent
SB = json.loads((HERE / "storyboard.json").read_text(encoding="utf-8"))
EDL = json.loads((HERE / "voice" / "edl.json").read_text(encoding="utf-8"))
LOCAL_EC = HERE / "local" / "ec"      # проект EffectCraft и его файлы: run_script читает только папку проекта
ASSETS = LOCAL_EC / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
FPS = SB.get("fps", 24)
W, H = 1920, 1080
K_STAND = SB.get("k", 70)          # масштаб фигур, % (стоящая фигура листа ~740 px -> ~520 px)
PAD = 60

WORDS = {}
for w in EDL["words"]:
    WORDS.setdefault(w["line"], []).append(w)


def norm(w):
    """Слово для сравнения: без регистра, диакритики (Danaë, fiancé) и пунктуации."""
    w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", w.lower())


# ---------- время ----------

def resolve(a, shot):
    """Якорь -> секунды серии."""
    if isinstance(a, (int, float)):
        return float(a)
    m = re.fullmatch(r"(?:(\d+):)?([A-Za-z0-9'ë]+)(?:#(\d+))?(\$)?([+-]\d+(?:\.\d+)?)?", a)
    if not m:
        raise SystemExit(f"{shot['id']}: не понял якорь {a!r}")
    line, word, nth, at_end, off = m.groups()
    off = float(off or 0)
    if line is None:
        if word == "start":
            return shot["t0"] + off
        if word == "end":
            return shot["t1"] + off
        line = shot["line"]
    ws = WORDS.get(int(line))
    if not ws:
        raise SystemExit(f"{shot['id']}: нет слов реплики {line}")
    if word == "start":
        return ws[0]["t0"] + off
    if word == "end":
        return ws[-1]["t1"] + off
    hits = [w for w in ws if norm(w["w"]) == norm(word)]
    n = int(nth or 1)
    if len(hits) < n:
        raise SystemExit(f"{shot['id']}: в реплике {line} нет слова {word!r} #{n}: "
                         f"{' '.join(w['w'] for w in ws)}")
    w = hits[n - 1]
    return (w["t1"] if at_end else w["t0"]) + off


def frame(t):
    return round(t * FPS) / FPS


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = max(0.0, min(1.0, u))
    return 1 - (1 - u) ** 2


def frames(t0, t1, step=1):
    return [round(f / FPS, 5) for f in range(round(t0 * FPS), round(t1 * FPS) + 1, step)]


def pop(t, t0, k):
    """Сплющить-растянуть при смене позы: 0,25 с, затухающая пружина ±7 %."""
    u = (t - t0) / 0.25
    if u < 0 or u > 1:
        return k, k
    s = 0.07 * math.cos(math.pi * 2 * u) * (1 - u)
    return k * (1 + s), k * (1 - s)


# ---------- картинки ----------

def stone_of(im, seed):
    """Цветной рисунок -> серый камень с трещинами, тот же размер и альфа."""
    a = im.getchannel("A")
    g = ImageOps.grayscale(im.convert("RGB"))
    lut = [int(28 + v * 0.62) if v < 70 else int(105 + v * 0.42) for v in range(256)]
    g = g.point(lut)
    rgb = Image.merge("RGB", [g.point(lambda v: min(255, v + 4)), g, g.point(lambda v: max(0, v - 6))])
    d = ImageDraw.Draw(rgb)
    rnd = random.Random(seed)
    w, h = im.size
    for _ in range(int(w * h / 26000) + 4):
        x, y = rnd.uniform(0.1, 0.9) * w, rnd.uniform(0.1, 0.95) * h
        if a.getpixel((int(x), int(y))) < 200:
            continue
        pts = [(x, y)]
        for _ in range(rnd.randint(2, 4)):
            x += rnd.uniform(-28, 28)
            y += rnd.uniform(10, 34)
            pts.append((x, y))
        d.line(pts, fill=(70, 70, 66), width=3)
    out = rgb.convert("RGBA")
    out.putalpha(a)
    return out


def feet(a):
    """Середина ступней: столбцы с альфой в нижних 6 % рисунка."""
    w, h = a.size
    band = a.crop((0, int(h * 0.94), w, h)).point(lambda v: 255 if v > 128 else 0)
    box = band.getbbox()
    if not box:
        return w / 2, 0, w
    cols = [x for x in range(box[0], box[2]) if band.crop((x, 0, x + 1, band.height)).getbbox()]
    return (cols[0] + cols[-1]) / 2, cols[0], cols[-1]


_cache = {}


def asset(pose, tint, stone=False, shadow=None):
    """-> {src, anchor, size, rel}: фигура в тоне локации, с тенью, опора у ступней (или центр)."""
    key = (pose, tuple(tint or ()), stone, shadow)
    if key in _cache:
        return _cache[key]
    P = SB["poses"][pose]
    if isinstance(P, str):
        P = {"src": P}
    im = Image.open(HERE / P["src"]).convert("RGBA")
    if P.get("flip"):
        im = ImageOps.mirror(im)
    if stone:
        im = stone_of(im, hash(pose) % 1000)
    a = im.getchannel("A")
    if tint:
        rgb = ImageChops.multiply(im.convert("RGB"), Image.new("RGB", im.size, tuple(tint)))
        im = rgb.convert("RGBA")
        im.putalpha(a)
    w, h = im.size
    shadow = P.get("shadow", True) if shadow is None else shadow
    name = (f"{pose}{'_stone' if stone else ''}_{'%02x%02x%02x' % tuple(tint) if tint else 'raw'}"
            f"{'' if shadow else '_ns'}.png")
    if shadow:
        fx, x0, x1 = feet(a)
        canvas = Image.new("RGBA", (w + 2 * PAD, h + PAD), (0, 0, 0, 0))
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        half = max((x1 - x0) * 0.62, w * 0.18)
        cx, cy = fx + PAD, h - 4
        ImageDraw.Draw(sh).ellipse((cx - half, cy - 22, cx + half, cy + 20), fill=(20, 10, 10, 110))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
        canvas.alpha_composite(im, (PAD, 0))
        anchor = [cx, h]
    else:
        canvas = im
        anchor = P.get("anchor", [w / 2, h / 2] if P.get("center", True) else [w / 2, h])
    canvas.save(ASSETS / name)
    _cache[key] = {"src": str(ASSETS / name).replace("\\", "/"), "anchor": anchor, "size": list(canvas.size),
                   "rel": P.get("rel", 1.0)}
    return _cache[key]


FONT = HERE.parents[1] / "brand" / "fonts" / "LuckiestGuy-Regular.ttf"   # шрифт канала (Apache 2.0)
_titles = {}


def title_png(text, size):
    """Титр картинкой шрифтом канала: белый, тёмная обводка, мягкая тень; длинный — в две строки.
    -> ({src, anchor}, сдвиг центра вверх от базовой линии)."""
    from PIL import ImageFont
    text = re.sub(r'"([^"]*)"', lambda m: "“" + m.group(1) + "”", text).replace("'", "’")   # фигурные кавычки
    key = (text, size)
    if key in _titles:
        return _titles[key]
    font = ImageFont.truetype(str(FONT), int(size * 1.05))
    lines = [text]
    if font.getlength(text) > 1700 and " " in text:          # длинный — пополам по словам
        ws = text.split()
        cut = min(range(1, len(ws)), key=lambda i: abs(font.getlength(" ".join(ws[:i])) - font.getlength(" ".join(ws[i:]))))
        lines = [" ".join(ws[:cut]), " ".join(ws[cut:])]
    sw = max(4, int(size * 0.11))
    lh = int(size * 1.15)
    w = int(max(font.getlength(l) for l in lines)) + 4 * sw + 40
    h = lh * len(lines) + 4 * sw + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i, l in enumerate(lines):
        x = (w - font.getlength(l)) / 2
        y = 20 + 2 * sw + i * lh
        ImageDraw.Draw(sh).text((x + sw * 0.6, y + sw * 0.9), l, font=font, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
        ImageDraw.Draw(im).text((x, y), l, font=font, fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(28, 20, 14, 255))
    out = sh.filter(ImageFilter.GaussianBlur(sw * 0.8))
    out.alpha_composite(im)
    d = ASSETS / "titles"
    d.mkdir(exist_ok=True)
    name = f"t_{abs(hash(key)) % 10 ** 10}.png"
    out.save(d / name)
    # базовая линия старых текстовых слоёв ≈ низ последней строки; центр картинки — выше на столько
    cy = h / 2 - (20 + 2 * sw + (len(lines) - 1) * lh + size * 0.82)
    _titles[key] = ({"src": str(d / name).replace("\\", "/"), "anchor": [w / 2, h / 2]}, -cy)
    return _titles[key]


# ---------- склейки ----------

def build_shot(S, loc):
    t0, t1 = S["t0"], S["t1"]
    dur = t1 - t0
    rnd = random.Random(S["id"])
    L, solids, texts, cues = [], [], [], []
    tint = loc.get("tint")
    floor = loc.get("floor", 960)

    def T(a):
        return resolve(a, S)

    def local(keys):
        return [[round(k[0] - t0, 5)] + k[1:] for k in keys]

    def layer(name, src, a, b, **kw):
        d = {"name": name, "src": src, "in": round(max(0, a - t0), 5), "out": round(min(dur, b - t0), 5),
             "anchor": None, "pos": [], "scale": [], "rot": [], "opacity": [], "wipe": None, "parent": "cam"}
        d.update(kw)             # ключи во времени серии; в склейку переводятся в конце
        L.append(d)
        return d

    card = S.get("card")            # карточка главы: размытый фон, затемнение, номер и название
    if card:
        S["closeup"] = True
    # фон: 2752×1536 -> 1920×1080 (×0,6977); крупный план — увеличен и размыт
    bg = HERE / loc["bg"]
    bw, bh = Image.open(bg).size
    kbg = 100 * W / bw
    if S.get("closeup"):
        layer("bg", str(bg).replace("\\", "/"), t0, t1, anchor=[bw / 2, bh / 2], parent="none",
              pos=[[t0, W / 2, H / 2 - 40]], scale=[[t0, kbg * 1.5, kbg * 1.5]],
              effects=[{"match": "ADBE Gaussian Blur 2", "props": {"Blurriness": 30}}])
    else:
        layer("bg", str(bg).replace("\\", "/"), t0, t1, anchor=[bw / 2, bh / 2],
              pos=[[t0, W / 2, H / 2]], scale=[[t0, kbg, kbg]])

    for o in S.get("overlays", []):     # полноэкранные слои (пунктир на карте) с Linear Wipe
        a, b = T(o.get("at", "start")), T(o.get("until", "end"))
        ow, oh = Image.open(HERE / o["src"]).size
        wipe = None
        if "wipe" in o:
            w0, w1, ang = o["wipe"]
            wipe = {"angle": ang, "feather": 30, "keys": [[T(w0), 100], [T(w1), 0]]}
        layer("overlay", str(HERE / o["src"]).replace("\\", "/"), a, b, anchor=[ow / 2, oh / 2],
              pos=[[a, W / 2, H / 2]], scale=[[a, 100 * W / ow, 100 * W / ow]], wipe=wipe)

    # актёры: позы по времени, вход/выход, дрожь, дыхание, окаменение
    for i, A in enumerate(S.get("actors", [])):
        poses = A["poses"]
        a_tint = A.get("tint", tint)                 # созвездие и т.п.: свой тон
        x, y = A["x"], A.get("y", floor)
        rot_keys = [(T(r[0]), r[1]) for r in A.get("rot", [])]     # поворот по якорям (плавно)

        def rot_at(t, keys=rot_keys):
            """Поворот по ключам: до первого 0, между ключами плавно, после последнего — последний."""
            if not keys or t <= keys[0][0]:
                return keys[0][1] if keys and t >= keys[0][0] else 0.0
            for (ra, rv), (rb, rw) in zip(keys, keys[1:]):
                if ra <= t <= rb:
                    return rv + (rw - rv) * smooth((t - ra) / max(0.01, rb - ra))
            return keys[-1][1]
        k0 = A.get("k", K_STAND)
        a_until = T(A["until"]) if "until" in A else t1
        stone = A.get("stone")
        t_stone = max(T(stone["at"]), t0) if stone else None      # началось до склейки — сразу статуя
        shakes = [(T(s[0]), T(s[1])) for s in A.get("shake", [])]
        enter = A.get("enter")
        t_enter0 = T(enter.get("at", "start")) if enter else None
        # move: [[от, до, x, y?], ...] — плавный переход из текущего места в (x, y)
        moves = [(T(m[0]), T(m[1]), m[2], m[3] if len(m) > 3 else None) for m in A.get("move", [])]
        phase = rnd.uniform(0, 6.28)

        def place(t):
            """-> (x, y, rot) без дрожи."""
            px, py, rot = x, y, 0.0
            if enter and t_enter0 is not None:
                d = enter.get("dur", 0.8)
                u = (t - t_enter0) / d
                fx, fy = enter.get("from_x", x), enter.get("from_y", y)
                if u < 1:
                    e = ease_out(max(0.0, u))
                    px, py = fx + (x - fx) * e, fy + (y - fy) * e
                    if enter.get("walk", fy == y):
                        ph = 2 * math.pi * 2.5 * (t - t_enter0)
                        py -= 10 * abs(math.sin(ph))
                        rot = 2.5 * math.sin(ph)
            for ma, mb, mx, my in moves:
                if t <= ma:
                    break
                u = smooth((t - ma) / max(0.01, mb - ma))
                my = py if my is None else my
                if u < 1 and A.get("walk_moves", True):
                    ph = 2 * math.pi * 2.5 * (t - ma)
                    rot = 2.5 * math.sin(ph)
                    py -= 10 * abs(math.sin(ph)) * (1 - u)
                px, py = px + (mx - px) * u, py + (my - py) * u
            return px, py, rot

        for j, (pose, at) in enumerate(poses):
            a = T(at) if at != "start" else t0
            b = T(poses[j + 1][1]) if j + 1 < len(poses) else a_until
            if b <= t0 or a >= t1:
                continue
            ast = asset(pose, a_tint, shadow=A.get("shadow"))
            k = k0 * ast["rel"]
            lay = layer(f"a{i}_{pose}", ast["src"], a, b, anchor=ast["anchor"],
                        opacity=[[T(o[0]), o[1]] for o in A.get("opacity", [])])
            for t in frames(max(a, t0), min(b, t1)):
                px, py, rot = place(t)
                frozen = t_stone is not None and t >= t_stone
                dx = dy = 0
                if not frozen and any(s0 <= t <= s1 for s0, s1 in shakes):
                    dx, dy = rnd.uniform(-6, 6), rnd.uniform(-3, 3)
                lay["pos"].append([t, round(px + dx, 1), round(py + dy, 1)])
                sx, sy = pop(t, a, k) if (a > t0 + 0.01 or A.get("pop_first")) else (k, k)
                if not frozen and A.get("breathe", True):
                    b_ = math.sin(2 * math.pi * 0.9 * t + phase)
                    sx, sy = sx * (1 - 0.006 * b_), sy * (1 + 0.012 * b_)
                lay["scale"].append([t, round(sx, 3), round(sy, 3)])
                rot += rot_at(t)
                lay["rot"].append([t, round(rot, 2)])
            if stone and a <= t_stone < b:
                sa = asset(stone.get("pose", pose), tint, stone="pose" not in stone)
                px, py, _ = place(t_stone)
                layer(f"a{i}_stone", sa["src"], t_stone, a_until, anchor=sa["anchor"],
                      pos=[[t_stone, px, py]], scale=[[t_stone, k, k]],
                      wipe={"angle": 180, "feather": 40, "keys": [[t_stone, 100], [t_stone + stone.get("dur", 0.9), 0]]})
                if t_stone > t0 + 0.05 and not any(c[0] == "ice_crack" and abs(c[1] - t_stone) < 0.4 for c in cues):
                    cues += [["ice_crack", t_stone], ["stone_hit", t_stone + 0.05]]   # уже статуя — без звука;
                                                                                      # толпа каменеет — один звук

    # реквизит: путь по точкам, вращение, покачивание на волнах
    for i, Pp in enumerate(S.get("props", [])):
        ast = asset(Pp["pose"], Pp.get("tint", tint))
        k = Pp.get("k", 60) * ast["rel"]
        a = T(Pp.get("at", "start"))
        b = T(Pp.get("until", "end"))
        if "route" in Pp:     # равномерно по точкам кривой (карта)
            pts = json.loads((HERE / Pp["route"]).read_text(encoding="utf-8"))
            r0, r1 = T(Pp["route_from"]), T(Pp["route_to"])
            path = [[r0 + (r1 - r0) * n / (len(pts) - 1), p[0], p[1]] for n, p in enumerate(pts)]
        else:
            path = [[T(p[0]), p[1], p[2]] for p in Pp["path"]]
        lay = layer(f"p{i}_{Pp['pose']}", ast["src"], a, b, anchor=ast["anchor"])
        spin = Pp.get("spin", 0)
        for t in frames(a, b):
            if t <= path[0][0]:
                px, py = path[0][1:]
            elif t >= path[-1][0]:
                px, py = path[-1][1:]
            else:
                for (ta, xa, ya), (tb, xb, yb) in zip(path, path[1:]):
                    if ta <= t <= tb:
                        u = (t - ta) / max(0.01, tb - ta)
                        u = u if Pp.get("linear") or "route" in Pp else smooth(u)
                        px, py = xa + (xb - xa) * u, ya + (yb - ya) * u
                        break
            rot = spin * (t - a)
            if Pp.get("bob"):
                py += Pp["bob"] * math.sin(2 * math.pi * 0.6 * t)
                rot += 4 * math.sin(2 * math.pi * 0.45 * t)
            sx, sy = pop(t, a, k) if Pp.get("pop", True) and a > t0 + 0.01 else (k, k)
            lay["pos"].append([t, round(px, 1), round(py, 1)])
            lay["scale"].append([t, round(sx, 3), round(sy, 3)])
            lay["rot"].append([t, round(rot, 2)])

    for f in S.get("flash", []):
        tf = T(f)
        solids.append({"name": "flash", "color": [1.0, 0.95, 0.72], "in": max(0, tf - t0 - 0.05),
                       "out": min(dur, tf - t0 + 0.45),
                       "opacity": [[tf - t0 - 0.05, 0], [tf - t0, 40], [tf - t0 + 0.4, 0]]})

    if card:
        solids.append({"name": "dim", "color": [0.05, 0.04, 0.03], "in": 0, "out": dur, "opacity": [[0, 55]]})
        S.setdefault("titles", [])
        S["titles"] = [{"text": card["num"], "at": "start+0.15", "y": 440, "size": 64, "sfx": False},
                       {"text": card["title"], "at": "start+0.45", "y": 590, "size": 150, "sfx": False}] + S["titles"]
        cues.append(["transition", t0 + 0.05])
    for X in S.get("titles", []):
        a = T(X["at"])
        b = T(X["until"]) if "until" in X else t1
        if b - a < 0.6:                 # конец раньше начала — чаще всего слово встречается раньше: нужен #2
            raise SystemExit(f"{S['id']}: титр «{X['text']}» держится {b - a:.2f} с ({X['at']} → {X.get('until', 'end')})")
        img, cy = title_png(X["text"], X.get("size", 96))
        texts.append({"text": X["text"], "src": img["src"], "anchor": img["anchor"], "in": a - t0, "out": b - t0,
                      "size": X.get("size", 96), "pos": [X.get("x", W / 2), X.get("y", 1010) - cy],
                      "scale": [[a - t0, 150, 150], [a - t0 + 0.12, 94, 94], [a - t0 + 0.22, 100, 100]],
                      "opacity": [[max(a - t0, b - t0 - 0.2), 100], [b - t0, 0]] if b < t1 else []})
        cues.append(["title", a] if X.get("sfx", True) else ["", 0])

    for c in S.get("sfx", []):          # [звук, время, конец склейки] — фон обрывается со склейкой
        cues.append([c[0], T(c[1]), t1])

    # камера: медленный наезд через всю склейку, «рывки» на словах, тряска
    C = S.get("cam", {})
    cx, cy = C.get("center", [W / 2, H / 2 + 60])
    z0, z1 = C.get("from", 100), C.get("to", 104)
    punches = [(T(p[0]), p[1]) for p in C.get("punch", [])]
    cshakes = [(T(s[0]), s[1]) for s in C.get("shake", [])]
    for st in S.get("actors", []):
        if st.get("stone"):
            cshakes.append((T(st["stone"]["at"]), st["stone"].get("dur", 0.9)))
    cam = {"anchor": [cx, cy], "pos": [], "scale": []}
    for t in frames(t0, t1):
        s = z0 + (z1 - z0) * smooth((t - t0) / max(0.1, dur))
        for tp, add in punches:
            s += add * smooth((t - tp) / 0.12)
        dx = dy = 0
        for ts, d in cshakes:
            if ts <= t <= ts + d:
                kk = 1 - (t - ts) / d * 0.6
                dx, dy = rnd.uniform(-7, 7) * kk, rnd.uniform(-5, 5) * kk
        cam["scale"].append([round(t - t0, 5), round(s, 3), round(s, 3)])
        cam["pos"].append([round(t - t0, 5), round(cx + dx, 1), round(cy + dy, 1)])

    for d in L:
        for k in ("pos", "scale", "rot", "opacity"):
            d[k] = local(d[k])
        if d["wipe"]:
            d["wipe"]["keys"] = local(d["wipe"]["keys"])
    return {"name": S["id"], "start": t0, "duration": round(dur, 5), "cam": cam, "layers": L,
            "solids": solids, "texts": texts}, cues


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    shots = SB["shots"]
    for S in shots:
        S["line"] = int(S["at"].split(":")[0])
    for n, S in enumerate(shots):
        S["t0"] = 0.0 if n == 0 else frame(resolve(S["at"], S) - SB.get("cut_lead", 0.08))
    for n, S in enumerate(shots):
        S["t1"] = shots[n + 1]["t0"] if n + 1 < len(shots) else frame(EDL["duration"])
    bad = [f"{S['id']} ({S['at']}) {S['t0']:.2f} с — не позже предыдущей ({shots[n - 1]['id']} {shots[n - 1]['t0']:.2f} с)"
           for n, S in enumerate(shots) if n and S["t0"] <= shots[n - 1]["t0"] + 0.2]
    if bad:     # чаще всего слово встречается в реплике раньше: нужен #2
        raise SystemExit("склейки не по порядку:\n  " + "\n  ".join(bad))
    out_path = LOCAL_EC / "episode.json"
    shutil.copy(HERE / "build_episode.js", LOCAL_EC / "build_episode.js")
    old = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() and only else {"comps": []}
    old_comps = {c["name"]: c for c in old["comps"]}
    comps, cues = [], []
    for S in shots:
        loc = SB["locs"][S["loc"]]
        if only and not any(S["id"].startswith(o) for o in only) and S["id"] in old_comps:
            c = old_comps[S["id"]]
            if abs(c["start"] - S["t0"]) < 1e-3 and abs(c["duration"] - (S["t1"] - S["t0"])) < 1e-3:
                comps.append(c)
                continue
        c, q = build_shot(S, loc)
        comps.append(c)
        cues += q
    if not only:
        (HERE / "sound" / "cues.json").write_text(json.dumps(sorted(cues, key=lambda c: c[1]), indent=0),
                                                  encoding="utf-8")
    out_path.write_text(json.dumps({"fps": FPS, "size": [W, H], "comps": comps,
                                    "duration": frame(EDL["duration"])}), encoding="utf-8")
    for S in shots:
        print(f"{S['id']:5s} {S['t0']:7.2f}–{S['t1']:7.2f}  {S['loc']}")
    print("склеек", len(comps), "слоёв", sum(len(c["layers"]) for c in comps))


if __name__ == "__main__":
    main()
