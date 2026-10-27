# Персей и Медуза: промпты для Gemini (бесплатный веб-интерфейс)

Задача — сравнить с кадром, нарисованным кодом ([vectorcraft](../vectorcraft/)):
даст ли Gemini фоны и персонажей ближе к Unknown Frequencies.

Порядок:

1. **Лист 0** (эталон каста: Персей в 4 ракурсах и воин) — новый чат. Это дизайн канала,
   его утверждаем первым. Не понравилось — правим промпт и перегенерируем, дальше не идём.
2. **Лист 2** (позы сцены) — **в том же чате**, с приложенным листом 0.
3. **Лист 1** (фон) — в **отдельном** чате и без вложений: людей на фоне быть не должно,
   а приложенный Персей подтолкнёт Gemini его туда нарисовать.

Готовые картинки класть в `sheets/` как `00_cast_model.png`, `01_bg_lair.png` и
`02_cast_perseus.png` (`.jfif` тоже подойдёт, это JPEG).

Нарезка листа 2:
`python %USERPROFILE%/.claude/skills/sprite-prompts/scripts/slice_sheet.py sheets/02_cast_perseus.png cut/cast --expect 6`

## Библия каста (входит в каждый промпт с персонажами дословно)

Свой дизайн канала: круглоголовые человечки, как принято в жанре, но без чужих
маскотов (скелет-ведущий — это Unknown Frequencies).

```
CAST STYLE for the whole channel: simple round-headed cartoon people. Large white egg-shaped head, about one third of the body height, no hair unless stated. Two small solid black oval eyes, thick expressive black eyebrows, a small simple mouth, a tiny nose or none, no visible ears. Skin pure white with a bold black outline. Small simple bodies with slightly thick limbs and round mitten hands. Exaggerated comedic expressions. Ancient Greek clothing: tunics, sandals, bronze helmets.
```

---

## Лист 0 — эталон каста (16:9, 4 рисунка 4×1)

```
Wide 16:9 landscape image. Character model sheet (turnaround) for a hand-drawn 2D animated YouTube video about Greek mythology.
CAST STYLE for the whole channel: simple round-headed cartoon people. Large white egg-shaped head, about one third of the body height, no hair unless stated. Two small solid black oval eyes, thick expressive black eyebrows, a small simple mouth, a tiny nose or none, no visible ears. Skin pure white with a bold black outline. Small simple bodies with slightly thick limbs and round mitten hands. Exaggerated comedic expressions. Ancient Greek clothing: tunics, sandals, bronze helmets.
PERSEUS: a young hero in a bronze Corinthian helmet with a tall red horsehair crest, worn pushed up high on top of his head so his whole white egg-shaped face is visible, a cream tunic with a brown leather belt, a red cape, sandals, a round polished bronze shield and a short sword in a scabbard.
THE SOLDIER: an ordinary Greek soldier in a blue tunic and a plain open-faced grey iron helmet.
Clean professional 2D cartoon style for an adult comedy history channel. Bold confident black outlines with slight natural line-weight variation. Flat colors with only light cross-hatching in the shadows: no gradients, no soft shading, no texture, no cast shadows on the ground. Pure white (#FFFFFF) background everywhere, no paper texture, no vignette.
Layout: exactly 4 separate full-body drawings arranged in an invisible grid of 4 columns and 1 row. Each drawing sits fully inside its own cell, centered, with wide empty white gutters between cells. Nothing overlaps, touches or crosses into another cell. All figures at the same scale and on the same baseline. No text, no numbers, no labels, no captions, no grid lines, no frames, no borders, no ground lines, no watermark.
Row 1: (1) Perseus standing straight, facing the viewer, arms relaxed, shield on his left arm, calm confident little smile; (2) Perseus in three-quarter view facing right, same neutral pose; (3) Perseus in strict side view facing right, same neutral pose; (4) the soldier standing straight, facing the viewer, arms relaxed, slightly bored expression.
```

### Правка листа 0 (тем же чатом, следующим сообщением)

Первая попытка 2026-10-27 ([sheets/00_cast_model.png](sheets/00_cast_model.png)): ракурсы
согласованы, лист чистый и режется. Но коринфский шлем закрыл голову-яйцо (видна только
маска), у воина квадратная голова и белые глаза с веками, пальцы вместо варежек, рисунок 3
в 3/4, а не в профиль. Описание Персея и воина выше уже поправлено.

```
Same model sheet, same layout and style. Changes:
- Perseus wears his Corinthian helmet pushed up high on top of his head, so his whole large white egg-shaped face is fully visible, like the classic way of wearing it. Keep the red crest.
- In drawing 3 Perseus is in a strict side profile facing right: face, body and feet all in profile.
- The soldier has the same large white egg-shaped head as Perseus and the same small solid black oval eyes with thick eyebrows, no white eyeballs, no eyelids. Keep his bored expression with the eyebrows.
- All hands are round mitten hands with a thumb only, no separate fingers. Slightly thicker arms and legs.
Keep everything else exactly the same.
```

