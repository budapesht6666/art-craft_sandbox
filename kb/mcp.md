# MCP: Craft-программы и Claude Code

В каждую Craft-программу встроен MCP-сервер. Он запускается через CLI самой программы:
`<app>-cli mcp`, протокол stdio. Отдельных репозиториев под MCP нет, поэтому поиск по
слову «mcp» в названиях ничего не находит.

**Проверено на этой машине только для EffectCraft 0.17.0** (2026-10-25):

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

- **Где хук.** В `.claude/settings.local.json` проекта хук работает только в этой папке.
  Чтобы новые программы подключались при старте в любом проекте, хук нужен в
  `~/.claude/settings.json`.
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
C:\Program Files\PhotoCraft\photocraft-cli.exe     # путь по аналогии, проверить
C:\Program Files\VectorCraft\vectorcraft-cli.exe   # путь по аналогии, проверить
```

Для EffectCraft, FilmCraft и LightCraft эти пути указаны в документации. Для остальных
предполагаю тот же шаблон. Лаунчер может ставить и в другую папку, так что после
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

Флаг режима с окном отличается: у EffectCraft и FilmCraft `--bridge`, у LightCraft
`--connect`. Точный синтаксис смотрите в `docs/agents.md` или `docs/mcp.md` нужной программы.

Чтобы ограничить, какие файлы агент читает и пишет (PhotoCraft, VectorCraft):
`mcp --automation-read-root <папка> --automation-write-root <папка>`.

## Подключение к Claude Code

```powershell
# Для всех проектов (user scope): записывается в ~/.claude.json
claude mcp add --scope user effectcraft -- "C:\Program Files\EffectCraft\effectcraft-cli.exe" mcp
claude mcp add --scope user photocraft  -- "C:\Program Files\PhotoCraft\photocraft-cli.exe" mcp
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
