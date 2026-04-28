"""Хэндлер обоев — поиск, /random, /top, /categories, /favorites, /settings + inline-mode."""
from __future__ import annotations

import asyncio
import logging
import re
import uuid
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    FSInputFile,
    InlineQuery,
    InlineQueryResultPhoto,
    InputMediaPhoto,
    Message,
)

from bot.config import settings
from bot.database import async_session
from bot.database.crud import (
    cache_get_resized,
    get_or_create_user,
    get_or_create_wallpaper_cache,
    get_user_favorites,
    get_user_language,
    increment_download_count,
    log_search,
    toggle_favorite,
    update_cache_file_id,
    update_user_category,
    update_user_resolution,
)
from bot.emojis import E
from bot.i18n import t
from bot.keyboards.inline import (
    get_back_keyboard,
    get_categories_keyboard,
    get_category_setting_keyboard,
    get_favorites_keyboard,
    get_resolution_keyboard,
    get_resolution_setting_keyboard,
    get_search_results_keyboard,
    get_settings_keyboard,
)
from bot.services.wallhaven import (
    WallhavenError,
    WallhavenRateLimit,
    wallhaven_service,
)
from bot.utils.helpers import is_search_request

logger = logging.getLogger(__name__)
router = Router()

# директория для временных файлов
DOWNLOADS = Path("downloads")
DOWNLOADS.mkdir(exist_ok=True)

# обои на страницу
PER_PAGE = 5

# регулярка для wallhaven_id: 1-16 alphanum символов
_WID_RE = re.compile(r"^[a-zA-Z0-9]{1,16}$")

# in-memory сессия поиска: chat_id → {query, categories, sorting, top_range}
SEARCH_SESSIONS: dict[int, dict] = {}

# rate-limit для алёртов админу: тип ошибки → unix-ts последнего уведомления
_ADMIN_NOTIFY_LAST: dict[str, float] = {}
_ADMIN_NOTIFY_INTERVAL = 300  # не чаще раза в 5 минут на ключ


async def _notify_admins_throttled(bot, message: str, key: str | None = None) -> None:
    """Отправить уведомление всем админам с rate-limit (1 раз в 5 минут на ключ)."""
    import time as _t
    from bot.config import settings as _settings
    k = key or message[:80]
    now = _t.time()
    last = _ADMIN_NOTIFY_LAST.get(k, 0)
    if now - last < _ADMIN_NOTIFY_INTERVAL:
        return
    _ADMIN_NOTIFY_LAST[k] = now
    text = f"{E['warning']} <b>Bot alert</b>\n<code>{message}</code>"
    for admin_id in _settings.admin_id_list:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception as e:
            logger.warning("notify admin %s failed: %s", admin_id, e)


def _valid_wid(wid: str) -> bool:
    """Проверяет формат wallhaven_id (защита от инъекций в callback_data)."""
    return bool(_WID_RE.match(wid or ""))


# ------------------------------------------------------------------ utilities

async def _get_lang(user_id: int) -> str:
    async with async_session() as session:
        return await get_user_language(session, user_id)


def _category_for_user(default_category: str) -> str:
    """user.default_category → wallhaven categories битмаска."""
    if default_category == "anime":
        return "010"
    if default_category == "people":
        return "001"
    if default_category == "both":
        return "110"
    return "100"


