"""Дорожка голоса серии: сегменты сценария -> voice/voice.wav и voice/edl.json (время каждого слова).

python voice.py tts      — черновой голос edge-tts (для аниматика до записи)
python voice.py eleven   — клон голоса пользователя в ElevenLabs (channel/voice/README.md), для публикации
python voice.py rec voice/rec.m4a — запись пользователя: время слов из transcribe.py (кэш voice/rec_words.json)
                                    -> последний удачный дубль каждого сегмента, ускоренный под тайминг
                                    черновика (local/edl_tts.json), ролик не растягивается

Сегмент — кусок реплики между (beat). Между сегментами пауза BEAT, между репликами GAP,
после реплики — ещё storyboard.json "pause_after" (под крик, камень и т.п.), перед репликой —
"pause_before" (карточка главы).
edl.json: {"duration", "segments": [{line, seg, src, a, b, t}], "words": [{line, w, t0, t1}]} —
время слов в секундах серии; по нему gen_episode.py ставит ключи, mix.py режет голос, subs.py пишет .srt.
"""
import asyncio
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
VOICE = HERE / "voice"
BEAT, GAP, LEAD = 0.7, 0.45, 0.6     # пауза на (beat), между репликами, тишина в начале
MAX_TEMPO = 1.3                      # rec: быстрее запись не ускоряем — дальше речь звучит неестественно
TTS_EDL = HERE / "local" / "edl_tts.json"   # тайминг чернового голоса — под него подгоняется запись
TTS_VOICE, TTS_RATE = "en-US-AndrewNeural", "+4%"
SR = 48000


def script_lines():
    """script.md -> {номер: [сегменты]}: реплики «**N.** текст», сегменты делятся по (beat)."""
    text = (HERE / "script.md").read_text(encoding="utf-8").split("## Текст", 1)[1]
    lines = {}
    for m in re.finditer(r"\*\*(\d+)\.\*\*\s+(.+?)(?=\n\s*\n|\Z)", text, re.S):
        body = " ".join(m.group(2).split())
        segs = [s.strip() for s in body.split("(beat)") if s.strip()]
        lines[int(m.group(1))] = segs
    return lines


def words_of(s):
    return [w for w in re.findall(r"[A-Za-z0-9']+", s.replace("ë", "e"))]


def norm(w):
    w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode()     # Danaë, fiancé
    return re.sub(r"[^a-z0-9]", "", w.lower())


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


async def tts_one(text, path):
    import edge_tts
    c = edge_tts.Communicate(text.replace("Danaë", "Danae"), TTS_VOICE, rate=TTS_RATE, boundary="WordBoundary")
    marks, audio = [], bytearray()
    async for ch in c.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            marks.append([ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7])
    path.write_bytes(bytes(audio))
    return marks


def tts_segments(lines):
    """Каждый сегмент — свой mp3 (кэш в voice/tts/), слова из WordBoundary."""
    out = HERE / "local" / "tts"            # синтетический голос пересобирается, в git не идёт
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "marks.json"
    marks = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    segs = []
    for n, parts in lines.items():
        for k, text in enumerate(parts):
            p = out / f"l{n:02d}_{k}.mp3"
            key = f"{n}_{k}"
            if not p.exists() or marks.get(key, {}).get("text") != text:
                for attempt in range(4):          # edge-tts иногда отвечает NoAudioReceived
                    try:
                        m = asyncio.run(tts_one(text, p))
                        break
                    except Exception as e:   # noqa: BLE001
                        print("  повтор", key, e)
                else:
                    sys.exit(f"edge-tts не ответил на {key}")
                marks[key] = {"text": text, "words": m}
            w = marks[key]["words"]
            segs.append({"line": n, "seg": k, "src": str(p), "a": 0.0, "b": dur(p),
                         "words": [[x, t0, t1] for x, t0, t1 in w]})
    cache.write_text(json.dumps(marks, ensure_ascii=False, indent=0), encoding="utf-8")
    return segs


ELEVEN_VOICE = "Pretty Much History narrator"     # клон голоса пользователя (channel/voice/README.md)
ELEVEN_MODEL = "eleven_v4"                        # выбрана пользователем 2026-10-27 (сравнение с multilingual_v2, v3)
ELEVEN_SPEED = 1.0   # темп клона (voice_settings.speed, ElevenLabs: 0.7–1.2). Серия 1 — 1.0 (клон на 27 % медленнее
                     # edge-tts, 11:44). Пользователь просит со следующей серии 1.1–1.2
