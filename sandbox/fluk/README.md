# Флюк — мультсериал про белого кота

Один проект на всё про Флюка: персонаж, рисунки, серии, звук и пройденные подходы.
Исследование ниши и инструментов — [kb/youtube-research.md](../../kb/youtube-research.md),
[kb/animation-toolkit.md](../../kb/animation-toolkit.md).

## Где что лежит

| Папка | Что там |
|---|---|
| `art/` | Рисунки Gemini: [PROMPTS.md](art/PROMPTS.md) (библия персонажа и промпты листов), `sheets/` (листы PNG), `cut/` (нарезка: model, expr, poses, parts, hands, props), `ref/` (фото кота пользователя, только локально), `gemini.py` (API, на бесплатном ключе картинки недоступны) |
| `episode1/` | **Текущая работа**, серия «The Cucumber»: сценарий [EPISODE1.md](episode1/EPISODE1.md); ключи `gen_ec.py` → `ec/build_ec.js` → проект EffectCraft; звук `sfx_ep1.py` → `stems/` → сессия SoundCraft `fluk_ep1.scsession`; монтаж FilmCraft `fluk_ep1.fcproj`; обложка PhotoCraft `thumb/`; результат в `out/` |
| `sound/` | `synth.py` — общие синтезаторы звуков и `clip()` для живых записей; `cc0/` — мурчание и мяуканье (CC0, Kerzoven, opengameart.org/content/cat-purr-meow) |
| `archive/` | Пройденные подходы, каждый со своим README |

## Подходы по порядку (2026-10-26)

1. `archive/01-effectcraft-cutout` — перекладка в EffectCraft, кот нарисован кодом.
   «Картонная кукла», пользователь: «дерьмо полное».
2. `archive/02-blender-gp` — Blender Grease Pencil, каждый кадр рисуется кодом, риг и
   ходьба в Python. Тело гнётся, но рисунок кодом некрасивый: «морда уродская»,
   «тело странной формы», «рука — отдельный ужас».
3. `archive/03-blender-mesh` — рисунок Gemini на сетке в Blender. Технология работает;
   показала, что перекрытые части нужно рисовать отдельно.
4. `archive/04-parts-test` — Флюк из деталей Gemini (торс, голова, лапы) на Pillow.
   Картинка держится, но «движения надуманные и не смешные».
5. `archive/05-pillow-poses` — та же серия целыми позами на Pillow.
6. **`episode1/` — сейчас:** конвейер на Craft-программах (ниже).

## Конвейер серии (2026-10-26)

| Подзадача | Программа |
|---|---|
| Рисунки: персонаж, позы, руки, реквизит, комната | Gemini, бесплатно, спрайт-листы (скилл `sprite-prompts`) |
| Нарезка листов | `slice_sheet.py` (Python) |
| Головы для крупных планов в вектор | **VectorCraft**: `imageTrace` в режиме `logo` |
| Сцена и анимация: позы, Puppet-булавки, камера, размытие в движении | **EffectCraft** (ключи из `gen_ec.py`, сборка `ec/build_ec.js`) |
| Звук: 4 дорожки → сведение и мастеринг до −16 LUFS | Python-синтез + CC0 → **SoundCraft** |
| Монтаж: титр, версии 16:9 и Shorts 9:16 с ведением кадра | **FilmCraft** |
| Обложка YouTube | **PhotoCraft** |

## Как запускать

```
cd sandbox/fluk/episode1
python gen_ec.py      # ec/ep1_keys.json
# EffectCraft: открыть/сохранить ec/fluk_ep1.ecproj, run_script: eval(build_ec.js), рендер (30 с)
python sfx_ep1.py     # stems/*.wav, затем SoundCraft fluk_ep1.scsession → stems/master.wav
# FilmCraft: fluk_ep1.fcproj → out/fluk_ep1_cucumber_16x9.mp4 и _shorts.mp4
```

Нарезка новых листов:
`python <shared-claude-skills>/skills/sprite-prompts/scripts/slice_sheet.py art/sheets/08_key_poses.png art/cut/key --expect 8 --prefix key`.
