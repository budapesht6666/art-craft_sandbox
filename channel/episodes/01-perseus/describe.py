"""Описание ролика для YouTube: главы с таймкодами (по карточкам раскадровки) + атрибуция музыки и звуков.

python describe.py  ->  out/description.md

Таймкоды берутся из local/ec/episode.json (после gen_episode.py), поэтому после новой записи голоса
описание пересобирается само. YouTube требует, чтобы первая глава начиналась с 0:00.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
EP = json.loads((HERE / "local" / "ec" / "episode.json").read_text(encoding="utf-8"))
SB = json.loads((HERE / "storyboard.json").read_text(encoding="utf-8"))
cards = {s["id"]: s["card"] for s in SB["shots"] if "card" in s}


def mmss(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


chapters = [("0:00", "Intro")]
for c in EP["comps"]:
    if c["name"] in cards:
        chapters.append((mmss(c["start"]), cards[c["name"]]["title"].title()))
tracks = sorted({m[1] for m in SB.get("music", [])})  # [метка, трек] или [метка, трек, сдвиг громкости]
titles = {p.stem: p.stem.replace("_", " ").title() for p in (HERE.parents[1] / "local" / "music").glob("*.mp3")}
lines = [f"# {SB['title']} — описание для YouTube", "",
         "Вставить в поле «Описание» как есть (главы YouTube строит по таймкодам сам).", "", "```",
         "His grandpa locked his mom in a tower. Zeus got in anyway. What followed: a head in a bag, "
         "a very quiet wedding and the worst discus throw in history. This is the entire story of Perseus.", "",
         "Chapters:"]
lines += [f"{t} {name}" for t, name in chapters]
lines += ["", "Music by Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0 License",
          "http://creativecommons.org/licenses/by/4.0/"]
lines += [f'"{titles.get(t, t)}"' for t in tracks]
lines += ["", "Sound effects: Sonniss GameAudioGDC bundle, Wikimedia Commons (CC0).", "",
          "#GreekMythology #Perseus #Medusa", "```", "",
          "Длительность ролика: " + mmss(EP["duration"])]
lines += ["", "## Остальные поля в YouTube Studio", "",
          "| Поле | Что ставить |", "|---|---|",
          "| Название | `The ENTIRE Story of Perseus` (запасное: `The ENTIRE Story of Perseus (Greek Mythology Explained)`) |",
          "| Обложка | `out/thumb/perseus_thumb.jpg` |",
          "| Плейлист | создать `Greek Mythology` |",
          "| Аудитория | «Нет, это видео не для детей» |",
          "| Теги | `perseus, medusa, greek mythology, perseus and medusa, andromeda, danae, zeus, "
          "greek myths explained, mythology animated, the entire story of perseus` |",
          "| Язык видео | английский |",
          "| Категория | Education |",
          "| Изменённый или синтетический контент | «Нет»: рисунок нереалистичный, голос — клон голоса автора |",
          "| Субтитры | загрузить `out/subs/perseus.<язык>.srt`, 6 языков |",
          "| Конечная заставка | последние 13 с, справа: «Подписаться» + плейлист `Greek Mythology` |",
          "| Публикация | «Запланировать»: 28.10, 02:00 (UTC+7) = 27.10, 15:00 ET |",
          "",
          "Хэштеги в конце описания: первые три YouTube показывает над названием.",
          "",
          "## Шортсы (`out/shorts/`)", "",
          "Выкладывать через 3–6 ч после длинного ролика или на следующий день, по одному. В поле «Похожее видео» "
          "указать длинный ролик.", "",
          "| Файл | Название |", "|---|---|",
          "| `perseus_short_1_graeae.mp4` | `Three Sisters. One Eye. Bad Idea. #greekmythology #perseus #shorts` |",
          "| `perseus_short_2_atlas.mp4` | `How Perseus Turned a Giant Into Mountains #greekmythology #atlas #shorts` |",
          "| `perseus_short_3_discus.mp4` | `The Worst Discus Throw in History #greekmythology #perseus #shorts` |"]
(HERE / "out" / "description.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
