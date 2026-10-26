# Флюк: промпты для Gemini (бесплатный веб-интерфейс)

Порядок: сначала **лист 1** (эталон дизайна). Если Флюк нравится, остальные листы в
**том же чате**, к каждому прикладывать картинку листа 1. Готовые PNG класть в
`sandbox/fluk/art/sheets/` с именами `01_model.png`, `02_expressions.png` и т. д.
Нарезка: `python <skills>/sprite-prompts/scripts/slice_sheet.py sheets/03_poses.png cut/poses --expect 6`.

Если в интерфейсе нельзя выбрать соотношение сторон, оно указано в самом промпте.

## Библия Флюка (входит в каждый промпт дословно)

```
FLUK, an original cartoon cat: chubby and fluffy with pure white fur; big round head with
full round cheeks; medium ears with softly rounded tips and pale pink insides; large eyes
with light sage-green irises, big black pupils and two white shines; small pink nose; tiny "w"
mouth; soft pink cheek blush; short stubby legs with round paws; thick fluffy tail.
Personality: lazy, smug and easily offended. His signature expression is a half-lidded,
unimpressed side-eye.
```

---

## Лист 1 — эталон: Флюк в четырёх ракурсах (16:9, 4 рисунка)

```
Wide 16:9 landscape image. Character model sheet.
FLUK, an original cartoon cat: chubby and fluffy with pure white fur; big round head with full round cheeks; medium ears with softly rounded tips and pale pink insides; large eyes with light sage-green irises, big black pupils and two white shines; small pink nose; tiny "w" mouth; soft pink cheek blush; short stubby legs with round paws; thick fluffy tail. Personality: lazy, smug and easily offended. His signature expression is a half-lidded, unimpressed side-eye.
Clean professional 2D cartoon animation style for an adult comedy web series. Appealing simple shapes with solid construction. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows, no highlights except the eye shines. Pure white (#FFFFFF) background everywhere, no paper texture, no vignette.
Layout: exactly 4 separate drawings arranged in an invisible grid of 4 columns and 1 row. Each drawing sits fully inside its own cell, centered, with wide empty white gutters between cells. Nothing overlaps, touches or crosses into another cell. All drawings at the same scale and on the same baseline. No text, no numbers, no labels, no captions, no grid lines, no frames, no borders, no ground lines, no watermark.
Cells, left to right: (1) side view, standing on all four legs, facing right, calm smug look; (2) three-quarter view, sitting, looking at the viewer with the half-lidded unimpressed side-eye; (3) front view, sitting, neutral cute face; (4) back view, sitting, tail curled around the paws.
```

## Лист 2 — выражения (1:1, 9 голов)

```
Square 1:1 image. Expression sheet of the same character as in the attached reference image: keep identical proportions, head shape, eye design, colors and line style.
FLUK, an original cartoon cat: chubby and fluffy with pure white fur; big round head with full round cheeks; medium ears with softly rounded tips and pale pink insides; large eyes with light sage-green irises, big black pupils and two white shines; small pink nose; tiny "w" mouth; soft pink cheek blush; short stubby legs with round paws; thick fluffy tail. Personality: lazy, smug and easily offended. His signature expression is a half-lidded, unimpressed side-eye.
Clean professional 2D cartoon animation style for an adult comedy web series. Appealing simple shapes with solid construction. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows, no highlights except the eye shines. Pure white (#FFFFFF) background everywhere, no paper texture, no vignette.
Layout: exactly 9 separate drawings of the head only, three-quarter view facing right, arranged in an invisible grid of 3 columns and 3 rows. Each drawing sits fully inside its own cell, centered, with wide empty white gutters between cells. Nothing overlaps, touches or crosses into another cell. All heads at the same size. No text, no numbers, no labels, no captions, no grid lines, no frames, no borders, no watermark.
Row 1: (1) neutral cute; (2) signature half-lidded unimpressed side-eye, flat mouth; (3) shocked: tiny pupils, ears flattened, fur puffed, mouth open.
Row 2: (4) blissful: eyes closed in happy arcs, purring smile; (5) suspicious squint, one eyebrow-like lid lower; (6) offended: eyes closed, nose up, turned slightly away.
Row 3: (7) hunting: huge round pupils, ears pointed forward, focused; (8) annoyed glare straight at the viewer; (9) big lazy yawn, eyes squeezed shut.
```

## Лист 3 — ключевые позы (16:9, 8 рисунков)