async def _safe_unlink(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError as e:
        logger.warning("не смог удалить %s: %s", path, e)


# ------------------------------------------------------------------ search

async def _send_search_results(
    bot,
    chat_id: int,
    user_lang: str,
    query: str,
    page: int,
    items: list[dict],
    *,
    categories: str = "111",
    sorting: str = "relevance",
    atleast: str | None = None,
) -> None:
    """Отправить media group + клавиатуру с действиями."""
    # wallhaven блокирует hotlinking full-size URL (Telegram получает 403/HTML),
    # поэтому скачиваем превью сами параллельно. Если файл > 5MB или wallhaven недоступен,
    # fallback на thumbs.original (защиту от hotlink не имеют).
    async def _fetch_preview(item: dict) -> bytes | str | None:
        size = item.get("file_size") or 0
        path = item.get("path")
        if 0 < size <= 5_000_000 and path:
            data = await wallhaven_service.fetch_bytes(path)
            if data:
                return data
        thumbs = item.get("thumbs", {})
        return thumbs.get("original") or thumbs.get("large")

    previews = await asyncio.gather(*(_fetch_preview(it) for it in items))

    promo = t("wallpaper.promo", user_lang, bot_username=settings.bot_username)
    media = []
    for idx, (item, preview) in enumerate(zip(items, previews), 1):
        if not preview:
            continue
        caption = (
            f"<b>{idx}.</b> {item.get('resolution', '')} "
            f"• {item.get('category', '').capitalize()} "
            f"• {E['star']} {item.get('favorites', 0)}"
            f"{promo}"
        )
        if isinstance(preview, bytes):
            file = BufferedInputFile(preview, filename=f"wp_{item.get('id', idx)}.jpg")
            media.append(InputMediaPhoto(media=file, caption=caption, parse_mode="HTML"))
        else:
            media.append(InputMediaPhoto(media=preview, caption=caption, parse_mode="HTML"))

    try:
        await bot.send_media_group(chat_id=chat_id, media=media)
    except TelegramBadRequest as e:
        logger.warning("send_media_group failed: %s, fallback к одиночным фото", e)
        for m in media:
            try:
                await bot.send_photo(chat_id=chat_id, photo=m.media, caption=m.caption,
                                     parse_mode="HTML")
            except TelegramBadRequest as ee:
                logger.warning("send_photo failed: %s", ee)

    header = t("wallpaper.search_results_header", user_lang, query=query, page=page)
    await bot.send_message(
        chat_id=chat_id,
        text=header,
        reply_markup=get_search_results_keyboard(
            items, query, page, user_lang, chat_id=chat_id,
            categories=categories, sorting=sorting, atleast=atleast,
        ),
        parse_mode="HTML",
    )


async def _do_search(
    message_or_chat_id,
    bot,
    user_id: int,
    query: str,
    page: int = 1,
    *,
    categories: str | None = None,
    sorting: str = "relevance",
    top_range: str | None = None,
    atleast: str | None = None,
) -> None:
    """Общая логика поиска. Используется и из команд, и из callback."""
    chat_id = message_or_chat_id if isinstance(message_or_chat_id, int) else message_or_chat_id.chat.id

    async with async_session() as session:
        user = await get_or_create_user(
            session=session, telegram_id=user_id,
            username=None, full_name="",
        )
        lang = user.language or "ru"
        user_cats = categories or _category_for_user(user.default_category)
        api_key = user.wallhaven_api_key

    svc = wallhaven_service
    # если у юзера свой ключ — создаём временный сервис на его ключе
    if api_key:
        from bot.services.wallhaven import WallhavenService
        svc = WallhavenService(api_key=api_key)

    # сохраняем параметры сессии поиска (для пагинации без потери categories)
    SEARCH_SESSIONS[chat_id] = {
        "query": query,
        "categories": user_cats,
        "sorting": sorting,
        "top_range": top_range,
        "atleast": atleast,
    }

    # Wallhaven не индексирует кириллицу — предупредим заранее
    if query and re.search(r"[Ѐ-ӿ]", query):
        try:
            await bot.send_message(chat_id, t("wallpaper.cyrillic_hint", lang),
                                   parse_mode="HTML")
        except TelegramBadRequest:
            pass

    # статусное сообщение "ищем обои…" — удалим перед выдачей или при ошибке
    status_msg = None
    try:
        status_msg = await bot.send_message(chat_id, t("wallpaper.searching", lang),
                                            parse_mode="HTML")
    except TelegramBadRequest:
        pass

    async def _drop_status():
        if status_msg is None:
            return
        try:
            await status_msg.delete()
        except TelegramBadRequest:
            pass

    try:
        data = await svc.search(
            query=query,
            page=page,
            categories=user_cats,
            purity="100",
            sorting=sorting,
            top_range=top_range,
            atleast=atleast,
        )
    except WallhavenRateLimit:
        await _drop_status()
        await _notify_admins_throttled(bot, "Wallhaven rate limit", key="rate_limit")
        await bot.send_message(chat_id, t("wallpaper.rate_limited", lang))
        return
    except WallhavenError as e:
        await _drop_status()
        logger.error("Wallhaven search error: %s", e)
        await _notify_admins_throttled(bot, f"Wallhaven search error: {e}", key="search_error")
        await bot.send_message(chat_id, t("wallpaper.search_error", lang))
        return

    items = data.get("data", [])[:PER_PAGE]

    async with async_session() as session:
        await log_search(session, user_id, query, len(items))

    if not items:
        await _drop_status()
        await bot.send_message(chat_id, t("wallpaper.no_results", lang))
        return

    # сохраняем кэш по каждому
    async with async_session() as session:
        for it in items:
            await get_or_create_wallpaper_cache(
                session,
                wallhaven_id=it["id"],
                thumb_url=it.get("thumbs", {}).get("large", ""),
                full_url=it.get("path", ""),
                resolution=it.get("resolution", ""),
                category=it.get("category", "general"),
            )

    await _drop_status()
    await _send_search_results(
        bot, chat_id, lang, query, page, items,
        categories=user_cats, sorting=sorting, atleast=atleast,
    )


# ------------------------------------------------------------------ commands

@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext) -> None:
    """/search <query> — поиск обоев."""
    await state.clear()
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        lang = await _get_lang(message.from_user.id)
        await message.answer(t("wallpaper.search_prompt", lang), parse_mode="HTML")
        return
    await _do_search(message, message.bot, message.from_user.id, parts[1].strip())


