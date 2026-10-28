# MCP: Craft-программы и Claude Code

В каждую Craft-программу встроен MCP-сервер. Он запускается через CLI самой программы:
`<app>-cli mcp`, протокол stdio. Отдельных репозиториев под MCP нет, поэтому поиск по
слову «mcp» в названиях ничего не находит.

**Проверено на этой машине** (2026-10-25): EffectCraft 0.17.0, FilmCraft 0.13.0,
PhotoCraft 0.16.0, VectorCraft 0.17.0, SoundCraft 0.13.1. Подробности в разделах ниже.
EffectCraft:

- путь к CLI `C:\Program Files\EffectCraft\effectcraft-cli.exe`;
- MCP-сервер отдаёт 27 инструментов;
- `run_script`, `file.exportLottie`, `save_project` и `render-frame` работают.

Остальное взято из README, `docs/agents.md` и `docs/mcp.md` репозиториев.

Подключено на уровне пользователя:

- `effectcraft` → `effectcraft-cli.exe mcp --autosave`
- `effectcraft-app` → `effectcraft-cli.exe mcp --bridge 9877`. Работает только с окном,
  запущенным с `--control 9877`. Обычный запуск порт не открывает, это проверено. Есть
  скрипт `shared-claude-skills\skills\craft-apps\scripts\start-live.ps1`.

У канала управления нет авторизации (только 127.0.0.1), постоянно его не включать.

Новые программы регистрирует скрипт `shared-claude-skills\skills\craft-apps\scripts\setup-mcp.ps1`
(есть `-WhatIf`).

Команда `claude` на этой машине не в `PATH` у PowerShell. Полный путь:
`%USERPROFILE%\.local\bin\claude.exe`.

## Автоподключение новых программ (хук SessionStart)

`setup-mcp.ps1 -Quiet` молчит, если ничего не добавил, и отрабатывает за 0,7 с. Поэтому
его можно запускать хуком при каждом старте сессии.

Ловушки (проверено 2026-10-25):

- **Где хук.** Хук лежит в `.claude/settings.local.json` этого проекта (решение
  пользователя). Он не попадает в git и срабатывает только при запуске сессии здесь. Чтобы
  программы подключались при старте в любом проекте, хук нужно перенести в
  `~/.claude/settings.json`.
- **Matcher `startup`.** Хук срабатывает только при запуске новой сессии. Без matcher он
  срабатывал бы ещё и при `resume`, `clear` и `compact`.
- **Слэши.** Путь пишите прямыми слэшами (`C:/projects/...`). Обратные слэши bash
  съедает, и получается `C:projectsclaude...`.
- **Проверка.** Время последнего запуска хука лежит в
  `%LOCALAPPDATA%\craft-apps\setup-mcp-last-run.txt`.
- **PowerShell 5.1 не разбирает `~/.claude.json` через `ConvertFrom-Json`**: в списке
  проектов пути повторяются с разным регистром буквы диска. Скрипт читает файл через
  `JavaScriptSerializer`.

```json
"hooks": {
  "SessionStart": [
    {
      "matcher": "startup",
      "hooks": [
        {
          "type": "command",
          "command": "powershell -NoProfile -ExecutionPolicy Bypass -File C:/projects/claude/shared-claude-skills/skills/craft-apps/scripts/setup-mcp.ps1 -Quiet",
          "timeout": 30
        }
      ]
    }
  ]
}
```

## FilmCraft

Проверено 2026-10-25, FilmCraft 0.13.0:

- `filmcraft` (без окна) стартует с пустым проектом;
- `file.openDemoProject` открывает демо-проект (последовательность 21);
- `render_frame {seconds: 2}` отдаёт кадр.

Время в FilmCraft считается в тиках: 254016000000 на секунду. Команды принимают и `seconds`,
`frame` или `timecode`.

У FilmCraft нет флагов, ограничивающих доступ к папкам (`--automation-read-root`): сервер
может читать и писать везде, куда может пользователь.

## PhotoCraft, VectorCraft, SoundCraft

Подключены 2026-10-25 хуком `SessionStart`. Проверка: сервер запущен вручную по stdio,
`initialize` → `tools/list` → создание документа → сохранение в файл.