Вторая попытка ([sheets/00_cast_model_v2.png](sheets/00_cast_model_v2.png)): Персей
утверждён (лицо-яйцо открыто, варежки, руки толще; профиль в рисунке 3 почти чистый). У
воина голова стала яйцом, но глаза всё равно белые с веками. Правка только рисунка 4:

```
Almost perfect. Change only drawing 4, the soldier: replace his eyes with exactly the same eyes as Perseus has in drawing 1 — two small solid black oval dots, no white eyeballs, no eyelids, no bags under the eyes. Show his bored look only with flat, low, slightly tilted thick eyebrows and the small flat mouth. Do not change drawings 1, 2 and 3 at all.
```

Если Персей при этом «поплывёт» — не страшно: лист всё равно режется на фигуры, Персея
берём из v2, воина из v3.

**Итог: эталон — [sheets/00_cast_model_v3.png](sheets/00_cast_model_v3.png)** (2026-10-27).
Глаза воина исправлены (чёрные овалы, лицо скорее хмурое, чем скучающее), Персей не
изменился (отличие от v2 — 0,3 % пикселей, шум JPEG). Нарезка `--expect 4` прошла с первого
раза: [cut/model/](cut/model/). Вывод: за правку модель надёжно чинит одну-две вещи, а
повторно проигнорированную черту исправляет, когда указываешь на образец на том же листе
(«exactly the same eyes as Perseus has in drawing 1»).

## Лист 1 — фон: логово Медузы (16:9, одна картинка)

```
Wide 16:9 landscape image. Background painting for a hand-drawn 2D animated YouTube video about Greek mythology, in the style of a modern adult cartoon history channel.
Scene: Medusa's lair on a barren rocky island at dusk. Ruins of a small Greek temple with broken marble columns on the left, a dark cave entrance in the cliff on the right, a glimpse of the sea on the far left horizon, orange and purple sunset sky. In the middle distance, three small grey stone statues of petrified warriors frozen in terrified poses. The lower center of the image is open, flat rocky ground where characters will stand later.
Style: bold dark brown-black ink outlines with natural line-weight variation, loose cross-hatching in the shadows, slightly muted warm painted colors, soft directional light from the setting sun, clear depth with foreground, middle ground and background, subtle paper grain.
No living characters, no people, no animals, no text, no letters, no logo, no watermark, no frame.
```

## Лист 2 — персонажи сцены (16:9, 6 рисунков 3×2)

```
Wide 16:9 landscape image. Character pose sheet for a hand-drawn 2D animated YouTube video about Greek mythology.
Perseus and the soldier are the same characters as in the attached reference image: keep identical proportions, head shape, eye design, colors, helmets and line style.
CAST STYLE for the whole channel: simple round-headed cartoon people. Large white egg-shaped head, about one third of the body height, no hair unless stated. Two small solid black oval eyes, thick expressive black eyebrows, a small simple mouth, a tiny nose or none, no visible ears. Skin pure white with a bold black outline. Small simple bodies with slightly thick limbs and round mitten hands. Exaggerated comedic expressions. Ancient Greek clothing: tunics, sandals, bronze helmets.
PERSEUS: a young hero in a bronze Corinthian helmet with a tall red horsehair crest, worn pushed up high on top of his head so his whole white egg-shaped face is visible, a cream tunic with a brown leather belt, a red cape, sandals, a round polished bronze shield and a short sword in a scabbard.
THE SOLDIER: an ordinary Greek soldier in a blue tunic and a plain open-faced grey iron helmet.
MEDUSA'S HEAD: green skin, angry glowing yellow eyes, a frown with small fangs, hair made of a dozen green snakes.
Clean professional 2D cartoon style for an adult comedy history channel. Bold confident black outlines with slight natural line-weight variation. Flat colors with only light cross-hatching in the shadows: no gradients, no soft shading, no texture, no cast shadows on the ground. Pure white (#FFFFFF) background everywhere, no paper texture, no vignette.
Layout: exactly 6 separate full-body drawings arranged in an invisible grid of 3 columns and 2 rows. Each drawing sits fully inside its own cell, centered, with wide empty white gutters between cells. Nothing overlaps, touches or crosses into another cell. All figures at the same scale; figures in one row share the same baseline. No text, no numbers, no labels, no captions, no grid lines, no frames, no borders, no ground lines, no watermark.
Row 1: (1) Perseus standing in side view facing right, one arm stretched far forward holding Medusa's severed head by her snake-hair, his own head turned away over his shoulder, eyes squeezed shut, a nervous sweat drop; (2) Perseus tiptoeing backwards, holding his polished shield up and looking into it like a mirror to see behind him, nervous; (3) Perseus triumphant, facing the viewer, raising Medusa's severed head high above his head with a huge grin.
Row 2: (4) the soldier facing left, arms thrown up, screaming in terror with huge eyes, the lower half of his body already turned into grey cracked stone; (5) Medusa's severed head alone, snakes hissing in all directions, angry glare; (6) the same soldier completely turned into a grey cracked stone statue, frozen mid-scream with arms up.
```
