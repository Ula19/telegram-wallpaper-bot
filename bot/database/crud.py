"""CRUD операции с базой данных."""
import json
import logging
from datetime import datetime

from sqlalchemy import delete, func as sa_func, select, text as sa_text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    Channel,
    Favorite,
    SearchRequest,
    User,
    WallpaperCache,
)

logger = logging.getLogger(__name__)


# === Базовые функции (User / Channel) ===

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
    language: str | None = None,
) -> User:
    """Получить юзера или создать нового."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language=language or "ru",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    """Получить язык юзера (по умолчанию ru)."""
    result = await session.execute(
        select(User.language).where(User.telegram_id == telegram_id)
    )
    lang = result.scalar_one_or_none()
    return lang or "ru"


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    """Обновить язык юзера."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.language = language
        await session.commit()


async def update_user_resolution(
    session: AsyncSession, telegram_id: int, resolution: str
) -> None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.default_resolution = resolution
        await session.commit()


async def update_user_category(
    session: AsyncSession, telegram_id: int, category: str
) -> None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.default_category = category
        await session.commit()


async def increment_download_count(
    session: AsyncSession, telegram_id: int
) -> None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.download_count = (user.download_count or 0) + 1
        await session.commit()


async def get_active_channels(session: AsyncSession) -> list[Channel]:
    """Получить все каналы для обязательной подписки."""
    result = await session.execute(select(Channel))
    return list(result.scalars().all())


async def add_channel(
    session: AsyncSession,
    channel_id: int,
    title: str,
    invite_link: str,
) -> Channel:
    """Добавить канал."""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(f"Канал {channel_id} уже добавлен")

    channel = Channel(
        channel_id=channel_id,
        title=title,
        invite_link=invite_link,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    """Удалить канал. Возвращает True если удалён."""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return False

    await session.delete(channel)
    await session.commit()
    return True


async def get_user_stats(session: AsyncSession) -> dict:
    """Базовая статистика для админ-панели."""
    total = await session.execute(select(sa_func.count(User.id)))
    total_users = total.scalar() or 0

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(sa_func.count(User.id)).where(User.created_at >= today)
    )
    today_users = today_result.scalar() or 0

    downloads = await session.execute(
        select(sa_func.sum(User.download_count))
    )
    total_downloads = downloads.scalar() or 0

    channels = await session.execute(select(sa_func.count(Channel.id)))
    total_channels = channels.scalar() or 0

    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_downloads": total_downloads,
        "total_channels": total_channels,
    }


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    """Все telegram_id юзеров для рассылки."""
    result = await session.execute(select(User.telegram_id))
    return [row[0] for row in result.all()]


# === Wallpaper cache ===

async def get_or_create_wallpaper_cache(
    session: AsyncSession,
    wallhaven_id: str,
    *,
    thumb_url: str = "",
    full_url: str = "",
    resolution: str = "",
    category: str = "general",
) -> WallpaperCache:
    """Атомарно создать или обновить запись кэша (через INSERT ... ON CONFLICT).
    Заполняем только пустые поля при конфликте (CASE WHEN существующее пустое — берём новое).
    """
    stmt = pg_insert(WallpaperCache).values(
        wallhaven_id=wallhaven_id,
        thumb_url=thumb_url,
        full_url=full_url,
        resolution=resolution,
        category=category,
    )
    # обновляем поля только если в БД они пустые (чтобы не затереть useful данные)
    upd = {
        "thumb_url": sa_func.coalesce(
            sa_func.nullif(WallpaperCache.thumb_url, ""), stmt.excluded.thumb_url,
        ),
        "full_url": sa_func.coalesce(
            sa_func.nullif(WallpaperCache.full_url, ""), stmt.excluded.full_url,
        ),
        "resolution": sa_func.coalesce(
            sa_func.nullif(WallpaperCache.resolution, ""), stmt.excluded.resolution,
        ),
        "category": sa_func.coalesce(
            sa_func.nullif(WallpaperCache.category, ""), stmt.excluded.category,
        ),
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=[WallpaperCache.wallhaven_id], set_=upd,
    )
    await session.execute(stmt)
    await session.commit()

    # читаем актуальный объект
    result = await session.execute(
        select(WallpaperCache).where(WallpaperCache.wallhaven_id == wallhaven_id)
    )
    return result.scalar_one()


