"""Сведение серии: голос + звуки по меткам + музыка по главам -> sound/mix.wav (−14 LUFS, пик −1 dBTP).

Стемы для мастеринга в SoundCraft (local/): stem_voice_raw.wav (голос к −16 LUFS, без обработки) и
stem_fx.wav (звуки + музыка, уже приглушённые под голос). Чистовой мастер делает SoundCraft
(см. README серии, «Мастеринг»); sound/mix.wav — запасной мастер ffmpeg и основа для check_masking().

python sound/mix.py

Голос — опора: его громкость не трогаем, остальное — ниже на заданное число дБ.
Звуки (sound/sfx/, все выровнены sfx.py к одной громкости) — по категориям GAIN; фоновые (BEDS)
звучат до конца своей склейки с затуханием. Музыка (storyboard.json "music", channel/local/music,
Kevin MacLeod CC BY 4.0) — каждый трек выровнен к −16 LUFS, под голосом на MUSIC_DB ниже, в паузах
голоса длиннее секунды и на карточках глав — громче (MUSIC_GAP_DB), между треками кроссфейд.
Мастер — двухпроходный loudnorm. ffmpeg — всегда с -nostdin (в фоновой оболочке иначе висит).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from gen_episode import resolve  # noqa: E402

EDL = json.loads((ROOT / "voice" / "edl.json").read_text(encoding="utf-8"))
SB = json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))
CUES = json.loads((HERE / "cues.json").read_text(encoding="utf-8"))
MUSIC_DIR = ROOT.parents[1] / "local" / "music"
LOCAL = ROOT / "local"
DUR = EDL["duration"]
SR = 48000
MUSIC_DB = -17          # музыка под голосом (голос ≈ −16 LUFS -> музыка ≈ −33)
MUSIC_GAP_DB = -9       # в паузах голоса и на карточках
DUCK_THRESHOLD = 0.03  # sidechain: с какой громкости голоса шина звуков начинает уходить вниз (≈ −30 dBFS)
XFADE = 1.5
GAIN = {   # дБ относительно выровненного звука; не названные — DEFAULT
    "title": -20, "pop": -16, "pops": -15, "whoosh": -12, "swoosh": -12, "whoosh_big": -10, "boing": -10,
    "transition": -13, "paper": -14, "cloth": -12, "bells_magic": -11, "shimmer": -10, "magic": -9, "magic_big": -9,
    "bonk": -5, "stone_hit": -9, "ice_crack": -11, "slash": -7, "sword": -8, "splash": -10, "drop": -13, "braam": -8,
    "creepy": -12, "impact": -7, "thunder": -7, "roar": -6, "trex": -6, "growl": -8, "gurgle": -9,
    "yell": -11, "scream": -11, "gasp": -9, "laugh": -9, "laugh_f": -9, "cry": -10, "evil_laugh": -10, "baby": -14,
    "horse": -8, "whistle": -10, "dizzy": -9, "fanfare_bell": -9, "lock": -9, "stamp": -12, "clock": -12, "hiss": -12,
}
BEDS = {"party": -20, "fire": -20, "waves": -21, "waves_soft": -21, "crowd_stadium": -20, "storm": -15,
        "crickets": -14, "wind": -16, "snore": -14, "music_box": -16, "church_bells": -15, "crowd_cheer": -14}
DEFAULT = -10
ALIAS = {"title": "pop"}


def ff(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)


def lufs(path):
    out = subprocess.run(["ffmpeg", "-nostdin", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def music_sections():
    secs = []
    for i, m in enumerate(SB.get("music", [])):        # [якорь, трек, поправка дБ (необязательно)]
        t = max(0.0, resolve(m[0], {"id": "music", "t0": 0.0, "t1": DUR, "line": 1}))
        secs.append([t, m[1], m[2] if len(m) > 2 else 0.0])
    out = []
    for i, (t, track, db) in enumerate(secs):
        end = secs[i + 1][0] if i + 1 < len(secs) else DUR
        out.append((t, end, track, db))
    return out


def voice_gaps():
    """Паузы голоса длиннее секунды — там музыка громче."""
    gaps, prev = [], 0.0
    for s in EDL["segments"]:
        if s["t"] - prev > 1.2:           # подъём музыки не задевает ни конец, ни начало фразы
            gaps.append((prev + 0.4, s["t"] - 0.4))
        prev = s["t"] + s["b"] - s["a"]
    gaps.append((prev + 0.15, DUR))
    return gaps


def build():
    inputs = ["-i", str(ROOT / "voice" / "voice.wav")]
    fmt = f"aresample={SR},aformat=sample_fmts=fltp:channel_layouts=stereo"
    # голос сначала приводим к −16 LUFS: громкость модели/записи не должна менять пропорции с музыкой
    voice_gain = -16.0 - lufs(ROOT / "voice" / "voice.wav")
    fx = [f"[0]{fmt},volume={voice_gain:.2f}dB,asplit[v_raw][v_in]",      # v_raw — сырой стем для SoundCraft
          "[v_in]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=10:release=150,volume=2dB[voice]"]
    labels = ["[voice]"]
    # музыка: каждый раздел — свой трек с начала, по кругу если короче, кроссфейд на стыках
    gaps = voice_gaps()
    up = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in gaps) or "0"
    k_lo, k_hi = 10 ** (MUSIC_DB / 20), 10 ** (MUSIC_GAP_DB / 20)
    for i, (a, b, track, db) in enumerate(music_sections()):
        f = MUSIC_DIR / f"{track}.mp3"
        inputs += ["-stream_loop", "-1", "-i", str(f)]
        n = len([x for x in inputs if x == "-i"]) - 1
        length = b - a + XFADE
        fx.append(f"[{n}]{fmt},atrim=0:{length:.2f},loudnorm=I=-16:TP=-2:LRA=11,{fmt},volume={db}dB,"
                  f"afade=t=in:d={0.05 if i == 0 else XFADE}:curve=qsin,afade=t=out:st={length - XFADE:.2f}:d={XFADE}:curve=qsin,"
                  f"adelay={int(a * 1000)}:all=1,"
                  f"volume='{k_lo:.4f}+({k_hi:.4f}-{k_lo:.4f})*min(1,{up})':eval=frame[m{i}]")
        labels.append(f"[m{i}]")
    # звуки: одинаковые в пределах 0,3 с не складываем (три одинаковых удара разом — +9,5 дБ)
    last = {}
    for i, c in enumerate(CUES):
        name, t = c[0], c[1]
        if not name or t - last.get(name, -9.0) < 0.3:
            continue
        last[name] = t
        src = HERE / "sfx" / f"{ALIAS.get(name, name)}.wav"
        if not src.exists():
            print("нет звука", name)
            continue
        inputs += ["-i", str(src)]
        n = len([x for x in inputs if x == "-i"]) - 1
        if name in BEDS:
            end = c[2] if len(c) > 2 and c[2] else t + 10
            d = max(0.5, end - t)
            chain = (f"[{n}]{fmt},atrim=0:{d:.2f},afade=t=in:d=0.4,afade=t=out:st={max(0, d - 0.6):.2f}:d=0.6,"
                     f"volume={BEDS[name]}dB")
        else:
            chain = f"[{n}]{fmt},volume={GAIN.get(name, DEFAULT)}dB"
        fx.append(f"{chain},adelay={max(0, int(t * 1000))}:all=1[s{i}]")
        labels.append(f"[s{i}]")
    # всё кроме голоса — отдельным стемом: по нему check_masking() ищет, где звуки перекрывают рассказчика
    rest = labels[1:]
    # шина звуков и музыки приглушается под голосом (sidechain): перекрыть рассказчика она не может,
    # а в паузах акценты звучат в полную силу
    fx += [f"{''.join(rest)}amix=inputs={len(rest)}:normalize=0:duration=longest,apad,atrim=0:{DUR}[fx_bus]",
           "[voice]asplit=3[v_mix][v_stem][v_key]",
           f"[fx_bus][v_key]sidechaincompress=threshold={DUCK_THRESHOLD}:ratio=4:attack=15:release=350:knee=4,"
           "asplit[fx_mix][fx_stem]",
           f"[v_mix][fx_mix]amix=inputs=2:normalize=0:duration=first,apad,atrim=0:{DUR}[out]"]
    script = LOCAL / "mix_filter.txt"
    script.write_text(";\n".join(fx), encoding="utf-8")
    raw = LOCAL / "mix_raw.wav"
    ff(*inputs, "-filter_complex_script", str(script), "-map", "[out]", "-ac", "2", "-t", str(DUR), str(raw),
       "-map", "[v_stem]", "-ac", "1", "-t", str(DUR), str(LOCAL / "stem_voice.wav"),
       "-map", "[fx_stem]", "-ac", "2", "-t", str(DUR), str(LOCAL / "stem_fx.wav"),
       "-map", "[v_raw]", "-ac", "1", "-c:a", "pcm_s24le", "-t", str(DUR), str(LOCAL / "stem_voice_raw.wav"))
    # мастер: два прохода loudnorm -> −14 LUFS, −1 dBTP
    meas = subprocess.run(["ffmpeg", "-nostdin", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]+\}", meas[meas.rfind("Parsed_loudnorm"):], re.S).group(0))
    ff("-i", str(raw), "-af", f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
       f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
       f"aresample={SR}", str(HERE / "mix.wav"))
    print(f"mix.wav {DUR:.1f} с, музыка {len(music_sections())} частей, звуков {len(labels) - 1 - len(music_sections())}")


def check_masking(margin=0.0):
    """Места, где звуки и музыка ближе margin дБ к голосу (окна 400 мс, пока голос звучит) — их надо тише."""
    import numpy as np

    def rms_db(path):
        raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-af", "highpass=f=150,highpass=f=150",
                              "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, dtype=np.float32)
        csum = np.concatenate([[0.0], np.cumsum(a.astype(np.float64) ** 2)])
        starts = np.arange(0, len(a) - 3200, 800)          # окно 400 мс, шаг 100 мс
        return 10 * np.log10((csum[starts + 3200] - csum[starts]) / 3200 + 1e-12)
    v, f = rms_db(LOCAL / "stem_voice.wav"), rms_db(LOCAL / "stem_fx.wav")
    n = min(len(v), len(f))
    # уровень фразы: максимум голоса за ±0,5 с (паузы между словами не считаются «тихим голосом»)
    v_now = v[:n]
    v = np.array([v[max(0, i - 5):i + 6].max() for i in range(n)])
    spans = []
    for i in range(n):
        if v_now[i] > -40 and v_now[i] > v[i] - 12 and f[i] > v[i] - margin:     # голос звучит прямо сейчас
            t = i / 10
            if spans and t - spans[-1][1] <= 0.3:
                spans[-1][1] = t
            else:
                spans.append([t, t])
    print(f"перекрытие голоса (звуки/музыка ближе {margin:.0f} дБ к голосу): {len(spans)} мест")
    for a, b in spans:
        hits = sorted({c[0] for c in CUES if c[0] and a - 1.0 <= c[1] <= b + 0.2})
        print(f"  {int(a // 60)}:{a % 60:05.2f}–{b % 60:05.2f}  {', '.join(hits) or 'музыка'}")
    return spans


def report():
    """Громкость по минутам: голос отдельно и весь микс — видно, не тонет ли голос и не пропала ли музыка."""
    def lufs_per(path, step=60):
        out = []
        for t in range(0, int(DUR), step):
            o = subprocess.run(["ffmpeg", "-nostdin", "-ss", str(t), "-t", str(step), "-i", str(path), "-af", "ebur128",
                                "-f", "null", "-"], capture_output=True, text=True).stderr
            v = re.findall(r"I:\s+(-?[\d.]+) LUFS", o)
            out.append(float(v[-1]) if v else None)
        return out
    mix = lufs_per(HERE / "mix.wav")
    total = subprocess.run(["ffmpeg", "-nostdin", "-i", str(HERE / "mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    print("мастер:", re.findall(r"I:\s+(-?[\d.]+) LUFS", total)[-1], "LUFS, пик",
          re.findall(r"Peak:\s+(-?[\d.]+) dBFS", total)[-1], "dBTP")
    print("по минутам (LUFS):", " ".join(f"{v:.1f}" if v is not None else "—" for v in mix))


if __name__ == "__main__":
    build()
    check_masking()
    report()
