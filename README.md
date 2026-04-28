# bot_4_wallpaper

Telegram-бот для поиска и отправки HD-обоев через Wallhaven API.

## Возможности

- Поиск по тексту (на английском) — выдача 5 обоев пачкой с превью.
- «Подбор по фильтрам» — без запроса: категория (General / Anime / All), сортировка (релевантность / топ недели / новые / по просмотрам), минимальное разрешение (Any / ≥ FullHD / ≥ 4K).
- `/random` — случайные, `/top` — топ за неделю.
- `/categories` — 10 готовых тематик; у части (Природа, Космос, Аниме, Города, Игры) есть подкатегории.
- Избранное — добавление кнопкой под обоями, отдельный список через `/favorites`.
- Кнопки под каждым превью: **Скач.** (оригинал документом, > 20 МБ — авто-уменьшение до разрешения по умолчанию), **Разм.** (ресайз до выбранного разрешения через Pillow), **Избр.** (toggle).
- Inline-mode: `@bot query` — быстрый поиск из любого чата.
- Кэш Telegram `file_id` для оригинала и ресайзов — повторные запросы мгновенные.
- Мультиязычность: ru / uz / en, кнопка «Сменить язык».
- Обязательная подписка на каналы (настраивается в админке).
- Rate limit (5 поисков / минуту), throttled-уведомления админам при ошибках Wallhaven.
- Фоновая очистка: временные файлы, устаревший кэш в БД, история поиска.

## Стек

- Python 3.12 + aiogram 3.26
- PostgreSQL + SQLAlchemy 2.0 (asyncpg)
- httpx (Wallhaven API), Pillow (ресайз), aiofiles
- Docker + docker compose

## Быстрый старт

```bash
cp .env.example .env
# Заполнить: BOT_TOKEN, DB_PASSWORD, ADMIN_IDS, BOT_USERNAME, ADMIN_USERNAME
# Опционально: WALLHAVEN_API_KEY (повышает rate-limit и даёт доступ к sketchy/nsfw)

docker compose up -d --build
```

## Локальная разработка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
python -m bot.main
```

## Структура

```
bot/
├── main.py                  # точка входа, фоновая очистка
├── config.py                # настройки из .env
├── i18n.py                  # переводы ru/uz/en
├── emojis.py                # premium-эмодзи (E_ID + E)
├── handlers/
│   ├── start.py             # /start, меню, профиль, /help, смена языка, подписка
│   ├── admin.py             # /admin: статистика, каналы, рассылка, /stats
│   └── wallpaper.py         # /search /random /top /categories /favorites /settings + inline-mode
├── services/
│   └── wallhaven.py         # клиент Wallhaven API (retry, семафор, ресайз)
├── database/
│   ├── models.py            # User, Channel, WallpaperCache, Favorite, SearchRequest
│   └── crud.py              # CRUD + cleanup_old_data
├── keyboards/
│   ├── inline.py            # все клавиатуры пользователя
│   └── admin.py             # клавиатуры админки
├── middlewares/
│   ├── subscription.py      # проверка обязательной подписки
│   └── rate_limit.py        # 5 поисков / мин
└── utils/
    ├── commands.py          # меню команд Telegram (per-language)
    └── helpers.py           # is_search_request, детект кириллицы
```

## Команды

| Команда | Описание |
|---|---|
| `/start` | Запуск, главное меню |
| `/menu` | Главное меню |
| `/search <query>` | Поиск обоев |
| `/random` | Случайные обои |
| `/top` | Топ за неделю |
| `/categories` | 10 тематических категорий |
| `/favorites` | Избранные обои |
| `/settings` | Разрешение и категория по умолчанию |
| `/profile` | Профиль и счётчик скачиваний |
| `/help` | Справка |
| `/language` | Смена языка |
| `/admin`, `/stats` | Только для ADMIN_IDS |

## Конфигурация .env

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен от @BotFather |
| `BOT_USERNAME` | Юзернейм бота (для подписи и inline-mode) |
| `ADMIN_IDS` | Telegram ID админов через запятую |
| `ADMIN_USERNAME` | Контакт в /help |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL |
| `WALLHAVEN_API_KEY` | Опционально — глобальный ключ Wallhaven |
| `DEFAULT_RESOLUTION` | По умолчанию `1920x1080` |
| `LOCAL_BOT_API_URL` | Опционально — Local Bot API (по умолчанию `https://api.telegram.org`) |