@router.callback_query(F.data == "wallpaper_search")
async def wallpaper_search_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    """Кнопка 'Найти обои' — попросить ввести запрос."""
    await state.clear()
    lang = await _get_lang(callback.from_user.id)
    await callback.message.answer(t("wallpaper.search_prompt", lang), parse_mode="HTML")
    await callback.answer()


async def _send_random(bot, chat_id: int, user_id: int) -> None:
    """Общая логика для /random и кнопки 'Случайные обои'."""
    lang = await _get_lang(user_id)
    try:
        items = await wallhaven_service.get_random()
    except WallhavenRateLimit:
        await _notify_admins_throttled(bot, "Wallhaven rate limit", key="rate_limit")
        await bot.send_message(chat_id, t("wallpaper.rate_limited", lang))
        return
    except WallhavenError as e:
        logger.error("get_random: %s", e)
        await _notify_admins_throttled(bot, f"Wallhaven random error: {e}", key="random_error")
        await bot.send_message(chat_id, t("wallpaper.search_error", lang))
        return

    items = items[:PER_PAGE]
    if not items:
        await bot.send_message(chat_id, t("wallpaper.no_results", lang))
        return

    async with async_session() as session:
        for it in items:
            await get_or_create_wallpaper_cache(
                session, wallhaven_id=it["id"],
                thumb_url=it.get("thumbs", {}).get("large", ""),
                full_url=it.get("path", ""),
                resolution=it.get("resolution", ""),
                category=it.get("category", "general"),
            )

    SEARCH_SESSIONS[chat_id] = {
        "query": "", "categories": "111", "sorting": "random", "top_range": None,
    }
    await bot.send_message(chat_id, t("wallpaper.random_header", lang), parse_mode="HTML")
    await _send_search_results(bot, chat_id, lang, "random", 1, items)


async def _send_top(bot, chat_id: int, user_id: int) -> None:
    """Общая логика для /top и кнопки 'Топ'."""
    lang = await _get_lang(user_id)
    try:
        items = await wallhaven_service.get_top(top_range="1w")
    except WallhavenRateLimit:
        await _notify_admins_throttled(bot, "Wallhaven rate limit", key="rate_limit")
        await bot.send_message(chat_id, t("wallpaper.rate_limited", lang))
        return
    except WallhavenError as e:
        logger.error("get_top: %s", e)
        await _notify_admins_throttled(bot, f"Wallhaven top error: {e}", key="top_error")
        await bot.send_message(chat_id, t("wallpaper.search_error", lang))
        return

    items = items[:PER_PAGE]
    if not items:
        await bot.send_message(chat_id, t("wallpaper.no_results", lang))
        return

    async with async_session() as session:
        for it in items:
            await get_or_create_wallpaper_cache(
                session, wallhaven_id=it["id"],
                thumb_url=it.get("thumbs", {}).get("large", ""),
                full_url=it.get("path", ""),
                resolution=it.get("resolution", ""),
                category=it.get("category", "general"),
            )

    SEARCH_SESSIONS[chat_id] = {
        "query": "", "categories": "111", "sorting": "toplist", "top_range": "1w",
    }
    await bot.send_message(chat_id, t("wallpaper.top_header", lang), parse_mode="HTML")
    await _send_search_results(bot, chat_id, lang, "top", 1, items)