| Программа | Сервер | Инструментов | Проверено |
|---|---|---|---|
| PhotoCraft 0.16.0 | `photocraft` → `mcp --automation-read-root C:/projects --automation-write-root C:/projects` | 26 | `doc_new`, `doc_save` (png, jpg, webp), `doc_open` |
| VectorCraft 0.17.0 | `vectorcraft` → `mcp` | 32 | `draw_shape` (звезда), `export` в svg |
| SoundCraft 0.13.1 | `soundcraft` → `mcp` | 17 | `new_session {template: demo}`, `bounce_mix` 2 с в wav (`lufs`, `peak_db` в ответе) |

После перезапуска сессии все три сервера видны в Claude Code и отвечают (2026-10-25).

**PhotoCraft вырезает героя из кадра** (проверено 2026-10-28, 0.16.0): `command_run
layer.removeBackground {"refine": true}` (это Select Subject + маска) и `doc_save` в png с
альфой. «Главный объект» программа выбирает сама: из кадра «девушка + собака» берёт
девушку, поэтому героя вырезают из кадра, обрезанного вокруг него. Серое на сером
(собака на асфальте, белая футболка на светлом фоне) приходится дочищать. Рецепт — в
скилле `craft-apps`, раздел «вырезать героя из кадра».
У `soundcraft` `inspect_session {detail: "summary"}` всё равно возвращает почти всю сессию
(у демо-сессии это около 600 строк JSON). Для точечных вопросов это много.

**Доступ к файлам:**

- **PhotoCraft в режиме без окна без корней не трогает ни одного файла.** Любой путь
  отклоняется: «automation path rejected: drive, device and stream prefixes are not
  allowed». Каждый флаг можно указать только один раз (`cannot be used multiple times`).
  Корень `C:/` принимается. Пользователь выбрал `C:/projects` на чтение и запись: пути вне
  него отклоняются («absolute paths must be inside the automation root»), относительные
  пути считаются от корня. Корни прописаны в `setup-mcp.ps1`.
- **PhotoCraft не создаёт папку для сохранения.** Если её нет, `doc_save` падает с
  `NotFound`. Создайте папку заранее.
- VectorCraft и SoundCraft без флагов читают и пишут везде, куда может пользователь.
  Флаги корней у них можно повторять. Если их задать, разрешено только внутри.

**Режим с окном** (по `--help`, не проверено):

- PhotoCraft: окно `photocraft --control <порт>`, MCP `mcp --bridge <порт>`. Нужен токен
  (`--control-token`, `--control-token-file` или `PHOTOCRAFT_CONTROL_TOKEN`). В этом режиме
  корни задаются у программы, а у MCP флаги корней запрещены.
- VectorCraft: `vectorcraft-cli mcp` без флагов сам подключается к окну на
  127.0.0.1:7979 (`vectorcraft --control 7979`), а если окна нет, работает без него.
  `--connect ADDR` задаёт другой адрес, `--headless` запрещает подключение. Флаги корней
  включают режим без окна.
- SoundCraft: окно `soundcraft --control 0`, MCP `mcp --connect <порт>`. Инструменты с
  пометкой APP_ONLY (скриншот, клики) работают только так. Есть и `soundcraft-cli app
  [--port P] METHOD [JSON]` для разовых вызовов в окно.

## Как узнать, что установлено

`shared-claude-skills\skills\craft-apps\scripts\status.ps1 -Online` показывает по каждой
программе: установленную версию (из реестра Windows, куда MSI пишет установку), свежую
версию на GitHub, есть ли CLI и подключён ли MCP.

Вручную: «Установка и удаление программ» в Windows (издатель Learning Machines LLC) или
папки `C:\Program Files\*Craft`.

Автообновление в лаунчере по умолчанию выключено (`auto_update:false` в
`%APPDATA%\ai.storyteller.artcraft-launcher\data\app.ron`). Сам лаунчер обновляется:
за день он поднялся с 0.7.0 до 0.8.1.

## Где лежит CLI

На Windows MSI-установщик кладёт CLI рядом с программой, но в `PATH` не добавляет:

