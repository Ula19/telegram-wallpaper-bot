"""Точка входа — запуск бота поиска обоев"""
import asyncio
import logging
import os
import sys
import time

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # на Windows — работаем без uvloop

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# флаг-файл для crash recovery
CRASH_FLAG = ".crash_flag"


async def main() -> None:
    """Инициализация и запуск бота"""
    # подключаемся к Local Bot API если указан URL
    session = None
    api_url = settings.local_bot_api_url
    if api_url != "https://api.telegram.org":
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(api_url, is_local=True),
            timeout=300  # 5 минут на запрос (обои обычно небольшие)
        )
        logger.info(f"Local Bot API: {api_url}")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен!)
    from bot.handlers import start, admin
    from bot.handlers import wallpaper  # TODO: заменить на реальный хендлер после реализации

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(wallpaper.router)  # последний — ловит все текстовые сообщения

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # события старта и остановки
    async def _background_cleanup() -> None:
        """Фоновая задача: очистка памяти, файлов downloads/, БД-кэша. Раз в 5 минут."""
        from bot.middlewares.rate_limit import cleanup_stale_entries
        from bot.database import async_session
        from bot.database.crud import cleanup_old_data
        downloads_dir = os.path.join(os.getcwd(), "downloads")
        # чистка БД делается реже — раз в час
        db_cleanup_every = 12  # 12 циклов × 5 мин = 1 час
        cycle = 0
        while True:
            await asyncio.sleep(300)  # 5 минут
            cycle += 1

            # 1) rate limit memory
            removed = cleanup_stale_entries()
            if removed:
                logger.info("Фоновая очистка: rate-limit -%d", removed)

            # 2) папка downloads — файлы старше 1 часа
            try:
                if os.path.isdir(downloads_dir):
                    cutoff = time.time() - 3600
                    deleted = 0
                    for name in os.listdir(downloads_dir):
                        path = os.path.join(downloads_dir, name)
                        try:
                            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                                os.unlink(path)
                                deleted += 1
                        except OSError:
                            pass
                    if deleted:
                        logger.info("Фоновая очистка: downloads/ -%d", deleted)
            except OSError as e:
                logger.warning("Не удалось почистить downloads/: %s", e)

            # 3) in-memory сессии поиска — старше 1 часа неактивности
            try:
                from bot.handlers.wallpaper import SEARCH_SESSIONS
                if len(SEARCH_SESSIONS) > 1000:
                    # просто полностью очищаем — это всего лишь параметры пагинации
                    cleared = len(SEARCH_SESSIONS)
                    SEARCH_SESSIONS.clear()
                    logger.info("Фоновая очистка: SEARCH_SESSIONS -%d", cleared)
            except Exception as e:
                logger.warning("Не удалось почистить SEARCH_SESSIONS: %s", e)

            # 4) БД: устаревший кэш и история поиска (раз в час)
            if cycle % db_cleanup_every == 0:
                try:
                    async with async_session() as s:
                        stats = await cleanup_old_data(s)
                    if stats["cache"] or stats["searches"]:
                        logger.info(
                            "Фоновая очистка БД: cache -%d, searches -%d",
                            stats["cache"], stats["searches"],
                        )
                except Exception as e:
                    logger.warning("cleanup_old_data failed: %s", e)

    @dp.startup()
    async def on_startup() -> None:
        # создаём таблицы в БД
        from bot.database import engine
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы БД созданы")

        # проверяем crash recovery
        if os.path.exists(CRASH_FLAG):
            logger.warning("Обнаружен crash-flag — предыдущий запуск завершился аварийно")
            os.remove(CRASH_FLAG)

        # ставим crash-flag (уберём при нормальном завершении)
        with open(CRASH_FLAG, "w") as f:
            f.write("running")

        # запускаем фоновую очистку
        asyncio.create_task(_background_cleanup())
        logger.info("Фоновая очистка запущена (интервал 5 мин)")

        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} запущен!")

        # ставим дефолтное меню команд (глобально, ru — для новых юзеров)
        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        # закрываем shared httpx-клиент Wallhaven
        try:
            from bot.services.wallhaven import wallhaven_service
            await wallhaven_service.close()
        except Exception as e:
            logger.warning("Не удалось закрыть wallhaven_service: %s", e)
        # убираем crash-flag при нормальном завершении
        if os.path.exists(CRASH_FLAG):
            os.remove(CRASH_FLAG)
        logger.info("Бот остановлен")

    # запускаем polling
    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