@router.message(Command("random"))
async def cmd_random(message: Message) -> None:
    """5 случайных обоев."""
    await _send_random(message.bot, message.chat.id, message.from_user.id)


@router.callback_query(F.data == "wallpaper_random")
async def wallpaper_random_cb(callback: CallbackQuery) -> None:
    """Кнопка 'Случайные обои'."""
    await callback.answer()
    await _send_random(callback.bot, callback.message.chat.id, callback.from_user.id)


@router.message(Command("top"))
async def cmd_top(message: Message) -> None:
    """Топ обоев за неделю."""
    await _send_top(message.bot, message.chat.id, message.from_user.id)


@router.message(Command("categories"))
async def cmd_categories(message: Message) -> None:
    lang = await _get_lang(message.from_user.id)
    await message.answer(
        t("wallpaper.categories_header", lang),
        reply_markup=get_categories_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("wp:cat:"))
async def cb_category_pick(callback: CallbackQuery) -> None:
    """wp:cat:<query>:<categories>"""
    _, _, query, cats = callback.data.split(":", 3)
    await callback.answer()
    await _do_search(
        callback.message, callback.bot, callback.from_user.id,
        query, page=1, categories=cats,
    )


@router.callback_query(F.data.startswith("wp:tree:"))
async def cb_category_tree(callback: CallbackQuery) -> None:
    """wp:tree:<slug> — раскрыть подкатегории."""
    from bot.keyboards.inline import get_subcategories_keyboard
    _, _, slug = callback.data.split(":", 2)
    lang = await _get_lang(callback.from_user.id)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_subcategories_keyboard(slug, lang),
        )
    except TelegramBadRequest:
        await callback.message.answer(
            t("wallpaper.categories_header", lang),
            reply_markup=get_subcategories_keyboard(slug, lang),
            parse_mode="HTML",
        )
    await callback.answer()


# ------------------------------------------------------------------ pagination

@router.callback_query(F.data.startswith("wp:page:"))
async def cb_search_page(callback: CallbackQuery) -> None:
    """wp:page:<chat_id>:<n> — параметры поиска берём из SEARCH_SESSIONS."""
    try:
        _, _, chat_id_s, page = callback.data.split(":", 3)
        page = max(1, int(page))
    except ValueError:
        await callback.answer()
        return

    chat_id = callback.message.chat.id
    sess = SEARCH_SESSIONS.get(chat_id)
    if not sess:
        # сессия истекла — просим повторить запрос
        lang = await _get_lang(callback.from_user.id)
        await callback.answer()
        await callback.bot.send_message(chat_id, t("wallpaper.search_prompt", lang),
                                        parse_mode="HTML")
        return

    await callback.answer()
    await _do_search(
        callback.message, callback.bot, callback.from_user.id,
        sess["query"], page=page,
        categories=sess.get("categories"),
        sorting=sess.get("sorting", "relevance"),
        top_range=sess.get("top_range"),
        atleast=sess.get("atleast"),
    )


