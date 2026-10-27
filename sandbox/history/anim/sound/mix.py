"""Голос (дубль 2) + звуки -> sound/mix.wav под шот. python mix.py

Монтаж голоса: дубль 2 с 24,35 с, после «Don't look,» вставлена пауза PAUSE под крик и
камень. Времена звуков — в секундах шота (те же, что в gen_shot.py). Громкость −16 LUFS.
Ловушка: ffmpeg, запущенный из Python в фоновой оболочке, без -nostdin ждёт ввода и висит
вечно (простые вызовы из bash при этом работают). Голос подан двумя входами, ветер — тремя:
так проще, чем asplit и -stream_loop.
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
VOICE = HERE.parent / "voice" / "audio_2026-10-27_14-20-27.ogg"
T0, CUT, END = 24.35, 38.50, 42.75      # дубль 2: начало, точка вставки паузы, конец
PAUSE = 1.4
DUR = 20.8
SFX = [  # файл, время в шоте, громкость dB
    ("title.mp3", 12.93, -6),
    ("scream.mp3", 13.75, -5),
    ("flash.mp3", 14.38, -4),
    ("stone.mp3", 14.45, 0),
]
SR = 48000

inputs = ["-i", str(VOICE)] * 2 + ["-i", str(HERE / "wind.mp3")] * 3
for f, _, _ in SFX:
    inputs += ["-i", str(HERE / f)]
fmt = f"aresample={SR},aformat=sample_fmts=fltp:channel_layouts=mono"
fx = [
    f"[0]atrim={T0}:{CUT},asetpts=PTS-STARTPTS,{fmt}[v1]",
    f"anullsrc=r={SR}:cl=mono,atrim=0:{PAUSE},{fmt}[gap]",
    f"[1]atrim={CUT}:{END},asetpts=PTS-STARTPTS,{fmt}[v2]",
    "[v1][gap][v2]concat=n=3:v=0:a=1,highpass=f=80,"
    "acompressor=threshold=-20dB:ratio=3:attack=10:release=150,volume=2dB[voice]",
    f"[2][3][4]concat=n=3:v=0:a=1,{fmt},atrim=0:{DUR},volume=6dB,"
    f"afade=t=in:d=1,afade=t=out:st={DUR - 1.5}:d=1.5[amb]",
]
labels = ["[voice]", "[amb]"]
for i, (f, t, db) in enumerate(SFX):
    fx.append(f"[{i + 5}]{fmt},volume={db}dB,adelay={int(t * 1000)}:all=1[s{i}]")
    labels.append(f"[s{i}]")
fx.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,apad,atrim=0:{DUR},"
          f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample={SR}[out]")
cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fx), "-map", "[out]",
       "-ac", "2", "-t", str(DUR), str(HERE / "mix.wav")]
subprocess.run(cmd, check=True)
print("mix.wav", DUR, "с")
