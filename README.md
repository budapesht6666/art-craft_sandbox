# ArtCraft и Craft-программы: база знаний

Что мы выяснили про команду **storytold / ArtCraft** и её программы: что это, что
бесплатно, за что берут деньги, как подключить к Claude Code через MCP и чем это может
помочь проекту `remotion-skill`.

Данные собраны **2026-10-25** с getartcraft.com, GitHub API и README репозиториев.
Программы обновляются почти каждый день, поэтому версии и проценты готовности быстро
устаревают. Перед важным решением сверяйтесь с README нужного репозитория.

## Коротко

- **ArtCraft** — студия ИИ-картинок и видео. Код открыт, программа бесплатна, но
  генерация идёт через облако за кредиты (от $8 в месяц). Скачивается с
  [getartcraft.com/download](https://getartcraft.com/download).
- **Craft-программы** — 13 отдельных бесплатных программ на Rust, аналоги Photoshop,
  After Effects, Premiere, Illustrator и других. Без подписки, без облака, ИИ-функции
  необязательные и локальные. Все в **альфе**.
- **MCP** встроен в каждую Craft-программу (`<app>-cli.exe mcp`). У ArtCraft
  официального MCP нет.
- **Ставить** Craft-программы удобно через [ArtCraft Launcher](https://github.com/storytold/craft-launcher/releases/latest).
  Он уже установлен, сами программы пока нет.

## Разделы

| Файл | О чём |
|---|---|
| [kb/artcraft.md](kb/artcraft.md) | Студия ArtCraft: возможности, модели, тарифы, ArtCraft-X, неофициальный MCP |
| [kb/craft-apps.md](kb/craft-apps.md) | 13 Craft-программ: для чего, примеры, ИИ-функции, лаунчер |
| [kb/mcp.md](kb/mcp.md) | Как подключить Craft-программы к Claude Code: команды, режимы, порты |
| [kb/repos.md](kb/repos.md) | Все 68 репозиториев организации по группам |
| [kb/remotion-integration.md](kb/remotion-integration.md) | Чем Craft-программы могут помочь `remotion-skill` |
| [kb/sources.md](kb/sources.md) | Ссылки |

## Что сделано и что дальше

- [x] Собрана база знаний.
- [x] Установлен ArtCraft Launcher (Windows).
- [x] Установлен EffectCraft 0.17.0, CLI лежит в `C:\Program Files\EffectCraft\effectcraft-cli.exe`.
- [x] MCP `effectcraft` (без окна) и `effectcraft-app` (живое окно) подключены на уровне
      пользователя. Проверено: 27 инструментов, сцена через `run_script`, экспорт Lottie,
      сохранение `.ecproj`, рендер кадра с кириллицей.
- [x] Скилл `craft-apps` в `C:\projects\claude\shared-claude-skills\skills\craft-apps\`
      работает во всех проектах. Там же скрипты `setup-mcp.ps1` и `start-live.ps1`.
- [x] `effectcraft-app` проверен на живом окне (запуск через `start-live.ps1`): видит
      проект, двигает ползунок времени, делает скриншоты. Рендер идёт на GPU (AMD Radeon, Vulkan).
- [x] Тестовая плашка лежит в [sandbox/](sandbox/): `plate.ecproj` (проект), `plate.json`
      (Lottie), `frame.png` (кадр на 1 с).
- [x] Скрипт проверки состояния `status.ps1 -Online` (в скилле): что установлено, что
      устарело, что подключено к MCP. На 2026-10-25 стоят только EffectCraft 0.17.0 и
      лаунчер 0.8.1.
- [x] Установлен FilmCraft 0.13.0. MCP `filmcraft` проверен: демо-проект открывается,
      кадр рендерится.
- [x] Автообновление в лаунчере включено. Хук `SessionStart` запускает `setup-mcp.ps1 -Quiet`.
- [ ] Перенести хук из `.claude/settings.local.json` проекта в `~/.claude/settings.json` и
      записать путь прямыми слэшами (см. [kb/mcp.md](kb/mcp.md)).
- [ ] Проверить `filmcraft-app` на живом окне (возможно, нужен `FILMCRAFT_CONTROL_TOKEN`).
- [ ] Поставить PhotoCraft, LightCraft и другие программы по мере надобности.
- [ ] Проба для `remotion-skill`: Lottie-плашка из EffectCraft в композиции `KineticText`.

## Как это устроено

- **Здесь** — полная база знаний и песочница для проб.
- **Скилл `craft-apps`** (shared-claude-skills) — короткая рабочая инструкция для Claude.
  Подтягивается сам в любом проекте.
- **MCP** хранится в `~/.claude.json` (уровень пользователя). `sync.ps1` этот файл не
  сохраняет. На новой машине регистрацию повторяет `setup-mcp.ps1`.