ENV = Path(r"C:\projects\claude\remotion-skill\.env")


def eleven_key():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("нет ELEVENLABS_API_KEY")


def eleven_segments(lines):
    """Клон голоса ElevenLabs: каждый сегмент — with-timestamps (время символов -> время слов), кэш local/eleven/."""
    import base64
    import urllib.request
    k = eleven_key()
    voices = json.load(urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/voices",
                                                                     headers={"xi-api-key": k})))["voices"]
    vid = next((v["voice_id"] for v in voices if v["name"] == ELEVEN_VOICE), None)
    if not vid:
        sys.exit(f"нет голоса «{ELEVEN_VOICE}» в ElevenLabs (см. channel/voice/README.md)")
    out = HERE / "local" / "eleven"
    out.mkdir(parents=True, exist_ok=True)
    cache_p = out / "marks.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    flat = [(n, kk, t) for n, parts in lines.items() for kk, t in enumerate(parts)]
    segs = []
    for i, (n, kk, text) in enumerate(flat):
        key = f"{n}_{kk}"
        p = out / f"l{n:02d}_{kk}.mp3"
        if (cache.get(key, {}).get("text") != text or cache.get(key, {}).get("voice") != vid or not p.exists()
                or cache.get(key, {}).get("speed", 1.0) != ELEVEN_SPEED):
            body = {"text": text, "model_id": ELEVEN_MODEL, "voice_settings": {"speed": ELEVEN_SPEED},
                    "previous_text": flat[i - 1][2] if i else None, "next_text": flat[i + 1][2] if i + 1 < len(flat) else None}
            req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps",
                                         data=json.dumps(body).encode(), headers={"xi-api-key": k, "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=180))
            p.write_bytes(base64.b64decode(r["audio_base64"]))
            al = r["alignment"]
            words, cur, t0 = [], "", None
            for ch, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
                if ch.isspace():
                    if cur:
                        words.append([cur, t0, prev_b])
                    cur, t0 = "", None
                    continue
                if t0 is None:
                    t0 = a
                cur += ch
                prev_b = b
            if cur:
                words.append([cur, t0, prev_b])
            cache[key] = {"text": text, "voice": vid, "speed": ELEVEN_SPEED, "words": words}
            cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
            print("  ", key, len(text), "знаков")
        segs.append({"line": n, "seg": kk, "src": str(p), "a": 0.0, "b": dur(p),
                     "words": [[w, a, b] for w, a, b in cache[key]["words"]]})
    return segs


def rec_segments(lines, src):
    """Запись пользователя: для каждого сегмента — последний дубль, где совпали ≥ 80 % слов.

    Время слов — transcribe.py (скилл history-episode) с подсказкой имён, кэш voice/rec_words.json.
    """
    cache = VOICE / "rec_words.json"
    if not cache.exists():
        prompt = ("Greek mythology. Perseus, King Acrisius, Danae, Zeus, Polydectes, Medusa, Athena, Hermes, "
                  "nymphs, Andromeda, oracle, discus.")
        subprocess.run([sys.executable, str(HERE / "transcribe.py"), str(src), str(cache), "--model", "medium.en",
                        "--prompt", prompt], check=True)
    W = [[w["w"], w["s"], w["e"]] for seg in json.loads(cache.read_text(encoding="utf-8")) for w in seg["words"]]
    src = str(src)
    toks = [norm(w[0]) for w in W]
    segs = []
    for n, parts in lines.items():
        for k, text in enumerate(parts):
            want = [norm(w) for w in words_of(text)]
            best = None
            for i in range(len(toks)):
                if toks[i] != want[0] and (i + 1 >= len(toks) or toks[i + 1] != (want[1] if len(want) > 1 else "")):
                    continue
                # жадное совпадение с допуском пропусков
                j, hit, last = i, 0, i
                for w in want:
                    for d in range(3):
                        if j + d < len(toks) and toks[j + d] == w:
                            hit, last, j = hit + 1, j + d, j + d + 1
                            break
                if hit >= 0.8 * len(want):
                    best = (i, last)                  # последний удачный дубль
            if not best:
                print(f"  ! реплика {n}.{k} не найдена в записи: {text}")
                continue
            i, j = best
            a, b = max(0.0, W[i][1] - 0.05), W[j][2] + 0.12
            segs.append({"line": n, "seg": k, "src": src, "a": a, "b": b,
                         "words": [[w[0], w[1] - a, w[2] - a] for w in W[i:j + 1]]})
    fit_to_tts(segs)
    return segs


def fit_to_tts(segs):
    """Ролик не растягиваем под запись: каждую фразу ускоряем до длины той же фразы чернового голоса
    (rubberband: темп меняется, высота и тембр — нет). Медленнее не делаем, быстрее MAX_TEMPO — тоже."""
    if not TTS_EDL.exists():
        print("  нет local/edl_tts.json — запись идёт в своём темпе")
        return
    tgt = {f"{x['line']}.{x['seg']}": x["b"] - x["a"] for x in json.loads(TTS_EDL.read_text(encoding="utf-8"))["segments"]}
    over, tempos = 0.0, []
    for s in segs:
        want = tgt.get(f"{s['line']}.{s['seg']}")
        if not want:
            continue
        need = (s["b"] - s["a"]) / want
        s["tempo"] = round(min(max(need, 1.0), MAX_TEMPO), 3)
        tempos.append(s["tempo"])
        over += (s["b"] - s["a"]) / s["tempo"] - want if need > MAX_TEMPO else 0
    if tempos:
        sped = [x for x in tempos if x > 1.01]
        print(f"  подгонка: ускорено {len(sped)} из {len(tempos)} фраз, в среднем ×{sum(sped) / max(1, len(sped)):.2f}, "
              f"на пределе ×{MAX_TEMPO}: {sum(1 for x in tempos if x >= MAX_TEMPO)}; ролик длиннее на {over:.1f} с")


def assemble(segs):
    sb = json.loads((HERE / "storyboard.json").read_text(encoding="utf-8"))
    pause_after = {int(k): v for k, v in sb.get("pause_after", {}).items()}
    pause_before = {int(k): v for k, v in sb.get("pause_before", {}).items()}
    t, words, out = LEAD, [], []
    for i, s in enumerate(segs):
        if i == 0 or segs[i - 1]["line"] != s["line"]:
            t += pause_before.get(s["line"], 0)
        s["t"] = round(t, 3)
        k = s.get("tempo", 1.0)
        for w, t0, t1 in s.pop("words"):
            words.append({"line": s["line"], "w": w, "t0": round(t + t0 / k, 3), "t1": round(t + t1 / k, 3)})
        t += (s["b"] - s["a"]) / k
        nxt = segs[i + 1] if i + 1 < len(segs) else None
        if nxt and nxt["line"] == s["line"]:
            t += BEAT
        else:
            t += GAP + pause_after.get(s["line"], 0)
        out.append(s)
    total = round(t + 1.5, 3)
    edl = {"duration": total, "segments": out, "words": words}
    (VOICE / "edl.json").write_text(json.dumps(edl, ensure_ascii=False, indent=1), encoding="utf-8")
    # склейка: каждый сегмент — atrim + adelay, всё в amix
    inputs, fx, labels = [], [], []
    fmt = f"aresample={SR},aformat=sample_fmts=fltp:channel_layouts=mono"
    for i, s in enumerate(out):
        inputs += ["-i", s["src"]]
        tempo = f"rubberband=tempo={s['tempo']}:pitchq=quality," if s.get("tempo", 1.0) > 1.001 else ""
        fx.append(f"[{i}]atrim={s['a']}:{s['b']},asetpts=PTS-STARTPTS,{fmt},{tempo}adelay={int(s['t'] * 1000)}:all=1[s{i}]")
        labels.append(f"[s{i}]")
    fx.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{total}[out]")
    script = HERE / "local" / "voice_filter.txt"
    script.write_text(";\n".join(fx), encoding="utf-8")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex_script", str(script),
                    "-map", "[out]", str(VOICE / "voice.wav")], check=True)
    print(f"voice.wav {total:.1f} с, сегментов {len(out)}, слов {len(words)}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "tts"
    L = script_lines()
    if mode == "tts":
        segs = tts_segments(L)
    elif mode == "eleven":      # клон голоса; ролик подгоняется под голос, как с черновиком
        segs = eleven_segments(L)
    else:
        segs = rec_segments(L, Path(sys.argv[2]))
    assemble(segs)
    if mode == "tts":           # тайминг черновика — эталон для подгонки записи
        TTS_EDL.write_text((VOICE / "edl.json").read_text(encoding="utf-8"), encoding="utf-8")