```
C:\Program Files\EffectCraft\effectcraft-cli.exe
C:\Program Files\FilmCraft\filmcraft-cli.exe
C:\Program Files\LightCraft\lightcraft-cli.exe
C:\Program Files\PhotoCraft\photocraft-cli.exe
C:\Program Files\VectorCraft\vectorcraft-cli.exe
C:\Program Files\SoundCraft\soundcraft-cli.exe
```

Пути EffectCraft, FilmCraft, PhotoCraft, VectorCraft и SoundCraft проверены на этой машине
(2026-10-25), путь LightCraft взят из документации. Для остальных предполагаю тот же
шаблон. Лаунчер может ставить и в другую папку, так что после
установки путь нужно проверить.

На macOS CLI идёт отдельным архивом `<app>-cli-<ver>-macos-universal.zip`.

## Два режима

| Режим | Команда | Что даёт |
|---|---|---|
| Без окна | `<app>-cli mcp [файлы/папки]` (`--demo` открывает демо-проект) | Движок без интерфейса: открыть, изменить, отрендерить, экспортировать. Подходит для автоматизации |
| С окном | программа запущена с `--control <порт>`, а MCP подключается к ней (`--bridge <порт>` или `--connect 127.0.0.1:<порт>`) | Работа в живом окне: скриншоты, клики, жесты. Видно, что делает агент |

Порты по умолчанию из примеров:

| Программа | Порт |
|---|---|
| FilmCraft | 9876 |
| EffectCraft | 9877 |
| VectorCraft | 7979 |
| LightCraft | 7980 |

Флаг режима с окном отличается: у EffectCraft, FilmCraft и PhotoCraft `--bridge`, у
LightCraft, VectorCraft и SoundCraft `--connect`. Точный синтаксис смотрите в `--help`,
`docs/agents.md` или `docs/mcp.md` нужной программы.

Чтобы ограничить, какие файлы агент читает и пишет (PhotoCraft, VectorCraft, SoundCraft):
`mcp --automation-read-root <папка> --automation-write-root <папка>`. У PhotoCraft без них
файлы недоступны вовсе (см. выше).

## Подключение к Claude Code

```powershell
# Для всех проектов (user scope): записывается в ~/.claude.json
claude mcp add --scope user effectcraft -- "C:\Program Files\EffectCraft\effectcraft-cli.exe" mcp
claude mcp add --scope user photocraft  -- "C:\Program Files\PhotoCraft\photocraft-cli.exe" mcp --automation-read-root C:/projects --automation-write-root C:/projects
claude mcp add --scope user soundcraft  -- "C:\Program Files\SoundCraft\soundcraft-cli.exe" mcp
claude mcp add --scope user lightcraft  -- "C:\Program Files\LightCraft\lightcraft-cli.exe" mcp
claude mcp add --scope user filmcraft   -- "C:\Program Files\FilmCraft\filmcraft-cli.exe" mcp
claude mcp add --scope user vectorcraft -- "C:\Program Files\VectorCraft\vectorcraft-cli.exe" mcp

# Только для одного проекта (project scope): пишется в .mcp.json в корне проекта, коммитится
claude mcp add --scope project effectcraft -- "C:\Program Files\EffectCraft\effectcraft-cli.exe" mcp
```

Проверка: `claude mcp list`, затем в сессии `/mcp`.

Если это не помогает:

- Запустить CLI вручную (`& "C:\Program Files\EffectCraft\effectcraft-cli.exe" --help`)
  и посмотреть, что он пишет.
- После переустановки или обновления программы перезапустить MCP-подключения.

## Чем ещё можно управлять без MCP

Каждая программа принимает разовые CLI-вызовы с JSON на выходе. Их удобно вызывать из
скриптов `remotion-skill`:

```sh
effectcraft-cli render --comp Main --out main.mp4
effectcraft-cli exec file.exportLottie '{"comp":"Main","path":"main.json"}' main.ecproj
effectcraft-cli set Main '#1' transform/position '[100,360]' --time 0 main.ecproj --save

photocraft-cli run wave.psd \
  --cmd filter.sharpen.smartSharpen --params '{"amount":80}' \
  --out wave-final.png

filmcraft-cli commands      # список всех команд движка
```
