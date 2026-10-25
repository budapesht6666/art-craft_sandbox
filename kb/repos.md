# Все репозитории storytold

68 репозиториев на 2026-10-25 ([список](https://github.com/orgs/storytold/repositories?type=all)).
Получить свежий список:

```sh
curl -s "https://api.github.com/orgs/storytold/repos?per_page=100&type=all"
```

## Craft-программы (бесплатные)

photocraft, filmcraft, lightcraft, vectorcraft, effectcraft, designcraft, figcraft,
soundcraft, cadcraft, pdfcraft, wordcraft, gridcraft, deckcraft, AniCraft (заготовка).
Подробности в [craft-apps.md](craft-apps.md).

Ещё одна программа из этой группы:

- **craft-launcher** — установщик и обновлятор всех Craft-программ.

## Платная генерация

| Репозиторий | Что это |
|---|---|
| artcraft | Студия ИИ-картинок и видео, генерация за кредиты |
| artcraftx | Упрощённое приложение для ИИ-генерации, сборок нет |
| artcraft-services | Серверная часть и сайт облака ArtCraft |
| placeholder-artcraft | Архив, старая заглушка |

## Полезное отдельно

- **spark** (MIT) — рендерер 3D Gaussian Splatting для Three.js. Фотореалистичные
  3D-сцены, снятые с реальных мест. Можно встроить в `@remotion/three`.
- **indd-utils** — читает файлы InDesign без InDesign, конвертирует в IDML.
- **craft-ai-integrations** — общий ИИ-слой Craft-программ (свои ключи, ComfyUI, SAM).

## Общие компоненты Craft-программ

craft-libs (общие Rust-библиотеки), craft-fonts, craft-i18n (переводы),
craft-common-actions (CI), craft-contrib, craft-repo-status-app, craft-launcher-assets,
crafthub (пустой), photocraft-corpus (тестовые файлы), github-media (видео для README),
cloud-worker (без описания).

Форки чужих библиотек: egui, winit, winprint.rs.

## Наследие прошлых проектов (2020–2024)

Раньше команда делала синтез голоса (FakeYou, vo.codes) и VTuber-шоу на Unreal Engine.
Пользователю это не нужно.

- **Голос и ML:** storyteller-ml (Tacotron), vits-finetuning, realtime-voice-conversion,
  torchscript-models, FineTrainers-Conditioning, discord-vocodes, fakeyou-recast,
  voder-proxy, redirect-vocodes.
- **Unreal Engine:** HyperJail, AnimationTest, StreamTwo, UnrealZeroMQ, EventCenterPlugin,
  ActorSpawningPlugin, RuntimeAudioImporter, RuntimeFilesDownloader, UE4-OSC, CloudCamPlugin.
- **Захват движения и 3D-сканирование:** LiveScan3D, Azure-Kinect-Sample-for-Unity,
  k4a-sys-temp, cloudcam, point-generator, bevy-mocap, xsens-packet-send,
  motion-capture-data, storyteller-bevy.
- **Прочее:** hanashi-graphics-demo, html_test, irsa-manager,
  terraform-aws-observability-accelerator.
