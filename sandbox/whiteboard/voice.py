"""Озвучка сцены через edge-tts и тайминг элементов по словам.

Запуск: python sandbox/whiteboard/voice.py
Результат: voice.mp3, voice.srt и timing.json ({элемент: секунда начала}) рядом со скриптом.
Метка {имя} в тексте значит: элемент начинает рисоваться на следующем слове.
"""
import asyncio
import json
import re
from pathlib import Path

import edge_tts

HERE = Path(__file__).parent
VOICE = "ru-RU-DmitryNeural"
RATE = "+8%"
LEAD = 0.6  # тишина до первого слова, за неё успевает написаться заголовок

SCRIPT = (
    "{turtle}Почти все, с кем я разговаривал, {arrow}изначально думали, что для того, "
    "{text}чтобы заработать на криптовалюте, им придётся покупать и продавать её. "
    "{box}Ну, вы знаете: {buy}покупай дёшево, {wait}жди, пока Илон Маск напишет об этой "
    "монете в Твиттере, {sell}и затем продавай с хорошей прибылью. "
    "{warning}Честно говоря, это немного печально, потому что большинство людей "
    "{x_mark}теряют деньги при таком подходе. "
    "Печально ещё и потому, {say1}что есть гораздо {say2}лучший путь. "
    "{galaxy}Но в нём нужно немного разобраться."
)


def words(text):
    return re.findall(r"[\w-]+", text.lower().replace("ё", "е"))


async def main():
    cues, plain = [], []
    for part in re.split(r"(\{\w+\})", SCRIPT):
        m = re.fullmatch(r"\{(\w+)\}", part)
        if m:
            cues.append((m.group(1), len(words("".join(plain)))))
        else:
            plain.append(part)
    text = "".join(plain)

    # Сервис edge-tts время от времени отвечает NoAudioReceived на тот же самый запрос.
    for attempt in range(1, 9):
        try:
            audio, sub, starts = bytearray(), edge_tts.SubMaker(), []
            comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
                elif chunk["type"] == "WordBoundary":
                    sub.feed(chunk)
                    # offset и duration в тиках по 100 нс
                    for _ in words(chunk["text"]):
                        starts.append(chunk["offset"] / 1e7)
            break
        except edge_tts.exceptions.NoAudioReceived:
            print(f"попытка {attempt}: нет звука, повторяю")
            await asyncio.sleep(2 * attempt)
    else:
        raise SystemExit("edge-tts так и не ответил")
    (HERE / "voice.mp3").write_bytes(audio)
    (HERE / "voice.srt").write_text(sub.get_srt(), encoding="utf-8")

    n = len(words(text))
    if len(starts) != n:
        print(f"слов в тексте {n}, в озвучке {len(starts)} — тайминг может съехать")
    timing = {name: round(LEAD + starts[min(i, len(starts) - 1)], 2) for name, i in cues}
    timing["_end"] = round(LEAD + starts[-1] + 1.0, 2)
    timing["_lead"] = LEAD
    (HERE / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(timing, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
