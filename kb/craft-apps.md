# Craft-программы

13 отдельных программ, каждая повторяет известный профессиональный продукт. Написаны с
нуля на Rust, лицензия Apache-2.0 (у некоторых MIT или Apache-2.0).

Общее для всех программ:

- Windows, macOS, Linux, FreeBSD и браузер (WebAssembly).
- Бесплатно, без аккаунта и подписки.
- Каждое действие — команда из общего списка (400–650+ команд). Её можно вызвать из
  интерфейса, через CLI, через JSON-канал управления или через **MCP**. Значит, агент
  может делать всё, что делает человек. Подробнее в [mcp.md](mcp.md).
- **Альфа.** Работает, но заменой оригиналу для ежедневной работы пока не стала. У
  каждого репозитория есть `ROADMAP.md` и `docs/gaps.md` со списком того, чего не хватает.

Версии ниже — на 2026-10-25.

## Видео, фото, эффекты, графика

| Программа | Аналог | Версия | Для чего | Пример |
|---|---|---|---|---|
| [EffectCraft](https://github.com/storytold/effectcraft) | After Effects | 0.17.0 | Моушн-графика и композитинг: слои, ключевые кадры, маски, эффекты (Warp, Turbulent Displace, Fractal Noise, цветокоррекция), puppet-пины, выражения на JS (`wiggle`, `loopOut`), трекинг. Импорт и экспорт **Lottie**. Видео с прозрачностью: ProRes 4444, WebM VP9. Проект хранится в JSON (`.ecproj`). Кодеки свои, без FFmpeg | Анимированная заставка, плашка «подпишись», экспорт в Lottie для сайта или Remotion |
| [FilmCraft](https://github.com/storytold/filmcraft) | Premiere / Final Cut | 0.13.0 | Нелинейный монтаж, цвет (Lumetri), звук. Свои кодеки H.264, HEVC, ProRes, AAC. Обмен проектами через FCP 7 XML. Больше 650 команд | Ролик из нескольких клипов с цветокоррекцией и сведением звука |
| [PhotoCraft](https://github.com/storytold/photocraft) | Photoshop | 0.15.1 | Слои, маски, корректирующие слои, текст, фигуры, лечащая кисть, штамп, Content-Aware. Открывает и сохраняет настоящие PSD. Больше 500 команд. Генеративных ИИ-функций пока нет | Ретушь, коллаж, открыть чужой PSD |
| [LightCraft](https://github.com/storytold/lightcraft) | Lightroom | 0.14.0 | Каталог, проявка RAW, недеструктивная правка, локальные маски, пресеты, лица. ИИ-маски через SAM 3 и ИИ-шумодав — необязательные, модели ставятся отдельно | Обработать съёмку одним пресетом, затемнить небо маской |
| [VectorCraft](https://github.com/storytold/vectorcraft) | Illustrator | 0.17.0 | Векторная графика. SVG, PDF, `.ai`, EPS, DXF, EMF. Готовность около 65% | Логотип, иконки, постер |
| [DesignCraft](https://github.com/storytold/designcraft) | InDesign | 0.13.0 | Вёрстка страниц и макетов. Файлы InDesign читает [indd-utils](https://github.com/storytold/indd-utils) | Буклет, журнал, меню |
| [FigCraft](https://github.com/storytold/figcraft) | Figma | 0.10.0 | Дизайн интерфейсов, компоненты, прототипы, генерация React-кода | Макет приложения с кликабельным прототипом |
| [AniCraft](https://github.com/storytold/AniCraft) | 2D-анимация | — | Пока только заготовка: пустой README, релизов нет | — |

## Остальные

| Программа | Аналог | Пример |
|---|---|---|
| [SoundCraft](https://github.com/storytold/soundcraft) | Pro Tools | Запись и сведение звука |
| [CADCraft](https://github.com/storytold/cadcraft) | AutoCAD | Чертёж DWG/DXF |
| [PdfCraft](https://github.com/storytold/pdfcraft) | Acrobat | Читать, править, подписывать PDF |
| [WordCraft](https://github.com/storytold/wordcraft) | Word | Документы .docx |
| [GridCraft](https://github.com/storytold/gridcraft) | Excel | Таблицы и формулы |
| [DeckCraft](https://github.com/storytold/deckcraft) | PowerPoint | Презентации |

## ИИ в Craft-программах

Облачной генерации за деньги **нет**. Всё, что есть, необязательное и работает на
своём компьютере:

- LightCraft: выделение объектов (SAM 3), ИИ-шумодав. Веса ставятся отдельно.
- FilmCraft: распознавание речи, по умолчанию выключено.
- PhotoCraft: генеративных функций пока нет, авторы называют это главным пробелом.

Общий модуль [craft-ai-integrations](https://github.com/storytold/craft-ai-integrations)
(черновик) — одно ИИ-подключение на все программы. Можно подставить свой ключ
OpenAI-совместимого API, FLUX (Black Forest Labs), Gemini (Vertex), Seedance (BytePlus),
API-ключ ArtCraft или локальный ComfyUI и SAM. Платить придётся, только если сами
подключите платный сервис.

## Установка: ArtCraft Launcher

[storytold/craft-launcher](https://github.com/storytold/craft-launcher). Одно окно, из
которого ставятся и обновляются все 13 программ. Лаунчер сам выбирает сборку под ОС и
процессор и сверяет SHA-256. Интерфейс есть на русском.

- Windows x64: [artcraft-launcher-0.7.0-windows-x64.msi](https://github.com/storytold/craft-launcher/releases/download/v0.7.0/artcraft-launcher-0.7.0-windows-x64.msi)
  (или portable.zip). Свежие версии: [releases/latest](https://github.com/storytold/craft-launcher/releases/latest).
- Каждую программу можно скачать и отдельно, с её страницы релизов (`.msi` или portable.zip).
- Сам ArtCraft лаунчер не ставит, его качают с getartcraft.com.