```
Wide 16:9 landscape image. Pose sheet of the same character as in the attached reference image: keep identical proportions, head shape, eye design, fluffy fur outline, colors and line style.
FLUK, an original cartoon cat: chubby and fluffy with pure white fur; big round head with full round cheeks; medium ears with softly rounded tips and pale pink insides; large eyes with light sage-green irises, big black pupils and two white shines; small pink nose; tiny "w" mouth; soft pink cheek blush; short stubby legs with round paws; thick fluffy tail. Personality: lazy, smug and easily offended. His signature expression is a half-lidded, unimpressed side-eye.
Clean professional 2D cartoon animation style for an adult comedy web series. Appealing simple shapes with solid construction. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows, no highlights except the eye shines. Pure white (#FFFFFF) background everywhere, no paper texture, no vignette.
Layout: exactly 8 separate full-body drawings arranged in an invisible grid of 4 columns and 2 rows. Body always in side view facing right; the head may turn toward the viewer as in the reference. Each drawing sits fully inside its own cell, centered, with wide empty white gutters between cells. Nothing overlaps, touches or crosses into another cell. All drawings at the same scale; figures in one row share the same baseline. No props, no text, no numbers, no labels, no captions, no grid lines, no frames, no borders, no ground lines, no watermark.
Row 1: (1) eating: front low, head bowed down to floor level, eyes closed happily; (2) stalking: body pressed low to the floor, shoulders up, huge pupils, tail low and tense; (3) startled vertical jump: back arched high like a Halloween cat, all four legs stiff and straight, tail puffed up, tiny pupils, ears flat; (4) sniffing: neck stretched far forward, nose down, cautious squint.
Row 2: (5) sitting upright, chest out, smug half-lidded side-eye at the viewer; (6) proud walk: head up, eyes closed, tail straight up with a curl at the tip; (7) calm walk mid-stride, relaxed tail; (8) pounce: leaping forward, body fully stretched, front paws reaching ahead, hind legs extended back.
```

## Лист 4 — детали для рига (16:9, 8 рисунков)

Части рисуются отдельно, чтобы кости гнули их по отдельности (как в Live2D или Spine).

```
Wide 16:9 landscape image. Cut-out animation parts kit of the same character as in the attached reference image: keep identical proportions, fluffy fur outline, colors and line style, at the same scale as the standing side view in the reference.
FLUK, an original cartoon cat: chubby and fluffy with pure white fur; big round head with full round cheeks; medium ears with softly rounded tips and pale pink insides; large eyes with light sage-green irises, big black pupils and two white shines; small pink nose; tiny "w" mouth; soft pink cheek blush; short stubby legs with round paws; thick fluffy tail.
Clean professional 2D cartoon animation style. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows. Pure white (#FFFFFF) background everywhere.
Layout: exactly 8 separate parts arranged in an invisible grid of 4 columns and 2 rows, each part fully inside its own cell with wide empty white gutters, nothing overlapping. Every part is complete with a closed outline; where a part joins the body its end is rounded and slightly oversized so it can tuck under the torso. No text, no numbers, no labels, no grid lines, no frames, no watermark.
Row 1: (1) torso only, side view facing right: a soft chubby bean shape with a fluffy chest, no head, no legs, no tail; (2) head only, three-quarter view facing right like in the reference standing pose, neutral calm face, ears included; (3) near front leg only, straight, round paw; (4) far front leg only, the same shape in a slightly lighter cool-grey white.
Row 2: (5) near hind leg only, with a rounded fluffy haunch, bent at the hock, round paw; (6) far hind leg only, the same in a slightly lighter cool-grey white; (7) tail only, relaxed gentle S-curve; (8) tail only, puffed up straight like a bottle brush.
```

## Лист 5 — руки хозяина (1:1, 9 рисунков)

```
Square 1:1 image. Sheet of human arms for a 2D cartoon: an adult's arm in a grey hoodie sleeve with a simple friendly cartoon hand (four fingers and a thumb), entering the picture from the top edge.
Clean professional 2D cartoon animation style for an adult comedy web series. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows. Pure white (#FFFFFF) background everywhere.
Layout: exactly 9 separate drawings arranged in an invisible grid of 3 columns and 3 rows, each fully inside its own cell with wide empty white gutters, nothing overlapping. Same sleeve, same hand, same scale in all nine. No text, no numbers, no labels, no grid lines, no frames, no watermark.
Row 1: (1) hand pinching a cucumber in the middle, lowering it; (2) hand opening to release; (3) open empty hand pulling back up.
Row 2: (4) index finger pointing down, scolding; (5) hand petting gently, palm down; (6) hand holding a small red laser pointer.
Row 3: (7) hand holding a glass of water; (8) hand shaking a treat bag; (9) hand reaching down, fingers spread, tiptoe-sneaky.
```

## Лист 6 — реквизит (1:1, 9 рисунков)

```
Square 1:1 image. Props sheet for a 2D cartoon about a white cat.
Clean professional 2D cartoon animation style for an adult comedy web series. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows. Pure white (#FFFFFF) background everywhere.
Layout: exactly 9 separate objects arranged in an invisible grid of 3 columns and 3 rows, each fully inside its own cell with wide empty white gutters, nothing overlapping, all in a consistent scale for one scene. No text, no numbers, no labels, no grid lines, no frames, no watermark.
Row 1: (1) cucumber lying sideways, side view; (2) the same cucumber seen end-on, as a round cross-section; (3) steel cat food bowl full of kibble, side view.
Row 2: (4) the same bowl empty; (5) potted plant in a terracotta pot; (6) open cardboard box.
Row 3: (7) glass of water; (8) ball of red yarn; (9) small red laser dot glow on the floor.
```

