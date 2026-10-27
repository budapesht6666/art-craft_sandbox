# Голос канала: клон голоса пользователя в ElevenLabs

- **Дата:** 2026-10-27
- **Зачем:** рассказчик говорит чисто и в нужном темпе, но твоим тембром; новые серии не нужно
  записывать целиком — достаточно текста. Коммерческие права есть с тарифа Starter.
- **Статус:** ждём образец и тариф (сейчас аккаунт на Free: клонирование недоступно; положена скидка на
  первый месяц Starter).

## Коротко (2026-10-27)

Ключ API даёт всё, кроме смены тарифа: создать клон, озвучить, сравнить модели Claude делает сам
(`clone.py`). От пользователя — **только перейти на Starter** на сайте. Образец для первой пробы уже есть:
демо-запись (`sandbox/history/anim/voice`, Telegram/AAC) → `channel/local/voice/sample_clean.mp3`, 61 с.
Для чистового клона лучше новый образец по пункту 2 (без пережатия, 1,5–2 мин, разный текст).

```
python clone.py prepare <запись>   # чистка образца
python clone.py create             # после перехода на Starter
python clone.py test               # глава 1 на eleven_multilingual_v2 / eleven_v3 / eleven_v4
```

## Что нужно от тебя

### 1. Тариф Starter

elevenlabs.io → вход в тот же аккаунт, что уже подключён → **Upgrade** (или Settings → Subscription) →
**Starter** (по сторонним обзорам $5–6/мес, со скидкой на первый месяц — дешевле; точную цену покажет
сайт). Что даёт: коммерческие права на озвучку, мгновенный клон голоса (Instant Voice Cloning), около
30 000 знаков в месяц. Серия — около 7 600 знаков, то есть хватает на серию с запасом на переделки.

### 2. Записать образец: 1,5–2 минуты, по-английски

Текст — ниже. Читай **так, как хочешь, чтобы звучал рассказчик**: клон копирует не только тембр, но и
манеру, темп и акцент из образца. Если прочитать вяло — клон тоже будет вялым.

- iPhone: Настройки → Приложения → Диктофон → Качество звука → **Без сжатия**.
- Тихая маленькая комната, мягкие вещи вокруг, телефон на опоре в 15–20 см, чуть сбоку, авиарежим.
- **Одно расстояние до телефона всё время**, без шёпота и крика, без музыки и посторонних голосов.
- Ошибся — сделай паузу и перечитай фразу заново, лишнее я вырежу (в образце не должно быть «эээ»).
- Передать через AirDrop или «Сохранить в Файлы» (Telegram — только «Отправить как файл»).

Я почищу запись (шум, громкость к рекомендованным −23…−18 dB RMS, пик ниже −3 dB) и отдам тебе
готовый файл для загрузки.

### 3. Создать клон

Делает Claude через API (`clone.py create`), руками ничего не нужно. Если сайт попросит подтвердить
согласие на клонирование своего голоса — подтвердить там (галочка «это мой голос»).

### 4. Сравнить

Я пришлю одну главу в трёх вариантах: твой клон, черновой голос, и (если запишешь) твоя живая запись
с ускорением. Решаем по звучанию, потом озвучиваю серию целиком.

## Текст образца (≈ 260 слов, 1,5–2 мин)

Our story starts in the Greek city of Argos, with King Acrisius. Acrisius had a daughter, Danaë. But he
wanted a son. So he went to the Oracle of Delphi. Basically ancient Google, but with more smoke.

He asked: "Will I have a son?" The Oracle said: "No. But your daughter will. And your grandson will kill
you."

Now, a normal person would say: "Okay. I will be really, really nice to my grandson." Acrisius did not
say that.

He built a bronze tower and locked Danaë inside. No doors. No boys. No visitors. No grandson. Problem
solved.

Problem not solved. Because this is Greek mythology, and in Greek mythology, there is always Zeus.

Years passed. Perseus grew up strong, brave, and... let's say, very confident.

At a royal party, every guest brought the king a horse. Perseus had no horse. Perseus had no money.
Perseus had... confidence. "Horses are boring! Name anything, and I will bring it. Even the head of
Medusa!" The room went quiet. The king smiled. "Deal."

The Graeae were three old sisters. They were born old. Grey hair from day one. And between the three of
them, they had one eye. And one tooth. They passed the eye around and took turns seeing. "My turn!" "No,
my turn!" "You had it yesterday!"

The oracle was right. You can't run from fate. Fate has very good aim.

## Как это встанет в конвейер (для Claude)

- Найти голос: `GET /v1/voices` → по имени `Pretty Much History narrator` → `voice_id`.
- Озвучка: `voice.py eleven` (сделать) — по сегментам сценария, `POST /v1/text-to-speech/{voice_id}/with-timestamps`,
  модель `eleven_multilingual_v2`, `previous_text`/`next_text` для связности, время символов → время слов
  в `edl.json`. Дальше всё как с черновиком.
- Расход: ~1 кредит на знак (multilingual v2); серия ≈ 7 600 знаков.
- Ключ — `ELEVENLABS_API_KEY` из `remotion-skill/.env`, не печатать.
