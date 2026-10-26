# Персей и Медуза: промпты для Gemini (бесплатный веб-интерфейс)

Задача — сравнить с кадром, нарисованным кодом ([vectorcraft-history-style](../vectorcraft-history-style/)):
даст ли Gemini фоны и персонажей ближе к Unknown Frequencies.

Порядок: **лист 1** (фон) и **лист 2** (персонажи) можно делать в разных чатах, они не
зависят друг от друга. Если персонажи понравятся, следующие листы с ними — в том же чате и
с приложенным листом 2. Готовые картинки класть в `sheets/` как `01_bg_lair.png` и
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
CAST STYLE for the whole channel: simple round-headed cartoon people. Large white egg-shaped head, about one third of the body height, no hair unless stated. Two small solid black oval eyes, thick expressive black eyebrows, a small simple mouth, a tiny nose or none, no visible ears. Skin pure white with a bold black outline. Small simple bodies with slightly thick limbs and round mitten hands. Exaggerated comedic expressions. Ancient Greek clothing: tunics, sandals, bronze helmets.
PERSEUS: a young hero in a bronze Corinthian helmet with a tall red horsehair crest, a cream tunic with a brown leather belt, a red cape, sandals, a round polished bronze shield and a short sword in a scabbard.
THE SOLDIER: an ordinary Greek soldier in a blue tunic and a plain grey iron helmet.
MEDUSA'S HEAD: green skin, angry glowing yellow eyes, a frown with small fangs, hair made of a dozen green snakes.
Clean professional 2D cartoon style for an adult comedy history channel. Bold confident black outlines with slight natural line-weight variation. Flat colors with only light cross-hatching in the shadows: no gradients, no soft shading, no texture, no cast shadows on the ground. Pure white (#FFFFFF) background everywhere, no paper texture, no vignette.
Layout: exactly 6 separate full-body drawings arranged in an invisible grid of 3 columns and 2 rows. Each drawing sits fully inside its own cell, centered, with wide empty white gutters between cells. Nothing overlaps, touches or crosses into another cell. All figures at the same scale; figures in one row share the same baseline. No text, no numbers, no labels, no captions, no grid lines, no frames, no borders, no ground lines, no watermark.
Row 1: (1) Perseus standing in side view facing right, one arm stretched far forward holding Medusa's severed head by her snake-hair, his own head turned away over his shoulder, eyes squeezed shut, a nervous sweat drop; (2) Perseus tiptoeing backwards, holding his polished shield up and looking into it like a mirror to see behind him, nervous; (3) Perseus triumphant, facing the viewer, raising Medusa's severed head high above his head with a huge grin.
Row 2: (4) the soldier facing left, arms thrown up, screaming in terror with huge eyes, the lower half of his body already turned into grey cracked stone; (5) Medusa's severed head alone, snakes hissing in all directions, angry glare; (6) the same soldier completely turned into a grey cracked stone statue, frozen mid-scream with arms up.
```
