"""Упорядочивает штрихи в SVG из VectorCraft для рисования пером (Trim Paths по очереди).

Запуск: python sandbox/whiteboard/sort_strokes.py
Читает assets/trace/<имя>.svg, пишет assets/trace/<имя>_sorted.svg.
Составной путь режется на отдельные подпути. Надписи и линии рисуются слева направо,
рисунки — сверху вниз (полосами по 40 px, внутри полосы слева направо). В файле порядок
обратный: Trim Paths в режиме Individually начинает с последнего пути.
"""
import re
from pathlib import Path

TRACE = Path(__file__).parent / "assets" / "trace"
PICTURES = {"turtle", "crowd", "buy_icon", "wait_icon", "sell_icon", "galaxy", "warning"}
PATH_RE = re.compile(r"<path\b([^>]*?)\bd=\"([^\"]+)\"([^>]*)/>")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def subpaths(d):
    if re.search(r"[a-z]", d.replace("e-", "").replace("e+", "")):
        return [d]  # относительные команды не режем
    parts = [p.strip() for p in re.split(r"(?=M)", d) if p.strip()]
    return parts or [d]


def bbox(d):
    nums = [float(n) for n in NUM_RE.findall(d)]
    xs, ys = nums[0::2], nums[1::2]
    return min(xs), min(ys)


for svg in sorted(TRACE.glob("*.svg")):
    if svg.stem.endswith("_sorted"):
        continue
    text = svg.read_text(encoding="utf-8")
    items = []
    for before, d, after in PATH_RE.findall(text):
        for sub in subpaths(d):
            items.append((bbox(sub), f"<path{before}d=\"{sub}\"{after}/>"))
    if svg.stem in PICTURES:
        items.sort(key=lambda it: (int(it[0][1] // 40), it[0][0]))
    else:
        items.sort(key=lambda it: it[0][0])
    # Trim Paths (Individually) в EffectCraft 0.17.0 рисует с последнего пути в SVG
    items.reverse()
    head = text[: text.index("<g")]
    out = head + "<g>\n" + "\n".join(p for _, p in items) + "\n</g>\n</svg>\n"
    (TRACE / f"{svg.stem}_sorted.svg").write_text(out, encoding="utf-8")
    print(f"{svg.stem}: {len(items)} штрихов")