@router.callback_query(F.data == "wallpaper_discover")
async def cb_discover(callback: CallbackQuery) -> None:
    """Открыть меню подбора по фильтрам (без текстового запроса)."""
    from bot.keyboards.inline import get_search_filters_keyboard
    chat_id = callback.message.chat.id
    lang = await _get_lang(callback.from_user.id)
    sess = SEARCH_SESSIONS.setdefault(chat_id, {
        "query": "", "categories": "111",
        "sorting": "toplist", "top_range": "1w", "atleast": None,
    })
    await callback.answer()
    await callback.bot.send_message(
        chat_id, t("wallpaper.discover_header", lang),
        reply_markup=get_search_filters_keyboard(
            lang,
            categories=sess.get("categories", "111"),
            sorting=sess.get("sorting", "toplist"),
            atleast=sess.get("atleast"),
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "wp:filters_close")
async def cb_close_filters(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(F.data == "wp:filters_run")
async def cb_filters_run(callback: CallbackQuery) -> None:
    """Запустить поиск с текущими фильтрами (без текстового запроса)."""
    chat_id = callback.message.chat.id
    sess = SEARCH_SESSIONS.get(chat_id)
    if not sess:
        await callback.answer()
        return
    await callback.answer()
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await _do_search(
        callback.message, callback.bot, callback.from_user.id,
        sess.get("query", ""), page=1,
        categories=sess.get("categories"),
        sorting=sess.get("sorting", "toplist"),
        top_range=sess.get("top_range", "1w"),
        atleast=sess.get("atleast"),
    )


@router.callback_query(F.data.startswith("wp:f:"))
async def cb_search_filter(callback: CallbackQuery) -> None:
    """wp:f:cat:<bm> | wp:f:sort:<s> | wp:f:res:<r|any> — обновляет SEARCH_SESSIONS и перерисовывает меню."""
    from bot.keyboards.inline import get_search_filters_keyboard
    try:
        _, _, kind, value = callback.data.split(":", 3)
    except ValueError:
        await callback.answer()
        return

    chat_id = callback.message.chat.id
    sess = SEARCH_SESSIONS.get(chat_id)
    if not sess:
        await callback.answer()
        return
    lang = await _get_lang(callback.from_user.id)

    if kind == "cat" and value in ("100", "010", "111"):
        sess["categories"] = value
    elif kind == "sort" and value in ("relevance", "toplist", "date_added", "views"):
        sess["sorting"] = value
        sess["top_range"] = "1w" if value == "toplist" else None
    elif kind == "res":
        sess["atleast"] = None if value == "any" else value
    else:
        await callback.answer()
        return

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_search_filters_keyboard(
                lang,
                categories=sess.get("categories", "111"),
                sorting=sess.get("sorting", "relevance"),
                atleast=sess.get("atleast"),
            ),
        )
    except TelegramBadRequest:
        pass
    await callback.answer()


# ------------------------------------------------------------------ download / resize

TG_DOC_LIMIT = 20 * 1024 * 1024  # 20 MB — лимит обычного Bot API


async def _send_original(
    bot, chat_id: int, user_id: int, wallhaven_id: str, lang: str
) -> None:
    """Скачать (или взять file_id из кэша) и отправить как document.
    Если файл > 20 MB — автоматически ресайзим до user.default_resolution и шлём как photo."""
    async with async_session() as session:
        cache = await get_or_create_wallpaper_cache(session, wallhaven_id)

    promo = t("wallpaper.promo", lang, bot_username=settings.bot_username)
    # уже отправляли? — file_id
    if cache.file_id_orig:
        try:
            await bot.send_document(
                chat_id, cache.file_id_orig,
                caption=t("wallpaper.downloaded", lang) + promo,
            )
            async with async_session() as session:
                await increment_download_count(session, user_id)
            return
        except TelegramBadRequest as e:
            logger.warning("file_id_orig устарел: %s", e)

    # нет URL? тогда тянем детали
    if not cache.full_url:
        details = await wallhaven_service.get_wallpaper(wallhaven_id)
        if not details:
            await bot.send_message(chat_id, t("wallpaper.search_error", lang))
            return
        async with async_session() as session:
            cache = await get_or_create_wallpaper_cache(
                session, wallhaven_id,
                thumb_url=details.get("thumbs", {}).get("large", ""),
                full_url=details.get("path", ""),
                resolution=details.get("resolution", ""),
                category=details.get("category", "general"),
            )

    await bot.send_message(chat_id, t("wallpaper.downloading", lang))

    suffix = Path(cache.full_url).suffix or ".jpg"
    tmp = DOWNLOADS / f"{wallhaven_id}_{uuid.uuid4().hex}{suffix}"
    resized: Path | None = None
    try:
        await wallhaven_service.download_image(cache.full_url, tmp)
        size = tmp.stat().st_size

        if size <= TG_DOC_LIMIT:
            sent = await bot.send_document(
                chat_id, FSInputFile(str(tmp)),
                caption=t("wallpaper.downloaded", lang) + promo,
            )
            if sent.document:
                async with async_session() as session:
                    await update_cache_file_id(
                        session, wallhaven_id, file_id_orig=sent.document.file_id,
                    )
                    await increment_download_count(session, user_id)
        else:
            # > 20 MB — режем до дефолтного разрешения юзера, шлём как photo
            async with async_session() as session:
                user = await get_or_create_user(
                    session=session, telegram_id=user_id,
                    username=None, full_name="",
                )
                target_res = user.default_resolution or "1920x1080"
            resized = await wallhaven_service.resize_image(tmp, target_res)
            sent = await bot.send_photo(
                chat_id, FSInputFile(str(resized)),
                caption=t("wallpaper.downsized", lang, resolution=target_res) + promo,
            )
            if sent.photo:
                file_id = sent.photo[-1].file_id
                async with async_session() as session:
                    await update_cache_file_id(
                        session, wallhaven_id,
                        resolution=target_res, file_id=file_id,
                    )
                    await increment_download_count(session, user_id)
    except WallhavenError as e:
        logger.error("download_original failed: %s", e)
        await _notify_admins_throttled(bot, f"Wallhaven download error: {e}")
        await bot.send_message(chat_id, t("wallpaper.search_error", lang))
    finally:
        await _safe_unlink(tmp)
        if resized:
            await _safe_unlink(resized)


@router.callback_query(F.data.startswith("wp:dl:"))
async def cb_download(callback: CallbackQuery) -> None:
    wallhaven_id = callback.data.split(":", 2)[2]
    if not _valid_wid(wallhaven_id):
        await callback.answer()
        return
    lang = await _get_lang(callback.from_user.id)
    await callback.answer(t("wallpaper.downloading", lang))
    await _send_original(callback.bot, callback.message.chat.id,
                         callback.from_user.id, wallhaven_id, lang)


@router.callback_query(F.data.startswith("wp:rsz:"))
async def cb_resize_choose(callback: CallbackQuery) -> None:
    """Показать клавиатуру выбора разрешения."""
    wallhaven_id = callback.data.split(":", 2)[2]
    if not _valid_wid(wallhaven_id):
        await callback.answer()
        return
    lang = await _get_lang(callback.from_user.id)
    await callback.message.answer(
        t("wallpaper.resize_choose", lang),
        reply_markup=get_resolution_keyboard(wallhaven_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("wp:res:"))
async def cb_resize_apply(callback: CallbackQuery) -> None:
    """wp:res:<wallhaven_id>:<resolution>"""
    try:
        _, _, wallhaven_id, resolution = callback.data.split(":", 3)
    except ValueError:
        await callback.answer()
        return
    if not _valid_wid(wallhaven_id):
        await callback.answer()
        return

    lang = await _get_lang(callback.from_user.id)
    await callback.answer(t("wallpaper.downloading", lang))
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    async with async_session() as session:
        cache = await get_or_create_wallpaper_cache(session, wallhaven_id)

    promo = t("wallpaper.promo", lang, bot_username=settings.bot_username)
    cached_fid = cache_get_resized(cache, resolution)
    if cached_fid:
        try:
            await callback.bot.send_photo(
                chat_id, cached_fid,
                caption=t("wallpaper.resize_done", lang, resolution=resolution) + promo,
            )
            return
        except TelegramBadRequest as e:
            logger.warning("file_id resized устарел: %s", e)

    # подтягиваем детали если нет URL
    if not cache.full_url:
        details = await wallhaven_service.get_wallpaper(wallhaven_id)
        if not details:
            await callback.bot.send_message(chat_id, t("wallpaper.search_error", lang))
            return
        async with async_session() as session:
            cache = await get_or_create_wallpaper_cache(
                session, wallhaven_id,
                thumb_url=details.get("thumbs", {}).get("large", ""),
                full_url=details.get("path", ""),
                resolution=details.get("resolution", ""),
                category=details.get("category", "general"),
            )

    suffix = Path(cache.full_url).suffix or ".jpg"
    src = DOWNLOADS / f"{wallhaven_id}_{uuid.uuid4().hex}{suffix}"
    resized: Path | None = None
    try:
        await wallhaven_service.download_image(cache.full_url, src)
        resized = await wallhaven_service.resize_image(src, resolution)
        sent = await callback.bot.send_photo(
            chat_id, FSInputFile(str(resized)),
            caption=t("wallpaper.resize_done", lang, resolution=resolution) + promo,
        )
        if sent.photo:
            file_id = sent.photo[-1].file_id
            async with async_session() as session:
                await update_cache_file_id(
                    session, wallhaven_id,
                    resolution=resolution, file_id=file_id,
                )
                await increment_download_count(session, user_id)
    except WallhavenError as e:
        logger.error("resize_apply failed: %s", e)
        await _notify_admins_throttled(callback.bot, f"Wallhaven resize error: {e}", key="resize_error")
        await callback.bot.send_message(chat_id, t("wallpaper.search_error", lang))
    finally:
        await _safe_unlink(src)
        if resized:
            await _safe_unlink(resized)


# ------------------------------------------------------------------ favorites

@router.callback_query(F.data.startswith("wp:fav:"))
async def cb_toggle_fav(callback: CallbackQuery) -> None:
    wallhaven_id = callback.data.split(":", 2)[2]
    if not _valid_wid(wallhaven_id):
        await callback.answer()
        return
    lang = await _get_lang(callback.from_user.id)
    async with async_session() as session:
        now_fav = await toggle_favorite(session, callback.from_user.id, wallhaven_id)
    await callback.answer(
        t("wallpaper.fav_added" if now_fav else "wallpaper.fav_removed", lang),
        show_alert=False,
    )


@router.message(Command("favorites"))
async def cmd_favorites(message: Message) -> None:
    await _show_favorites(message.bot, message.chat.id, message.from_user.id, page=1)


@router.callback_query(F.data == "wallpaper_favorites")
async def cb_favorites(callback: CallbackQuery) -> None:
    await callback.answer()
    await _show_favorites(callback.bot, callback.message.chat.id, callback.from_user.id, page=1)


@router.callback_query(F.data.startswith("wp:favpage:"))
async def cb_favorites_page(callback: CallbackQuery) -> None:
    try:
        page = int(callback.data.split(":", 2)[2])
    except ValueError:
        await callback.answer()
        return
    await callback.answer()
    await _show_favorites(callback.bot, callback.message.chat.id,
                          callback.from_user.id, page=page)


async def _show_favorites(bot, chat_id: int, user_id: int, page: int = 1) -> None:
    lang = await _get_lang(user_id)
    per_page = 5
    async with async_session() as session:
        favs, total = await get_user_favorites(session, user_id, page=page, per_page=per_page)

    if not favs:
        await bot.send_message(chat_id, t("wallpaper.fav_empty", lang),
                               parse_mode="HTML",
                               reply_markup=get_back_keyboard(lang))
        return

    total_pages = max(1, (total + per_page - 1) // per_page)

    # 1) сначала достаём кэш для всех favs одним проходом
    async def _load_cache(fav):
        async with async_session() as session:
            return await get_or_create_wallpaper_cache(session, fav.wallhaven_id)

    caches = await asyncio.gather(*(_load_cache(f) for f in favs))

    # 2) для тех, у кого нет thumb — параллельно тянем детали с Wallhaven
    async def _maybe_fetch(fav, cache):
        thumb = cache.thumb_url or cache.full_url
        if thumb:
            return cache, thumb
        details = await wallhaven_service.get_wallpaper(fav.wallhaven_id)
        if not details:
            return cache, ""
        thumb = details.get("thumbs", {}).get("large", "")
        async with async_session() as session:
            cache = await get_or_create_wallpaper_cache(
                session, fav.wallhaven_id,
                thumb_url=thumb,
                full_url=details.get("path", ""),
                resolution=details.get("resolution", ""),
                category=details.get("category", "general"),
            )
        return cache, thumb

    enriched = await asyncio.gather(
        *(_maybe_fetch(f, c) for f, c in zip(favs, caches))
    )

    # медиа-группа из миниатюр
    promo = t("wallpaper.promo", lang, bot_username=settings.bot_username)
    media = []
    for idx, (cache, thumb) in enumerate(enriched, 1):
        if thumb:
            media.append(InputMediaPhoto(
                media=thumb,
                caption=f"<b>{idx}.</b> {cache.resolution or ''}{promo}",
                parse_mode="HTML",
            ))

    if media:
        try:
            await bot.send_media_group(chat_id=chat_id, media=media)
        except TelegramBadRequest as e:
            logger.warning("favorites media_group: %s", e)

    await bot.send_message(
        chat_id,
        t("wallpaper.fav_list_header", lang,
          page=page, total_pages=total_pages, total=total),
        reply_markup=get_favorites_keyboard(favs, page, total_pages, lang),
        parse_mode="HTML",
    )


# ------------------------------------------------------------------ settings

@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    await _show_settings(message.bot, message.chat.id, message.from_user.id)


async def _show_settings(bot, chat_id: int, user_id: int, edit_message=None) -> None:
    async with async_session() as session:
        user = await get_or_create_user(
            session=session, telegram_id=user_id,
            username=None, full_name="",
        )
    lang = user.language or "ru"
    cat_key = {"general": "cat.general", "anime": "cat.anime",
               "both": "cat.both"}.get(user.default_category, "cat.general")
    text = t(
        "wallpaper.settings_header", lang,
        resolution=user.default_resolution,
        category=t(cat_key, lang),
    )
    kb = get_settings_keyboard(user, lang)
    if edit_message:
        try:
            await edit_message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            return
        except TelegramBadRequest:
            pass
    await bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "wp:settings")
async def cb_settings(callback: CallbackQuery) -> None:
    await callback.answer()
    await _show_settings(callback.bot, callback.message.chat.id,
                         callback.from_user.id, edit_message=callback.message)


@router.callback_query(F.data == "wp:set:res")
async def cb_set_resolution_menu(callback: CallbackQuery) -> None:
    lang = await _get_lang(callback.from_user.id)
    try:
        await callback.message.edit_text(
            t("wallpaper.settings_resolution", lang),
            reply_markup=get_resolution_setting_keyboard(lang),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        await callback.message.answer(
            t("wallpaper.settings_resolution", lang),
            reply_markup=get_resolution_setting_keyboard(lang),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("wp:setres:"))
async def cb_set_resolution_apply(callback: CallbackQuery) -> None:
    res = callback.data.split(":", 2)[2]
    async with async_session() as session:
        await update_user_resolution(session, callback.from_user.id, res)
    await callback.answer(f"{E['check']} {res}")
    await _show_settings(callback.bot, callback.message.chat.id,
                         callback.from_user.id, edit_message=callback.message)


@router.callback_query(F.data == "wp:set:cat")
async def cb_set_category_menu(callback: CallbackQuery) -> None:
    lang = await _get_lang(callback.from_user.id)
    try:
        await callback.message.edit_text(
            t("wallpaper.settings_category", lang),
            reply_markup=get_category_setting_keyboard(lang),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        await callback.message.answer(
            t("wallpaper.settings_category", lang),
            reply_markup=get_category_setting_keyboard(lang),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("wp:setcat:"))
async def cb_set_category_apply(callback: CallbackQuery) -> None:
    cat = callback.data.split(":", 2)[2]
    if cat not in ("general", "anime", "people", "both"):
        await callback.answer()
        return
    async with async_session() as session:
        await update_user_category(session, callback.from_user.id, cat)
    await callback.answer(f"{E['check']} {cat}")
    await _show_settings(callback.bot, callback.message.chat.id,
                         callback.from_user.id, edit_message=callback.message)


# ------------------------------------------------------------------ inline mode

@router.inline_query()
async def inline_search(inline_query: InlineQuery) -> None:
    """Inline-mode: @bot <query> → InlineQueryResultPhoto."""
    query = (inline_query.query or "").strip()
    if not query or len(query) < 2:
        await inline_query.answer([], cache_time=10, is_personal=True)
        return

    try:
        data = await wallhaven_service.search(
            query=query, categories="111", purity="100", sorting="relevance",
        )
    except (WallhavenError, WallhavenRateLimit) as e:
        logger.warning("inline search error: %s", e)
        await _notify_admins_throttled(inline_query.bot, f"Wallhaven inline error: {e}", key="inline_error")
        await inline_query.answer([], cache_time=10, is_personal=True)
        return

    items = data.get("data", [])[:10]
    results = []
    for it in items:
        thumbs = it.get("thumbs", {})
        # photo_url не может быть оригиналом (Telegram-лимит 5MB) — берём original/large превью
        photo_url = thumbs.get("original") or thumbs.get("large")
        thumb_url = thumbs.get("small") or thumbs.get("large")
        if not photo_url or not thumb_url:
            continue
        results.append(InlineQueryResultPhoto(
            id=str(it["id"])[:64],
            photo_url=photo_url,
            thumbnail_url=thumb_url,
            photo_width=it.get("dimension_x") or 1920,
            photo_height=it.get("dimension_y") or 1080,
            caption=f"{it.get('resolution', '')} • Wallhaven",
        ))

    await inline_query.answer(results, cache_time=300, is_personal=False)


# ------------------------------------------------------------------ catch-all text

@router.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def cmd_text_search(message: Message, state: FSMContext) -> None:
    """Любой текст без / трактуется как поисковый запрос (минимум 3 символа)."""
    text = (message.text or "").strip()
    if len(text) < 3:
        return
    if not is_search_request(text):
        return
    await state.clear()
    await _do_search(message, message.bot, message.from_user.id, text)
