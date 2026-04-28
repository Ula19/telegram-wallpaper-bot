"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['camera']} Я ищу и присылаю обои в высоком разрешении.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            f"• {E['search']} <b>Найти обои</b> — поиск по слову (на английском)\n"
            f"• {E['folder']} <b>Подбор по фильтрам</b> — без запроса, просто фильтры\n"
            f"• {E['refresh']} <b>Случайные</b> и {E['star']} <b>Избранное</b>\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['camera']} Yuqori sifatli rasmlarni topib yuboraman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            f"• {E['search']} <b>Rasm qidirish</b> — inglizcha so'z bo'yicha qidiruv\n"
            f"• {E['folder']} <b>Filtrlar bo'yicha tanlash</b> — so'rovsiz, faqat filtrlar\n"
            f"• {E['refresh']} <b>Tasodifiy</b> va {E['star']} <b>Sevimlilar</b>\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['camera']} I find and send high-resolution wallpapers.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            f"• {E['search']} <b>Search wallpapers</b> — by English keyword\n"
            f"• {E['folder']} <b>Browse with filters</b> — no query, just filters\n"
            f"• {E['refresh']} <b>Random</b> and {E['star']} <b>Favorites</b>\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.search": {
        "ru": "Найти обои",
        "uz": "Rasm qidirish",
        "en": "Search wallpapers",
    },
    "btn.discover": {
        "ru": "Подбор по фильтрам",
        "uz": "Filtrlar bo'yicha tanlash",
        "en": "Browse with filters",
    },
    "btn.wp_run_search": {
        "ru": "Запустить поиск",
        "uz": "Qidiruvni boshlash",
        "en": "Run search",
    },
    "btn.random": {
        "ru": "Случайные обои",
        "uz": "Tasodifiy rasmlar",
        "en": "Random wallpapers",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "btn.favorites": {
        "ru": "Избранное",
        "uz": "Sevimlilar",
        "en": "Favorites",
    },
    "btn.settings": {
        "ru": "Настройки",
        "uz": "Sozlamalar",
        "en": "Settings",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Скачиваний (всего): {{downloads}}\n"
            f"{E['gear']} Разрешение: {{resolution}}\n"
            f"{E['folder']} Категория: {{category}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sizning profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Yuklashlar (jami): {{downloads}}\n"
            f"{E['gear']} O'lcham: {{resolution}}\n"
            f"{E['folder']} Kategoriya: {{category}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Downloads (total): {{downloads}}\n"
            f"{E['gear']} Resolution: {{resolution}}\n"
            f"{E['folder']} Category: {{category}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['search']} <b>Поиск:</b> отправь текст на английском (например <code>nature 4k</code>) "
            "или используй /search\n"
            f"{E['folder']} <b>Подбор по фильтрам:</b> кнопка в меню — выбираешь категорию, "
            "сортировку и минимальное разрешение, бот подбирает обои\n"
            f"{E['refresh']} /random — случайные обои\n"
            f"{E['chart']} /top — топ за неделю\n"
            f"{E['folder']} /categories — 10 готовых тематик с подкатегориями\n"
            f"{E['star']} /favorites — твои избранные\n"
            f"{E['gear']} /settings — разрешение и категория по умолчанию\n\n"
            f"{E['download']} Под каждым превью есть кнопки:\n"
            "• <b>Скач.</b> — оригинальный файл (>20 МБ авто-уменьшается)\n"
            "• <b>Разм.</b> — ресайз под выбранное разрешение\n"
            "• <b>Избр.</b> — добавить в избранное\n\n"
            f"{E['lightning']} В любом чате: <code>@{{bot_username}} запрос</code> — inline-поиск\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['search']} <b>Qidiruv:</b> inglizcha matn yuboring (masalan <code>nature 4k</code>) "
            "yoki /search ishlating\n"
            f"{E['folder']} <b>Filtrlar bo'yicha tanlash:</b> menyudagi tugma — kategoriya, "
            "tartiblash va minimal o'lcham bo'yicha bot rasmlar tanlaydi\n"
            f"{E['refresh']} /random — tasodifiy rasmlar\n"
            f"{E['chart']} /top — hafta topi\n"
            f"{E['folder']} /categories — 10 ta tayyor kategoriya\n"
            f"{E['star']} /favorites — sevimlilaringiz\n"
            f"{E['gear']} /settings — standart o'lcham va kategoriya\n\n"
            f"{E['download']} Har bir rasm ostida tugmalar:\n"
            "• <b>Yukla</b> — asl fayl (>20 MB avtomatik kichraytiriladi)\n"
            "• <b>Resize</b> — tanlangan o'lchamga moslashtirish\n"
            "• <b>Sevim.</b> — sevimlilarga qo'shish\n\n"
            f"{E['lightning']} Istalgan chatda: <code>@{{bot_username}} so'rov</code> — inline qidiruv\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['search']} <b>Search:</b> send English text (e.g. <code>nature 4k</code>) "
            "or use /search\n"
            f"{E['folder']} <b>Browse with filters:</b> menu button — pick a category, "
            "sorting and minimum resolution, bot picks wallpapers for you\n"
            f"{E['refresh']} /random — random wallpapers\n"
            f"{E['chart']} /top — top of the week\n"
            f"{E['folder']} /categories — 10 ready-made themes with subcategories\n"
            f"{E['star']} /favorites — your saved wallpapers\n"
            f"{E['gear']} /settings — default resolution & category\n\n"
            f"{E['download']} Under each preview:\n"
            "• <b>DL</b> — original file (>20 MB auto-downsized)\n"
            "• <b>Size</b> — resize to the selected resolution\n"
            "• <b>Fav</b> — add to favorites\n\n"
            f"{E['lightning']} In any chat: <code>@{{bot_username}} query</code> — inline search\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['camera']} Этот бот ищет и отправляет обои высокого разрешения "
            "через Wallhaven API!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['camera']} Bu bot Wallhaven API orqali yuqori sifatli rasmlarni "
            "topadi va yuboradi!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['camera']} This bot finds and sends high-resolution wallpapers "
            "via Wallhaven API!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Siz hali barcha kanallarga obuna bo'lmadingiz:</b>\n\n"
            f"Obuna bo'ling va «{E['check']} Obunani tekshirish» tugmasini qayta bosing."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Отправь поисковый запрос или выбери действие."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi siz botdan foydalanishingiz mumkin! {E['plane']}\n\n"
            "Qidiruv so'rovini yuboring yoki amalni tanlang."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Send a search query or choose an action."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.not_found": {
        "ru": f"{E['cross']} <b>Ничего не найдено</b>\n\nПопробуй другой запрос.",
        "uz": f"{E['cross']} <b>Hech narsa topilmadi</b>\n\nBoshqa so'rovni sinab ko'ring.",
        "en": f"{E['cross']} <b>Nothing found</b>\n\nTry a different query.",
    },
    "error.api_error": {
        "ru": f"{E['warning']} <b>Ошибка API</b>\n\nВременная проблема. Попробуй позже.",
        "uz": f"{E['warning']} <b>API xatosi</b>\n\nVaqtinchalik muammo. Keyinroq urinib ko'ring.",
        "en": f"{E['warning']} <b>API error</b>\n\nTemporary issue. Try again later.",
    },
    "error.generic": {
        "ru": f"{E['cross']} <b>Что-то пошло не так</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Nimadir noto'g'ri ketdi</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['cross']} <b>Something went wrong</b>\n\nTry again later.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['download']} Всего скачиваний: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['download']} Jami yuklashlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['download']} Total downloads: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Bosh menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "cmd.search": {
        "ru": "Поиск обоев",
        "uz": "Rasm qidirish",
        "en": "Search wallpapers",
    },
    "cmd.random": {
        "ru": "Случайные обои",
        "uz": "Tasodifiy rasmlar",
        "en": "Random wallpapers",
    },
    "cmd.top": {
        "ru": "Топ за неделю",
        "uz": "Hafta topi",
        "en": "Top of the week",
    },
    "cmd.categories": {
        "ru": "Категории",
        "uz": "Kategoriyalar",
        "en": "Categories",
    },
    "cmd.favorites": {
        "ru": "Избранное",
        "uz": "Sevimlilar",
        "en": "Favorites",
    },
    "cmd.settings": {
        "ru": "Настройки",
        "uz": "Sozlamalar",
        "en": "Settings",
    },

    # === Wallpaper-специфичные ключи ===
    "wallpaper.search_prompt": {
        "ru": f"{E['search']} <b>Введите поисковый запрос:</b>\n\nПример: <code>nature 4k</code>, <code>cyberpunk city</code>, <code>minimal dark</code>",
        "uz": f"{E['search']} <b>Qidiruv so'rovini kiriting:</b>\n\nMisol: <code>nature 4k</code>, <code>cyberpunk city</code>, <code>minimal dark</code>",
        "en": f"{E['search']} <b>Enter your search query:</b>\n\nExample: <code>nature 4k</code>, <code>cyberpunk city</code>, <code>minimal dark</code>",
    },
    "wallpaper.search_results_header": {
        "ru": f"{E['search']} <b>Результаты по запросу</b> «{{query}}»\n{E['folder']} Страница {{page}}",
        "uz": f"{E['search']} <b>«{{query}}» bo'yicha natijalar</b>\n{E['folder']} Sahifa {{page}}",
        "en": f"{E['search']} <b>Results for</b> «{{query}}»\n{E['folder']} Page {{page}}",
    },
    "wallpaper.no_results": {
        "ru": f"{E['cross']} По запросу ничего не найдено.\nПопробуй другой запрос.",
        "uz": f"{E['cross']} So'rov bo'yicha hech narsa topilmadi.\nBoshqa so'rovni sinab ko'ring.",
        "en": f"{E['cross']} Nothing found for your query.\nTry a different one.",
    },
    "wallpaper.downloading": {
        "ru": f"{E['download']} Скачиваю обои…",
        "uz": f"{E['download']} Rasm yuklab olinmoqda…",
        "en": f"{E['download']} Downloading wallpaper…",
    },
    "wallpaper.downloaded": {
        "ru": f"{E['check']} Готово!",
        "uz": f"{E['check']} Tayyor!",
        "en": f"{E['check']} Done!",
    },
    "wallpaper.resize_choose": {
        "ru": f"{E['gear']} <b>Выбери разрешение:</b>",
        "uz": f"{E['gear']} <b>O'lchamni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose resolution:</b>",
    },
    "wallpaper.resize_done": {
        "ru": f"{E['check']} Картинка изменена под {{resolution}}",
        "uz": f"{E['check']} Rasm {{resolution}} o'lchamiga moslashtirildi",
        "en": f"{E['check']} Resized to {{resolution}}",
    },
    "wallpaper.fav_added": {
        "ru": f"{E['star']} Добавлено в избранное",
        "uz": f"{E['star']} Sevimlilarga qo'shildi",
        "en": f"{E['star']} Added to favorites",
    },
    "wallpaper.fav_removed": {
        "ru": f"{E['cross']} Убрано из избранного",
        "uz": f"{E['cross']} Sevimlilardan o'chirildi",
        "en": f"{E['cross']} Removed from favorites",
    },
    "wallpaper.fav_empty": {
        "ru": f"{E['star']} <b>Избранное пусто</b>\n\nДобавляй обои кнопкой {E['star']} под результатами поиска.",
        "uz": f"{E['star']} <b>Sevimlilar bo'sh</b>\n\nQidiruv natijalari ostidagi {E['star']} tugmasi orqali qo'shing.",
        "en": f"{E['star']} <b>Favorites are empty</b>\n\nAdd wallpapers via {E['star']} button under search results.",
    },
    "wallpaper.fav_list_header": {
        "ru": f"{E['star']} <b>Избранные обои</b>\n{E['folder']} Страница {{page}} из {{total_pages}} (всего {{total}})",
        "uz": f"{E['star']} <b>Sevimli rasmlar</b>\n{E['folder']} Sahifa {{page}}/{{total_pages}} (jami {{total}})",
        "en": f"{E['star']} <b>Favorite wallpapers</b>\n{E['folder']} Page {{page}}/{{total_pages}} (total {{total}})",
    },
    "wallpaper.categories_header": {
        "ru": f"{E['folder']} <b>Выбери категорию:</b>",
        "uz": f"{E['folder']} <b>Kategoriyani tanlang:</b>",
        "en": f"{E['folder']} <b>Choose a category:</b>",
    },
    "wallpaper.filters_header": {
        "ru": f"{E['gear']} <b>Фильтры поиска</b>\n\nВыбранный пункт отмечен «•».",
        "uz": f"{E['gear']} <b>Qidiruv filtrlari</b>\n\nTanlangan element «•» bilan belgilangan.",
        "en": f"{E['gear']} <b>Search filters</b>\n\nThe active option is marked with «•».",
    },
    # === Рекламная подпись под каждой картинкой ===
    "wallpaper.promo": {
        "ru": f"\n\n{E['camera']} Обои в HD через @{{bot_username}}",
        "uz": f"\n\n{E['camera']} HD rasmlar — @{{bot_username}} orqali",
        "en": f"\n\n{E['camera']} HD wallpapers via @{{bot_username}}",
    },
    "wallpaper.searching": {
        "ru": f"{E['search']} <i>Ищу обои…</i>",
        "uz": f"{E['search']} <i>Rasmlar qidirilmoqda…</i>",
        "en": f"{E['search']} <i>Searching wallpapers…</i>",
    },
    "wallpaper.cyrillic_hint": {
        "ru": (
            f"{E['warning']} <b>Wallhaven не индексирует кириллицу</b>\n\n"
            "Скорее всего ничего не найдётся. Попробуй на английском: "
            "<code>nature</code>, <code>mountain</code>, <code>cyberpunk</code>, "
            "<code>anime girl</code>."
        ),
        "uz": (
            f"{E['warning']} <b>Wallhaven kirill alifbosini tushunmaydi</b>\n\n"
            "Hech narsa topilmasligi mumkin. Inglizcha urinib ko'ring: "
            "<code>nature</code>, <code>mountain</code>, <code>cyberpunk</code>."
        ),
        "en": (
            f"{E['warning']} <b>Wallhaven does not index Cyrillic queries</b>\n\n"
            "Try English keywords: <code>nature</code>, <code>mountain</code>, "
            "<code>cyberpunk</code>."
        ),
    },
    "wallpaper.downsized": {
        "ru": (
            f"{E['warning']} Оригинал больше 20 МБ — отправил уменьшенную копию "
            "({resolution}). Чтобы получить оригинал — попробуй кнопку «Размер» "
            "и выбери разрешение поменьше."
        ),
        "uz": (
            f"{E['warning']} Asl nusxa 20 MB dan katta — kichraytirilgan nusxa "
            "yuborildi ({resolution})."
        ),
        "en": (
            f"{E['warning']} Original is over 20 MB — sent a downsized copy "
            "({resolution})."
        ),
    },
    "wallpaper.discover_header": {
        "ru": (
            f"{E['folder']} <b>Подбор по фильтрам</b>\n\n"
            "Выбери категорию, сортировку и минимальное разрешение.\n"
            "Активный пункт отмечен «•». Когда всё готово — нажми «Запустить поиск»."
        ),
        "uz": (
            f"{E['folder']} <b>Filtrlar bo'yicha tanlash</b>\n\n"
            "Kategoriya, tartiblash va minimal o'lchamni tanlang.\n"
            "Faol element «•» bilan belgilangan. Tayyor bo'lganda «Qidiruvni boshlash» tugmasini bosing."
        ),
        "en": (
            f"{E['folder']} <b>Browse with filters</b>\n\n"
            "Pick a category, sorting and minimum resolution.\n"
            "The active option is marked with «•». When ready, press «Run search»."
        ),
    },
    "wallpaper.settings_header": {
        "ru": (
            f"{E['gear']} <b>Настройки</b>\n\n"
            f"{E['camera']} Разрешение по умолчанию: <b>{{resolution}}</b>\n"
            f"{E['folder']} Категория по умолчанию: <b>{{category}}</b>"
        ),
        "uz": (
            f"{E['gear']} <b>Sozlamalar</b>\n\n"
            f"{E['camera']} Standart o'lcham: <b>{{resolution}}</b>\n"
            f"{E['folder']} Standart kategoriya: <b>{{category}}</b>"
        ),
        "en": (
            f"{E['gear']} <b>Settings</b>\n\n"
            f"{E['camera']} Default resolution: <b>{{resolution}}</b>\n"
            f"{E['folder']} Default category: <b>{{category}}</b>"
        ),
    },
    "wallpaper.settings_resolution": {
        "ru": f"{E['camera']} <b>Выбери разрешение по умолчанию:</b>",
        "uz": f"{E['camera']} <b>Standart o'lchamni tanlang:</b>",
        "en": f"{E['camera']} <b>Choose default resolution:</b>",
    },
    "wallpaper.settings_category": {
        "ru": f"{E['folder']} <b>Выбери категорию по умолчанию:</b>",
        "uz": f"{E['folder']} <b>Standart kategoriyani tanlang:</b>",
        "en": f"{E['folder']} <b>Choose default category:</b>",
    },
    "wallpaper.rate_limited": {
        "ru": f"{E['clock']} Wallhaven просит подождать. Попробуй через минуту.",
        "uz": f"{E['clock']} Wallhaven kutishni so'rayapti. Bir daqiqadan keyin urinib ko'ring.",
        "en": f"{E['clock']} Too many requests to Wallhaven. Try again in a minute.",
    },
    "wallpaper.search_error": {
        "ru": f"{E['warning']} Ошибка при поиске. Попробуй позже.",
        "uz": f"{E['warning']} Qidiruvda xato. Keyinroq urinib ko'ring.",
        "en": f"{E['warning']} Search error. Try again later.",
    },
    "wallpaper.top_header": {
        "ru": f"{E['chart']} <b>Топ обоев за неделю</b>",
        "uz": f"{E['chart']} <b>Hafta top rasmlari</b>",
        "en": f"{E['chart']} <b>Top wallpapers of the week</b>",
    },
    "wallpaper.random_header": {
        "ru": f"{E['refresh']} <b>Случайные обои</b>",
        "uz": f"{E['refresh']} <b>Tasodifiy rasmlar</b>",
        "en": f"{E['refresh']} <b>Random wallpapers</b>",
    },

    # === Категории (10 штук) ===
    "cat.nature": {"ru": "Природа", "uz": "Tabiat", "en": "Nature"},
    "cat.space": {"ru": "Космос", "uz": "Koinot", "en": "Space"},
    "cat.anime": {"ru": "Аниме", "uz": "Anime", "en": "Anime"},
    "cat.cars": {"ru": "Машины", "uz": "Mashinalar", "en": "Cars"},
    "cat.city": {"ru": "Города", "uz": "Shaharlar", "en": "City"},
    "cat.minimal": {"ru": "Минимализм", "uz": "Minimalizm", "en": "Minimal"},
    "cat.abstract": {"ru": "Абстракция", "uz": "Abstrakt", "en": "Abstract"},
    "cat.gaming": {"ru": "Игры", "uz": "O'yinlar", "en": "Gaming"},
    "cat.girls": {"ru": "Девушки", "uz": "Qizlar", "en": "Girls"},
    "cat.tech": {"ru": "Технологии", "uz": "Texnologiya", "en": "Tech"},
    "cat.both": {"ru": "Общее + Аниме", "uz": "Umumiy + Anime", "en": "General + Anime"},
    "cat.general": {"ru": "Общее", "uz": "Umumiy", "en": "General"},
    "cat.all": {"ru": "Все", "uz": "Hammasi", "en": "All"},
    "sort.relevance": {"ru": "Релевантные", "uz": "Mos", "en": "Relevant"},
    "sort.toplist": {"ru": "Топ недели", "uz": "Hafta topi", "en": "Top week"},
    "sort.new": {"ru": "Новые", "uz": "Yangi", "en": "New"},
    "sort.views": {"ru": "По просмотрам", "uz": "Ko'rishlar", "en": "Views"},
    "atleast.any": {"ru": "Любое", "uz": "Har qanday", "en": "Any size"},
    "atleast.fhd": {"ru": "≥ Full HD", "uz": "≥ Full HD", "en": "≥ Full HD"},
    "atleast.4k": {"ru": "≥ 4K", "uz": "≥ 4K", "en": "≥ 4K"},
    "sub.mountains":      {"ru": "Горы",      "uz": "Tog'lar",   "en": "Mountains"},
    "sub.sea":            {"ru": "Море",      "uz": "Dengiz",    "en": "Sea / Ocean"},
    "sub.forest":         {"ru": "Лес",       "uz": "O'rmon",    "en": "Forest"},
    "sub.sunset":         {"ru": "Закат",     "uz": "Kun botishi","en": "Sunset"},
    "sub.waterfall":      {"ru": "Водопад",   "uz": "Sharshara", "en": "Waterfall"},
    "sub.winter":         {"ru": "Зима",      "uz": "Qish",      "en": "Winter"},
    "sub.galaxy":         {"ru": "Галактика", "uz": "Galaktika", "en": "Galaxy"},
    "sub.planets":        {"ru": "Планеты",   "uz": "Sayyoralar","en": "Planets"},
    "sub.nebula":         {"ru": "Туманность","uz": "Tumanlik",  "en": "Nebula"},
    "sub.stars":          {"ru": "Звёзды",    "uz": "Yulduzlar", "en": "Stars"},
    "sub.anime_girl":     {"ru": "Аниме-девушка","uz": "Anime qiz","en": "Anime girl"},
    "sub.anime_landscape":{"ru": "Аниме-пейзаж", "uz": "Anime manzara","en": "Anime landscape"},
    "sub.anime_dark":     {"ru": "Аниме (тёмное)","uz": "Qorong'i anime","en": "Anime dark"},
    "sub.anime_school":   {"ru": "Школа",     "uz": "Maktab",    "en": "Anime school"},
    "sub.skyline":        {"ru": "Небоскрёбы","uz": "Osmono'par","en": "Skyline"},
    "sub.cyberpunk":      {"ru": "Киберпанк", "uz": "Kiberpunk", "en": "Cyberpunk"},
    "sub.night":          {"ru": "Ночной город","uz": "Tungi shahar","en": "Night city"},
    "sub.street":         {"ru": "Улицы",     "uz": "Ko'chalar", "en": "Streets"},
    "sub.cyberpunk_g":    {"ru": "Cyberpunk 2077","uz": "Cyberpunk 2077","en": "Cyberpunk 2077"},
    "sub.witcher":        {"ru": "Ведьмак",   "uz": "Vedmak",    "en": "Witcher"},
    "sub.gta":            {"ru": "GTA",       "uz": "GTA",       "en": "GTA"},
    "sub.elden_ring":     {"ru": "Elden Ring","uz": "Elden Ring","en": "Elden Ring"},

    # === Разрешения ===
    "res.fullhd": {"ru": "1920×1080 (FullHD)", "uz": "1920×1080 (FullHD)", "en": "1920×1080 (FullHD)"},
    "res.qhd": {"ru": "2560×1440 (2K)", "uz": "2560×1440 (2K)", "en": "2560×1440 (2K)"},
    "res.uhd": {"ru": "3840×2160 (4K)", "uz": "3840×2160 (4K)", "en": "3840×2160 (4K)"},
    "res.mobile": {"ru": "1080×1920 (Mobile)", "uz": "1080×1920 (Mobile)", "en": "1080×1920 (Mobile)"},

    # === Кнопки wallpaper ===
    "btn.wp_dl": {"ru": "Скач.", "uz": "Yukla", "en": "DL"},
    "btn.wp_resize": {"ru": "Разм.", "uz": "Resize", "en": "Size"},
    "btn.wp_fav": {"ru": "Избр.", "uz": "Sevim.", "en": "Fav"},
    "btn.wp_remove": {"ru": "Убрать", "uz": "Olib tashlash", "en": "Remove"},
    "btn.wp_prev": {"ru": "Пред. страница", "uz": "Oldingi sahifa", "en": "Prev page"},
    "btn.wp_next": {"ru": "След. страница", "uz": "Keyingi sahifa", "en": "Next page"},
    "btn.wp_filters": {"ru": "Фильтры", "uz": "Filtrlar", "en": "Filters"},
    "btn.wp_filters_close": {"ru": "Закрыть", "uz": "Yopish", "en": "Close"},
    "btn.wp_settings_res": {"ru": "Разрешение", "uz": "O'lcham", "en": "Resolution"},
    "btn.wp_settings_cat": {"ru": "Категория", "uz": "Kategoriya", "en": "Category"},

    # === /stats для админа ===
    "admin.stats_full": {
        "ru": (
            f"{E['chart']} <b>Расширенная статистика</b>\n\n"
            f"{E['users']} Юзеров: <b>{{total_users}}</b> (сегодня +{{today_users}})\n"
            f"{E['search']} Поисков: <b>{{total_searches}}</b>\n"
            f"{E['star']} Избранного: <b>{{total_favorites}}</b>\n"
            f"{E['download']} Скачиваний: <b>{{total_downloads}}</b>\n"
            f"{E['package']} Кэш обоев: <b>{{cache_size}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>\n\n"
            f"{E['pin']} <b>Топ-10 запросов:</b>\n{{top_list}}"
        ),
        "uz": (
            f"{E['chart']} <b>Kengaytirilgan statistika</b>\n\n"
            f"{E['users']} Foydalanuvchilar: <b>{{total_users}}</b> (bugun +{{today_users}})\n"
            f"{E['search']} Qidiruvlar: <b>{{total_searches}}</b>\n"
            f"{E['star']} Sevimlilar: <b>{{total_favorites}}</b>\n"
            f"{E['download']} Yuklashlar: <b>{{total_downloads}}</b>\n"
            f"{E['package']} Kesh: <b>{{cache_size}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>\n\n"
            f"{E['pin']} <b>Top-10 so'rovlar:</b>\n{{top_list}}"
        ),
        "en": (
            f"{E['chart']} <b>Detailed statistics</b>\n\n"
            f"{E['users']} Users: <b>{{total_users}}</b> (today +{{today_users}})\n"
            f"{E['search']} Searches: <b>{{total_searches}}</b>\n"
            f"{E['star']} Favorites: <b>{{total_favorites}}</b>\n"
            f"{E['download']} Downloads: <b>{{total_downloads}}</b>\n"
            f"{E['package']} Cache size: <b>{{cache_size}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>\n\n"
            f"{E['pin']} <b>Top-10 queries:</b>\n{{top_list}}"
        ),
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
