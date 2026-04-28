# bot_4_wallpaper

Telegram-бот поиска и отправки обоев высокого разрешения через Wallhaven API.

## Стек

- Python 3.12 + aiogram 3.26
- PostgreSQL + SQLAlchemy 2.0
- httpx + Pillow
- Docker + docker-compose

## Быстрый старт

```bash
cp .env.example .env
# Заполнить .env: BOT_TOKEN, DB_PASSWORD, ADMIN_IDS

docker compose up -d --build
```

## Локальная разработка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Заполнить .env

python -m bot.main
```

## Структура

```
bot/
├── main.py            # точка входа
├── config.py          # настройки из .env
├── handlers/
│   ├── start.py       # /start, меню, профиль
│   ├── admin.py       # /admin
│   └── wallpaper.py   # поиск, случайные, избранное (TODO)
├── services/
│   └── wallhaven.py   # клиент Wallhaven API (TODO)
├── database/
│   ├── models.py      # User, Channel, WallpaperCache, Favorite, SearchRequest
│   └── crud.py        # CRUD функции
└── keyboards/
    ├── inline.py      # пользовательские клавиатуры
    └── admin.py       # клавиатуры администратора
```

## Конфигурация .env

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен от @BotFather |
| `WALLHAVEN_API_KEY` | API-ключ Wallhaven (опционально) |
| `DB_*` | Настройки PostgreSQL |
| `ADMIN_IDS` | Telegram ID админов через запятую |
| `DEFAULT_RESOLUTION` | Разрешение по умолчанию (`1920x1080`) |
