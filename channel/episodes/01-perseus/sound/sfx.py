"""Звуки серии из библиотеки канала -> sound/sfx/<имя>.wav (выровнены по громкости) и sound/CREDITS.md.

python sound/sfx.py            — всё, чего ещё нет
python sound/sfx.py bonk stone — пересобрать эти
python sound/sfx.py --list X   — найти в библиотеке файлы по слову (с длительностью)

Библиотека — channel/local/sfx/ (только локально: Sonniss перераспространять нельзя):
  sonniss/2026/ — Sonniss GDC 2026 (коммерческое использование, YouTube, без атрибуции; нельзя
                  перепродавать звуки и учить на них ИИ — sonniss.com/gdc-bundle-license);
  commons/      — Wikimedia Commons, только CC0 и public domain (SOURCES.tsv).
Синтез ffmpeg — только для шумовых звуков, которые и в жизни шум (шипение змей).

Выравнивание: кусок [start, start+dur] (start=None — самое громкое окно), затухания по краям,
усиление до TARGET по максимуму моментальной громкости (EBU R128, окно 400 мс), лимитер −1 dBTP.
Так все звуки равны по ощущаемой громкости, а пропорции задаёт mix.py (категории).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
LIB = HERE.parents[2] / "local" / "sfx"
OUT = HERE / "sfx"
OUT.mkdir(exist_ok=True)
SR = 48000
TARGET = -16.0          # LUFS, максимум моментальной громкости каждого звука

# имя: (кусок имени файла, начало с или None, длительность с, примечание)
SPEC = {
    "whoosh":      ("Woosh Sweep Slide Infographics Basic", None, 0.8, ""),
    "whoosh_big":  ("Woosh Debris", None, 1.2, ""),
    "swoosh":      ("Cartoon Pull Swoosh Readout", None, 0.9, ""),
    "pop":         ("Interface Pop High Short", 0.0, 0.4, ""),
    "pops":        ("Cartoon Pops Random Sequence Reverb", 0.0, 1.2, ""),
    "boing":       ("Accept Boing Crunch", 0.0, 1.0, ""),
    "bonk":        ("Combat Punch Impact Light Hit Delay Crunchy Vintage Quick Smack", None, 0.6, ""),
    "impact":      ("Cartoon Airy Impact Creaks", None, 1.2, ""),
    "dizzy":       ("Cartoon Confused Dizzy", 0.0, 2.0, ""),
    "bubbles":     ("Cartoon Bubbles Short", 0.0, 1.0, ""),
    "transition":  ("Cartoon Transition Bass Down", 0.0, 1.5, ""),
    "braam":       ("Cinematic Horn Braam, Epic, Cinematic, Dark, Instrument, Huge-32", 0.0, 3.0, ""),
    "creepy":      ("Transition Braam Slow Dark Creepy", 0.0, 3.0, ""),
    "drop":        ("Bass Drop & Downer Medium 04", 0.0, 2.0, ""),
    "magic":       ("Magic Light Spell Enchantment Potion Effect Tonal Bright", 0.0, 2.0, ""),
    "magic_big":   ("magic, energy flow, astonishment", 0.0, 3.0, ""),
    "shimmer":     ("Power Up Bright Positive Successful Light Saturation Crash Shimmer", 0.0, 2.0, ""),
    "bells_magic": ("Magic Christmas Bells 2", None, 2.5, ""),
    "ice_crack":   ("ice, surface cracking, fissure, fast, hard", None, 1.4, "камень: хруст"),
    "stone_hit":   ("Wooden Hit, Dark, Heavy Hit", None, 1.5, "камень: удар"),
    "sword":       ("Sword Slide Cuts, Metallic, Impact", None, 1.0, ""),
    "slash":       ("Action Deploy Units Sword Slice Special Move Layered Swish", 0.0, 1.0, ""),
    "stamp":       ("Hit Blood Spill Splat Wood Impact Light Hit Squelch Small Thump", None, 0.35, "штамп на титрах"),
    "lock":        ("Suitcase Being Locked, Antique Suitcase 1", None, 1.2, ""),
    "splash":      ("Impact Water Deep Submerge Bubble Drown Ship Hit", 0.0, 2.0, ""),
    "waves":       ("Medium Waves at Pebble Beach", 2.0, 10.0, "фон"),
    "waves_soft":  ("Soft Waves Cliffs", 2.0, 10.0, "фон"),
    "wind":        ("Wind, Rush, Whoosh, Long x5", None, 3.0, ""),
    "storm":       ("STORM_Texas Rain Thunder Initial Crash Boom Storm", 0.0, 6.0, "гром"),
    "thunder":     ("Interior Thunder Rumble", None, 4.0, ""),
    "fire":        ("Dropping Fresh Pine Branches in Fire", 3.0, 10.0, "фон"),
    "party":       ("Dinner Party Crowd in Terrace", 5.0, 10.0, "фон"),
    "crowd_cheer": ("Small Club, 50 People, Crowd, Spanish, Cheering and Applause", None, 4.0, ""),
    "crowd_stadium": ("SBvma_Masculine Regional Match 005", 5.0, 10.0, "фон"),
    "gasp":        ("Police Officer Gasp Vocal Male Shocked Alert 1", 0.0, 1.2, ""),
    "laugh":       ("Police Officer Laugh Vocal Male 1", 0.0, 2.5, ""),
    "laugh_f":     ("Laughing Female 02 06", None, 2.0, ""),
    "cry":         ("Crying Female 04 05", None, 2.5, ""),
    "yell":        ("Male Adventurer, Active Yell 19", 0.0, 1.5, ""),
    "scream":      ("Construction Kit Male Screeching Breath Inhale Weak Squeal", None, 1.5, ""),
    "whistle":     ("Whistle Male 06 09", None, 2.5, ""),
    "evil_laugh":  ("Announcer Vocal Male Wet Special Kill Laugh Monster Kill Hahaha", 0.0, 2.5, ""),
    "roar":        ("Large Herbivore Roar 01", None, 3.0, ""),
    "trex":        ("ANMLRept_T Rex", None, 3.0, ""),
    "growl":       ("Creature Werewolf Growl Menacing Monstrous", None, 2.0, ""),
    "gurgle":      ("Aquatic Creature Gurgling 2", None, 2.5, ""),
    "music_box":   ("SBmb_Music Box A 013", 0.0, 4.0, ""),
    "clock":       ("CLOCKTick_Crooked Antique Clock", None, 3.0, ""),
    "church_bells": ("Church Bells, Near Distance, In Church Tower", 1.0, 5.0, ""),
    "fanfare_bell": ("Impact Hit Rapid Chord Reverb", 0.0, 2.0, ""),
    "paper":       ("Woosh Sweep Slide Infographics Basic", None, 0.6, ""),
    "cloth":       ("Action Inventory Open Flip Cloth Canvas Bag Slide Light", 0.0, 0.8, ""),
    "horse":       ("LL-Q1860__eng_-Jjamesryan-neigh", 0.0, 2.5, ""),
    "baby":        ("Baby_5_months_old_gabbling_laughing", None, 2.5, ""),
    "snore":       ("Snoring_of_old_man", None, 3.0, ""),
    "crickets":    ("Ambience, Forest Crickets, Birds, Connecticut", None, 6.0, "фон: тишина"),
    "fireworks":   ("13 Fireworks_powerful explosions_multiples in a row_near", None, 3.0, ""),
}
SYNTH = {   # шипение — отфильтрованный шум с «дыханием», как настоящее
    "hiss": (2.5, "anoisesrc=c=white:a=0.8", "highpass=f=2800,lowpass=f=9000,"
             "volume='0.4+0.6*abs(sin(2*PI*1.3*t))':eval=frame,afade=t=in:d=0.15,afade=t=out:st=2.1:d=0.4"),
}


def files():
    return [p for p in LIB.rglob("*") if p.suffix.lower() in (".wav", ".ogg", ".flac", ".mp3")]


def find(part):
    hits = [p for p in files() if part.lower() in p.name.lower()]
    if not hits:
        raise SystemExit(f"нет файла с «{part}» в {LIB}")
    return sorted(hits, key=lambda p: len(p.name))[0]


def decode(p):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(p), "-ac", "2", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)


def loudest(a, dur):
    """Начало окна dur с наибольшей энергией (шаг 50 мс)."""
    n, step = int(dur * SR), int(0.05 * SR)
    if len(a) <= n:
        return 0.0
    e = np.convolve((a ** 2).mean(1), np.ones(step), "valid")[::step]
    k = max(1, n // step)
    sums = np.convolve(e, np.ones(k), "valid")
    return float(np.argmax(sums) * step / SR)


def momentary_max(p):
    """Максимум моментальной громкости (окно 400 мс). Звук короче окна дополняется тишиной — иначе ebur128
    его не меряет и возвращал −70 (так щелчок 0,33 с получал +104 дБ усиления)."""
    out = subprocess.run(["ffmpeg", "-nostdin", "-i", str(p), "-af", "apad=pad_dur=1,ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ms = [float(x) for x in re.findall(r" M:\s*(-?[\d.]+)", out)]
    return max(ms) if ms else -70.0


def peak_db(p):
    out = subprocess.run(["ffmpeg", "-nostdin", "-i", str(p), "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"max_volume:\s*(-?[\d.]+) dB", out)
    return float(m.group(1)) if m else -90.0


def build(name):
    tmp = OUT / f"_{name}.wav"
    dst = OUT / f"{name}.wav"
    if name in SYNTH:
        d, src, flt = SYNTH[name]
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "lavfi", "-i", f"{src}:r={SR}:d={d}",
                        "-af", flt, "-ac", "2", str(tmp)], check=True)
        origin = ("синтез ffmpeg (отфильтрованный шум)", "прав третьих лиц нет")
    else:
        part, start, dur, _ = SPEC[name]
        src = find(part)
        if start is None:
            start = max(0.0, loudest(decode(src), dur) - 0.05)
        fo = min(0.3, dur / 4)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", str(src),
                        "-af", f"aresample={SR},afade=t=in:d=0.01,afade=t=out:st={dur - fo:.2f}:d={fo:.2f}",
                        "-ac", "2", str(tmp)], check=True)
        rel = src.relative_to(LIB).as_posix()
        if rel.startswith("sonniss"):
            origin = (f"Sonniss GDC 2026: {src.parent.name} / {src.name} ({start:.1f}+{dur} с)",
                      "Sonniss GDC bundle license: коммерческое использование, без атрибуции")
        else:
            lic = {r.split("\t")[0]: r.split("\t")[1] for r in (LIB / "commons" / "SOURCES.tsv").read_text(encoding="utf-8").splitlines() if r}
            origin = (f"Wikimedia Commons: {src.name} ({start:.1f}+{dur} с)", lic.get(src.name, "?"))
    m = momentary_max(tmp)
    if m < -45 and name not in SYNTH and SPEC[name][1] is not None:     # кусок — почти тишина: берём самое громкое окно
        print(f"  {name}: в куске {SPEC[name][1]}+{SPEC[name][2]} с тишина ({m:.0f} LUFS), беру самое громкое окно")
        SPEC[name] = (SPEC[name][0], None) + SPEC[name][2:]
        tmp.unlink()
        return build(name)
    gain = TARGET - m
    if m <= -69:                       # громкость не измерилась — по пику до −3 dBFS
        gain = -3 - peak_db(tmp)
        print(f"  ! {name}: громкость не измерилась, выравниваю по пику")
    gain = min(gain, 30.0)
    if gain > 15:
        print(f"  ! {name}: запись тихая, усиление {gain:+.1f} dB — проверить шум")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(tmp), "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.89:level=false", str(dst)], check=True)
    tmp.unlink()
    print(f"{name:14s} {gain:+6.1f} dB  {origin[0][:90]}")
    return origin


def main():
    if "--list" in sys.argv:
        word = sys.argv[sys.argv.index("--list") + 1].lower()
        for p in files():
            if word in p.name.lower() or word in p.parent.name.lower():
                d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                   capture_output=True, text=True).stdout.strip()
                print(f"{float(d or 0):6.1f} с  {p.parent.name} / {p.name}")
        return
    names = [a for a in sys.argv[1:] if not a.startswith("-")] or list(SPEC) + list(SYNTH)
    credits_path = HERE / "credits.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}
    for n in names:
        if (OUT / f"{n}.wav").exists() and not sys.argv[1:]:
            continue
        credits[n] = build(n)
    credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    rows = ["# Звуки и музыка серии", "",
            "Собирает `sfx.py` из библиотеки канала (`channel/local/sfx/`, только локально) и `mix.py`.",
            "Все звуки выровнены по громкости (максимум моментальной −16 LUFS), пропорции — категории в `mix.py`.", "",
            "| Звук | Источник | Лицензия |", "|---|---|---|"]
    rows += [f"| `{n}` | {o} | {l} |" for n, (o, l) in sorted(credits.items())]
    music = json.loads((HERE / "music.json").read_text(encoding="utf-8")) if (HERE / "music.json").exists() else {}
    if music:
        rows += ["", "## Музыка (Kevin MacLeod, incompetech.com, CC BY 4.0)", "",
                 "Строки для описания ролика:", "", "```"]
        for t in sorted({m["title"] for m in music.get("tracks", {}).values()}):
            rows += [f'"{t}" Kevin MacLeod (incompetech.com)']
        rows += ["Licensed under Creative Commons: By Attribution 4.0 License",
                 "http://creativecommons.org/licenses/by/4.0/", "```"]
    (HERE / "CREDITS.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
