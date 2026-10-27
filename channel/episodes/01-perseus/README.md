# Серия 1. «The ENTIRE Story of Perseus»

- **Дата:** 2026-10-27
- **Программы:** Gemini API (`gemini-nano-banana-2.1`), EffectCraft 0.17.0, VectorCraft 0.17.0 (карты),
  edge-tts (черновой голос), ffmpeg; звук — Sonniss GDC 2026 и Wikimedia Commons (CC0), музыка — Kevin MacLeod
- **Статус:** аниматик v2 на черновом голосе (≈ 9,5 мин); ждём запись голоса пользователя
- **История:** v1 — пилот на 2:30 (`local/*_v1_pilot*`); пользователь забраковал: коротко, звук разной
  громкости и плохого качества, нет музыки, субтитры только на английском. v2 исправляет всё это.

## Что где

| Путь | Что это |
|---|---|
| `script.md` | Текст для записи: 67 реплик в 9 главах, ~1350 слов, произношение имён |
| `storyboard_src.py` → `storyboard.json` | Раскадровка: 156 склеек, карточки глав, музыка по главам. Править — `storyboard_src.py` |
| `art/` | Генератор `gen.py`, библия и задания (`prompts/`), листы (`sheets/`), нарезка (`cut/`), карты (`map.py`, `map_world.py`, `map/`) |
| `voice.py` | Голос сегментами: `tts` — черновик, `rec <файл>` — запись пользователя → `voice/edl.json` |
| `gen_episode.py`, `build_episode.js`, `render.py` | Ключи → композиции EffectCraft → рендер склеек и склейка |
| `sound/sfx.py`, `sound/mix.py` | Звуки из библиотеки канала с выравниванием громкости; сведение с музыкой, −14 LUFS |
| `sound/CREDITS.md` | Источник и лицензия каждого звука и трека; строки атрибуции музыки для описания |
| `subs.py`, `subs/*.json` | Субтитры: английский из сценария, 5 переводов по сегментам (es, pt, de, fr, hi) |
| `out/video/perseus.mp4` | Готовый ролик (в git не идёт) |
| `out/subs/perseus.<язык>.srt` | Субтитры для YouTube Studio, 6 языков |
| `local/` | Только локально: проект EffectCraft, рендеры склеек, превью, черновой голос, пилот v1 |

Библиотека канала (общая для серий, только локально): `channel/local/sfx/` (Sonniss — перераспространять
нельзя), `channel/local/music/` (Kevin MacLeod).

## Пересобрать

```
python storyboard_src.py
python voice.py tts                       # или: python voice.py rec voice/<запись>.m4a
python gen_episode.py
# EffectCraft MCP: open_project {new} → save_project local/ec/episode.ecproj →
#   run_script local/ec/build_episode.js → save_project
python render.py sheet                    # лист проверки: кадр на склейку
python render.py shots
python sound/sfx.py && python sound/mix.py
python subs.py
python render.py join                     # -> out/video/perseus.mp4 и local/perseus_preview.mp4
```

## Финальная сборка в Craft-программах (v4, 2026-10-27)

Голос — клон голоса пользователя (ElevenLabs, `eleven_v4`, `voice.py eleven`), серия 11:44; распознавание
`medium.en` подтвердило текст без пропусков. Этапы:

| Этап | Программа | Файл |
|---|---|---|
| Анимация, рендер 157 склеек | EffectCraft 0.17 | `local/ec/episode.ecproj` |
| Карты | VectorCraft 0.17 | `art/map/*.svg` |
| Мастеринг: голос (EQ 7, де-эссер, компрессор 3:1) + звуки/музыка, мастер (компрессор 2:1, максимайзер) | SoundCraft | `local/soundcraft/perseus_master.scsession` → `master.wav`: −14,3 LUFS, TP −1,2 dBTP |
| Монтаж: 157 склеек встык + мастер, экспорт H.264 CRF 18 | FilmCraft | `local/filmcraft/perseus.fcproj` → `out/video/perseus.mp4` |
| Обложка 1280×720 | PhotoCraft | `local/thumb/perseus_thumb.pcraft` → `out/thumb/perseus_thumb.jpg` |

Скриптами остались: генерация картинок (Gemini API), нарезка, расчёт ключей, подготовка и выравнивание
звуков (57 файлов), черновое сведение со стемами, субтитры, описание.

## Оформление канала (v3, 2026-10-27)

- Титры и карточки — шрифтом канала Luckiest Guy (`channel/brand/fonts/`): `gen_episode.py` рисует их
  картинками через Pillow (обводка, тень, фигурные кавычки, длинные — в две строки), шрифт в систему не ставится.
- Ведущий Barnaby the Bard: заставка «Pretty Much History presents», «Subscribe», конечная заставка
  на 13 с (правая половина свободна под элементы YouTube «следующее видео» и «подписаться»).
- Логотип в кадр не вшит: в Studio есть кликабельный водяной знак канала (`channel/brand/out/watermark.png`).
- Голос: `voice.py tts` (черновик, только для аниматика — у edge-tts нет коммерческой лицензии),
  `voice.py eleven` (клон голоса пользователя, `channel/voice/README.md`), `voice.py rec <файл>`
  (живая запись, ускоряется под тайминг черновика до ×1,3, ролик не растягивается).

## Звук (v2)

- Звуки — реальные записи: Sonniss GDC 2026 (коммерческое использование и монетизируемый YouTube
  разрешены, атрибуция не нужна; нельзя перепродавать звуки и учить на них ИИ) и Wikimedia Commons
  (только CC0 / public domain). Синтез — только шипение змей (это и в жизни шум).
- Каждый звук выровнен к одной громкости (максимум моментальной −16 LUFS), тихий кусок записи
  определяется автоматически, усиление > 15 дБ выводится предупреждением.
- В миксе — категории: удары −5…−8 дБ, реакции −8…−10, «вжухи» −12, фоны −14…−21 и обрываются со склейкой.
- Музыка: 14 частей (свой трек на главу), каждая выровнена к −16 LUFS, под голосом −17 дБ (разрыв ~19 дБ,
  норма 18–24), в паузах и на карточках −9 дБ, кроссфейды 1,5 с.
- Мастер — двухпроходный loudnorm: −14,1 LUFS, пик −1,0 dBTP; по минутам −13,7…−15,1.

## Ловушки (v2)

- Якорь «The»/«He» часто встречается в реплике раньше нужного места: склейки встают не по порядку.
  Теперь `gen_episode.py` проверяет порядок и называет склейку.
- `fiancé`, `Danaë`: слова сравниваются после Unicode-нормализации (NFKD → ASCII).
- Нарезка листов: сетка цепляет куски соседей (сандалии верхнего ряда), связные области склеивают
  широкие фигуры. Помогает `slice_sheet.py --rows 2 --cols 4` (резы по пустым линиям) + очистка краёв.
- Gemini «уводит» новый каст в реалистичные лица; правка с приложенным эталоном стиля (`edit` + `refs`)
  чинит часть, остаток — правкой «как на рисунке N этого листа».
- Прямые ссылки Sonniss закрыты Cloudflare (curl получает HTML 5 КБ); зеркало Google Drive отдаётся
  `drive.usercontent.google.com/download?id=…&export=download&confirm=t`.
- Крик Вильгельма на Commons помечен CC0, но это запись Warner Bros 1951 г.: для монетизации не брать.
- Папку серии, открытую в EffectCraft/VectorCraft MCP, Windows не даёт переименовать целиком
  («Device or resource busy») — переносить содержимое по частям.
