"""Inline-клавиатуры — главное меню, подписка, язык + TODO wallpaper"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import settings
from bot.emojis import E_ID
from bot.i18n import t


def get_start_keyboard(user_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню бота"""
    buttons = [
        [InlineKeyboardButton(
            text=t("btn.search", lang),
            callback_data="wallpaper_search",
            style="primary",
            icon_custom_emoji_id=E_ID["search"],
        )],
        [InlineKeyboardButton(
            text=t("btn.discover", lang),
            callback_data="wallpaper_discover",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )],
        [
            InlineKeyboardButton(
                text=t("btn.random", lang),
                callback_data="wallpaper_random",
                style="primary",
                icon_custom_emoji_id=E_ID["refresh"],
            ),
            InlineKeyboardButton(
                text=t("btn.favorites", lang),
                callback_data="wallpaper_favorites",
                style="success",
                icon_custom_emoji_id=E_ID["star"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.profile", lang),
                callback_data="my_profile",
                style="success",
                icon_custom_emoji_id=E_ID["profile"],
            ),
            InlineKeyboardButton(
                text=t("btn.help", lang),
                callback_data="my_help",
                style="success",
                icon_custom_emoji_id=E_ID["info"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.language", lang),
            callback_data="change_language",
            style="success",
            icon_custom_emoji_id=E_ID["gear"],
        )],
    ]

    # кнопка админки для админов
    if user_id in settings.admin_id_list:
        buttons.append([InlineKeyboardButton(
            text=t("btn.admin_panel", lang),
            callback_data="admin_panel",
            style="danger",
            icon_custom_emoji_id=E_ID["lock"],
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_subscription_keyboard(
    channels: list[dict], lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Клавиатура подписки на каналы"""
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"{ch['title']}",
            url=ch["invite_link"],
            style="primary",
            icon_custom_emoji_id=E_ID["megaphone"],
        )])
    buttons.append([InlineKeyboardButton(
        text=t("btn.check_sub", lang),
        callback_data="check_subscription",
        style="success",
        icon_custom_emoji_id=E_ID["check"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Русский",
                callback_data="set_lang_ru",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_ru"],
            ),
            InlineKeyboardButton(
                text="O'zbek",
                callback_data="set_lang_uz",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_uz"],
            ),
            InlineKeyboardButton(
                text="English",
                callback_data="set_lang_en",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_gb"],
            ),
        ],
    ])


# === Wallpaper клавиатуры ===

# 10 категорий с привязкой к wallhaven categories битмаске
CATEGORY_BUTTONS = [
    # (i18n-key, slug, query, categories битмаска, has_subcats)
    ("cat.nature",   "nature",  "nature",     "100", True),
    ("cat.space",    "space",   "space",      "100", True),
    ("cat.anime",    "anime",   "anime",      "010", True),
    ("cat.cars",     "cars",    "cars",       "100", False),
    ("cat.city",     "city",    "city",       "100", True),
    ("cat.minimal",  "minimal", "minimalism", "100", False),
    ("cat.abstract", "abstr",   "abstract",   "100", False),
    ("cat.gaming",   "gaming",  "gaming",     "100", True),
    ("cat.girls",    "girls",   "girl",       "001", False),
    ("cat.tech",     "tech",    "technology", "100", False),
]

# Подкатегории — slug → list[(i18n-key, query, categories)].
SUBCATEGORIES = {
    "nature": [
        ("sub.mountains", "mountains",   "100"),
        ("sub.sea",       "sea ocean",   "100"),
        ("sub.forest",    "forest",      "100"),
        ("sub.sunset",    "sunset",      "100"),
        ("sub.waterfall", "waterfall",   "100"),
        ("sub.winter",    "winter snow", "100"),
    ],
    "space": [
        ("sub.galaxy",   "galaxy",  "100"),
        ("sub.planets",  "planet",  "100"),
        ("sub.nebula",   "nebula",  "100"),
        ("sub.stars",    "stars",   "100"),
    ],
    "anime": [
        ("sub.anime_girl",     "anime girl",     "010"),
        ("sub.anime_landscape", "anime landscape", "010"),
        ("sub.anime_dark",     "anime dark",     "010"),
        ("sub.anime_school",   "anime school",   "010"),
    ],
    "city": [
        ("sub.skyline",   "skyline",   "100"),
        ("sub.cyberpunk", "cyberpunk", "100"),
        ("sub.night",     "night city", "100"),
        ("sub.street",    "street",    "100"),
    ],
    "gaming": [
        ("sub.cyberpunk_g", "cyberpunk 2077", "100"),
        ("sub.witcher",     "witcher",        "100"),
        ("sub.gta",         "gta",            "100"),
        ("sub.elden_ring",  "elden ring",     "100"),
    ],
}

# доступные разрешения для ресайза/настроек
RESOLUTIONS = [
    ("res.fullhd", "1920x1080"),
    ("res.qhd",    "2560x1440"),
    ("res.uhd",    "3840x2160"),
    ("res.mobile", "1080x1920"),
]


def get_search_results_keyboard(
    items: list[dict], query: str, page: int, lang: str = "ru",
    chat_id: int = 0,
    categories: str = "111",
    sorting: str = "relevance",
    atleast: str | None = None,
) -> InlineKeyboardMarkup:
    """5 рядов по 3 кнопки (📥 / 📐 / ❤️) на каждый элемент + ряд пагинации.
    Параметры поиска для пагинации берутся из SEARCH_SESSIONS по chat_id.
    """
    rows = []
    for idx, item in enumerate(items, 1):
        wid = item["id"]
        rows.append([
            InlineKeyboardButton(
                text=f"{t('btn.wp_dl', lang)} {idx}",
                callback_data=f"wp:dl:{wid}",
                style="primary",
                icon_custom_emoji_id=E_ID["download"],
            ),
            InlineKeyboardButton(
                text=f"{t('btn.wp_resize', lang)} {idx}",
                callback_data=f"wp:rsz:{wid}",
                style="success",
                icon_custom_emoji_id=E_ID["gear"],
            ),
            InlineKeyboardButton(
                text=f"{t('btn.wp_fav', lang)} {idx}",
                callback_data=f"wp:fav:{wid}",
                style="success",
                icon_custom_emoji_id=E_ID["star"],
            ),
        ])

    rows.append([InlineKeyboardButton(
        text=t("btn.wp_next", lang),
        callback_data=f"wp:page:{chat_id}:{page + 1}",
        style="primary",
        icon_custom_emoji_id=E_ID["refresh"],
    )])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="danger",
        icon_custom_emoji_id=E_ID["home"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_search_filters_keyboard(
    lang: str = "ru",
    *,
    categories: str = "111",
    sorting: str = "relevance",
    atleast: str | None = None,
) -> InlineKeyboardMarkup:
    """Меню фильтров поиска. Открывается отдельным сообщением."""
    def _mark(active: bool, label: str) -> str:
        return f"• {label}" if active else label

    rows = [
        # категория
        [
            InlineKeyboardButton(
                text=_mark(categories == "100", t("cat.general", lang)),
                callback_data="wp:f:cat:100",
                style="success",
                icon_custom_emoji_id=E_ID["folder"],
            ),
            InlineKeyboardButton(
                text=_mark(categories == "010", t("cat.anime", lang)),
                callback_data="wp:f:cat:010",
                style="success",
                icon_custom_emoji_id=E_ID["folder"],
            ),
            InlineKeyboardButton(
                text=_mark(categories == "111", t("cat.all", lang)),
                callback_data="wp:f:cat:111",
                style="success",
                icon_custom_emoji_id=E_ID["folder"],
            ),
        ],
        # сортировка
        [
            InlineKeyboardButton(
                text=_mark(sorting == "relevance", t("sort.relevance", lang)),
                callback_data="wp:f:sort:relevance",
                style="success",
                icon_custom_emoji_id=E_ID["search"],
            ),
            InlineKeyboardButton(
                text=_mark(sorting == "toplist", t("sort.toplist", lang)),
                callback_data="wp:f:sort:toplist",
                style="success",
                icon_custom_emoji_id=E_ID["chart"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=_mark(sorting == "date_added", t("sort.new", lang)),
                callback_data="wp:f:sort:date_added",
                style="success",
                icon_custom_emoji_id=E_ID["clock"],
            ),
            InlineKeyboardButton(
                text=_mark(sorting == "views", t("sort.views", lang)),
                callback_data="wp:f:sort:views",
                style="success",
                icon_custom_emoji_id=E_ID["eye"],
            ),
        ],
        # минимальное разрешение
        [
            InlineKeyboardButton(
                text=_mark(not atleast, t("atleast.any", lang)),
                callback_data="wp:f:res:any",
                style="success",
                icon_custom_emoji_id=E_ID["camera"],
            ),
            InlineKeyboardButton(
                text=_mark(atleast == "1920x1080", t("atleast.fhd", lang)),
                callback_data="wp:f:res:1920x1080",
                style="success",
                icon_custom_emoji_id=E_ID["camera"],
            ),
            InlineKeyboardButton(
                text=_mark(atleast == "3840x2160", t("atleast.4k", lang)),
                callback_data="wp:f:res:3840x2160",
                style="success",
                icon_custom_emoji_id=E_ID["camera"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.wp_run_search", lang),
            callback_data="wp:filters_run",
            style="primary",
            icon_custom_emoji_id=E_ID["search"],
        )],
        [InlineKeyboardButton(
            text=t("btn.wp_filters_close", lang),
            callback_data="wp:filters_close",
            style="danger",
            icon_custom_emoji_id=E_ID["cross"],
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_categories_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Сетка 2x5 для 10 категорий. Если у категории есть подкатегории — открывает подменю."""
    rows = []
    row: list[InlineKeyboardButton] = []
    for key, slug, query, cats, has_sub in CATEGORY_BUTTONS:
        cb = f"wp:tree:{slug}" if has_sub else f"wp:cat:{query}:{cats}"
        row.append(InlineKeyboardButton(
            text=t(key, lang),
            callback_data=cb,
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        ))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="danger",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_subcategories_keyboard(slug: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Подменю подкатегорий конкретной категории."""
    rows = []
    row: list[InlineKeyboardButton] = []
    for key, query, cats in SUBCATEGORIES.get(slug, []):
        row.append(InlineKeyboardButton(
            text=t(key, lang),
            callback_data=f"wp:cat:{query}:{cats}",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        ))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="wallpaper_categories",
        style="danger",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_resolution_keyboard(
    wallhaven_id: str, lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Inline-клавиатура выбора разрешения для конкретного обоя."""
    rows = []
    for key, res in RESOLUTIONS:
        rows.append([InlineKeyboardButton(
            text=t(key, lang),
            callback_data=f"wp:res:{wallhaven_id}:{res}",
            style="primary",
            icon_custom_emoji_id=E_ID["camera"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="danger",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_settings_keyboard(user, lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню настроек юзера."""
    rows = [
        [InlineKeyboardButton(
            text=t("btn.wp_settings_res", lang),
            callback_data="wp:set:res",
            style="primary",
            icon_custom_emoji_id=E_ID["camera"],
        )],
        [InlineKeyboardButton(
            text=t("btn.wp_settings_cat", lang),
            callback_data="wp:set:cat",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="danger",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_resolution_setting_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    rows = []
    for key, res in RESOLUTIONS:
        rows.append([InlineKeyboardButton(
            text=t(key, lang),
            callback_data=f"wp:setres:{res}",
            style="primary",
            icon_custom_emoji_id=E_ID["camera"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="wp:settings",
        style="danger",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_category_setting_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Категории по умолчанию (general/anime/both)."""
    rows = [
        [InlineKeyboardButton(
            text=t("cat.general", lang),
            callback_data="wp:setcat:general",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )],
        [InlineKeyboardButton(
            text=t("cat.anime", lang),
            callback_data="wp:setcat:anime",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )],
        [InlineKeyboardButton(
            text=t("cat.both", lang),
            callback_data="wp:setcat:both",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="wp:settings",
            style="danger",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_favorites_keyboard(
    items: list, page: int, total_pages: int, lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Клавиатура для списка избранного. items — список Favorite-моделей."""
    rows = []
    for idx, fav in enumerate(items, 1):
        rows.append([
            InlineKeyboardButton(
                text=f"{t('btn.wp_dl', lang)} {idx}",
                callback_data=f"wp:dl:{fav.wallhaven_id}",
                style="primary",
                icon_custom_emoji_id=E_ID["download"],
            ),
            InlineKeyboardButton(
                text=f"{t('btn.wp_remove', lang)} {idx}",
                callback_data=f"wp:fav:{fav.wallhaven_id}",
                style="danger",
                icon_custom_emoji_id=E_ID["trash"],
            ),
        ])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(
            text=t("btn.wp_prev", lang),
            callback_data=f"wp:favpage:{page - 1}",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        ))
    if page < total_pages:
        nav.append(InlineKeyboardButton(
            text=t("btn.wp_next", lang),
            callback_data=f"wp:favpage:{page + 1}",
            style="primary",
            icon_custom_emoji_id=E_ID["refresh"],
        ))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="danger",
        icon_custom_emoji_id=E_ID["home"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)