## Лист 7 — комната (16:9, один фон)

```
Wide 16:9 landscape image. Background for a 2D cartoon: a cozy living room seen straight from the side, like a theatre stage. Back wall with soft mint striped wallpaper, white baseboard, warm wooden floor taking the lower quarter of the frame, a window with mustard curtains on the left, a framed picture of a fish on the wall, a blue armchair cut off at the right edge, a potted plant standing on the floor in the left corner. The middle of the floor is empty: space for characters.
Clean professional 2D cartoon animation style for an adult comedy web series. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows. No characters, no text, no watermark.
```

## Лист 8 — ключевые позы серии «Огурец» (16:9, 8 рисунков, приложить 01_model)

```
Wide 16:9 landscape image. Key pose sheet of the same character as in the attached reference image: keep identical proportions, head shape, eye design, fluffy fur outline, colors and line style.
FLUK, an original cartoon cat: chubby and fluffy with pure white fur; big round head with full round cheeks; medium ears with softly rounded tips and pale pink insides; large eyes with light sage-green irises, big black pupils and two white shines; small pink nose; tiny "w" mouth; soft pink cheek blush; short stubby legs with round paws; thick fluffy tail. Personality: lazy, smug and easily offended.
Clean professional 2D cartoon animation style for an adult comedy web series. Strong, exaggerated, readable silhouettes like classic cartoon key poses. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows, no highlights except the eye shines. Pure white (#FFFFFF) background everywhere.
Layout: exactly 8 separate full-body drawings in an invisible grid of 4 columns and 2 rows, all at the same scale, each fully inside its own cell with wide empty white gutters, nothing overlapping. No props, no text, no numbers, no labels, no grid lines, no frames, no ground lines, no watermark.
Row 1: (1) facing right, sitting back after a meal, licking his lips with a small pink tongue, eyes closed, blissfully satisfied; (2) facing right, standing, lazily looking back over his own shoulder toward his tail, half-lidded; (3) mid-air panic jump: body twisted in the air, all four legs splayed out stiffly in different directions, back arched, every bit of fur standing up, tail puffed straight up like a bottle brush, tiny pupils, mouth open in a yowl; (4) frozen after landing, facing left: crouched very low with bent legs, tail puffed, huge wide eyes staring at something on the floor ahead.
Row 2: (5) facing left, cautious approach: body stretched long and low, neck extended far forward, nose sniffing, one front paw lifted mid-step; (6) facing left, crouched, reaching one front paw far forward to poke something on the floor, eyes squinting suspiciously; (7) sitting, facing right, licking his raised front paw with eyes closed, pretending nothing happened, nonchalant; (8) sitting, facing right, paw still raised, slowly glancing at the viewer with the half-lidded "you saw nothing" side-eye.
```

## Лист 9 — добивка и головы (1:1, 9 рисунков, приложить 01_model)

```
Square 1:1 image. Sheet of the same character as in the attached reference image: keep identical proportions, head shape, eye design, fluffy fur outline, colors and line style.
FLUK, an original cartoon cat: chubby and fluffy with pure white fur; big round head with full round cheeks; medium ears with softly rounded tips and pale pink insides; large eyes with light sage-green irises, big black pupils and two white shines; small pink nose; tiny "w" mouth; soft pink cheek blush; short stubby legs with round paws; thick fluffy tail.
Clean professional 2D cartoon animation style for an adult comedy web series. Bold confident black outlines with slight natural line-weight variation. Flat colors only: no gradients, no shading, no texture, no cast shadows. Pure white (#FFFFFF) background everywhere.
Layout: exactly 9 separate drawings in an invisible grid of 3 columns and 3 rows, each fully inside its own cell with wide empty white gutters, nothing overlapping. No props, no text, no numbers, no labels, no grid lines, no frames, no watermark.
Row 1: (1) full body, facing right, slowly backing away to the left in a low crouch, eyes locked suspiciously on something on the floor in front of him; (2) full body, facing right, eating: head down, cheeks full, eyes closed happily, chewing; (3) full body, facing right, sitting tall with eyes closed and nose in the air, offended dignity.
Row 2 (heads only, three-quarter view): (4) looking back over the shoulder to the left, half-lidded; (5) looking down-left at the floor, suspicious; (6) eyes wide, staring left, ears flattened.
Row 3 (heads only, three-quarter view): (7) eyes darting to the side, nervous; (8) licking lips, tongue out, eyes closed; (9) guilty innocent glance at the viewer, eyes wide.
```