async def update_cache_file_id(
    session: AsyncSession,
    wallhaven_id: str,
    *,
    file_id_orig: str | None = None,
    resolution: str | None = None,
    file_id: str | None = None,
) -> None:
    """Обновить file_id оригинала или ресайзнутой версии (атомарно, через JSONB merge)."""
    if file_id_orig is not None:
        await session.execute(
            update(WallpaperCache)
            .where(WallpaperCache.wallhaven_id == wallhaven_id)
            .values(file_id_orig=file_id_orig)
        )

    if resolution and file_id:
        # JSONB merge на стороне Postgres. CAST вместо :patch::jsonb,
        # т.к. SQLAlchemy text() парсит `::` как часть named-параметра.
        await session.execute(
            sa_text(
                "UPDATE wallpaper_cache "
                "SET file_id_resized = COALESCE(file_id_resized, '{}'::jsonb) "
                "|| CAST(:patch AS jsonb) "
                "WHERE wallhaven_id = :wid"
            ),
            {"patch": json.dumps({resolution: file_id}), "wid": wallhaven_id},
        )

    await session.commit()


def cache_get_resized(cache: WallpaperCache, resolution: str) -> str | None:
    """Достать file_id для ресайзнутой версии (helper, без await)."""
    data = cache.file_id_resized or {}
    if isinstance(data, dict):
        return data.get(resolution)
    return None


# === Favorites ===

async def is_favorite(
    session: AsyncSession, user_id: int, wallhaven_id: str
) -> bool:
    result = await session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.wallhaven_id == wallhaven_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def toggle_favorite(
    session: AsyncSession, user_id: int, wallhaven_id: str
) -> bool:
    """Добавить/удалить из избранного. Возвращает True если теперь в избранном."""
    result = await session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.wallhaven_id == wallhaven_id,
        )
    )
    fav = result.scalar_one_or_none()
    if fav:
        await session.delete(fav)
        await session.commit()
        return False
    fav = Favorite(user_id=user_id, wallhaven_id=wallhaven_id)
    session.add(fav)
    await session.commit()
    return True


async def get_user_favorites(
    session: AsyncSession, user_id: int, page: int = 1, per_page: int = 10
) -> tuple[list[Favorite], int]:
    """Список избранного пользователя постранично + общее количество."""
    total_q = await session.execute(
        select(sa_func.count(Favorite.id)).where(Favorite.user_id == user_id)
    )
    total = total_q.scalar() or 0

    offset = (max(page, 1) - 1) * per_page
    result = await session.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.added_at.desc())
        .limit(per_page)
        .offset(offset)
    )
    return list(result.scalars().all()), total


# === Search log ===

async def log_search(
    session: AsyncSession, user_id: int, query: str, results_count: int
) -> None:
    session.add(SearchRequest(
        user_id=user_id, query=query[:500], results_count=results_count,
    ))
    await session.commit()


async def get_search_stats(session: AsyncSession) -> dict:
    """Расширенная статистика для /stats: топ-запросы, размер кэша, избранное."""
    base = await get_user_stats(session)

    total_searches_q = await session.execute(
        select(sa_func.count(SearchRequest.id))
    )
    total_searches = total_searches_q.scalar() or 0

    total_favorites_q = await session.execute(
        select(sa_func.count(Favorite.id))
    )
    total_favorites = total_favorites_q.scalar() or 0

    cache_size_q = await session.execute(
        select(sa_func.count(WallpaperCache.id))
    )
    cache_size = cache_size_q.scalar() or 0

    top_q = await session.execute(
        select(SearchRequest.query, sa_func.count(SearchRequest.id).label("c"))
        .group_by(SearchRequest.query)
        .order_by(sa_func.count(SearchRequest.id).desc())
        .limit(10)
    )
    top_queries = [(row[0], row[1]) for row in top_q.all()]

    return {
        **base,
        "total_searches": total_searches,
        "total_favorites": total_favorites,
        "cache_size": cache_size,
        "top_queries": top_queries,
    }


async def cleanup_old_data(session: AsyncSession, *,
                           cache_days: int = 60,
                           search_days: int = 90) -> dict:
    """Удаляет устаревшие записи кэша и истории поиска. Возвращает счётчики."""
    from datetime import timedelta
    now = datetime.utcnow()
    cache_cutoff = now - timedelta(days=cache_days)
    search_cutoff = now - timedelta(days=search_days)

    # WallpaperCache: запись старше cache_days без активного избранного
    fav_subq = select(Favorite.wallhaven_id).distinct().subquery()
    cache_q = await session.execute(
        delete(WallpaperCache).where(
            WallpaperCache.cached_at < cache_cutoff,
            WallpaperCache.wallhaven_id.notin_(select(fav_subq.c.wallhaven_id)),
        )
    )
    deleted_cache = cache_q.rowcount or 0

    # SearchRequest: вся история старше search_days
    sr_q = await session.execute(
        delete(SearchRequest).where(SearchRequest.created_at < search_cutoff)
    )
    deleted_searches = sr_q.rowcount or 0

    await session.commit()
    return {"cache": deleted_cache, "searches": deleted_searches}
