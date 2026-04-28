"""Модели базы данных — User, Channel + доменные модели обоев"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    # когда первый раз зашел в бота
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # сколько раз скачивал обоев
    download_count: Mapped[int] = mapped_column(default=0)
    # язык интерфейса: ru / uz / en
    language: Mapped[str] = mapped_column(String(5), default="ru")

    # === Пользовательские настройки обоев ===
    # разрешение по умолчанию (например "1920x1080")
    default_resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    # категория по умолчанию: general / anime / people
    default_category: Mapped[str] = mapped_column(String(20), default="general")
    # личный API-ключ Wallhaven (опционально — для NSFW и лучших лимитов)
    wallhaven_api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username})>"


class Channel(Base):
    """Канал/группа для обязательной подписки"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id канала в Telegram (например -1001234567890)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    # название для отображения юзеру
    title: Mapped[str] = mapped_column(String(255))
    # ссылка на канал (для кнопки "Подписаться")
    invite_link: Mapped[str] = mapped_column(String(255))
    # когда добавлен
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Channel {self.channel_id} ({self.title})>"


# === TODO: доменные модели обоев ===

class WallpaperCache(Base):
    """Кэш обоев из Wallhaven — хранит file_id для быстрой повторной отправки"""
    __tablename__ = "wallpaper_cache"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # ID обоя на Wallhaven (например "abc123")
    wallhaven_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    # URL превью
    thumb_url: Mapped[str] = mapped_column(String(500))
    # URL полного изображения
    full_url: Mapped[str] = mapped_column(String(500))
    # разрешение ("1920x1080")
    resolution: Mapped[str] = mapped_column(String(20))
    # категория ("general", "anime", "people")
    category: Mapped[str] = mapped_column(String(20))
    # file_id оригинала в Telegram (None если ещё не отправляли)
    file_id_orig: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # file_id ресайзнутых версий (JSONB: {"1920x1080": "...", "2560x1440": "..."})
    file_id_resized: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # когда закэшировано
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<WallpaperCache {self.wallhaven_id} ({self.resolution})>"


class Favorite(Base):
    """Избранные обои пользователя"""
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # telegram_id юзера
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    # ID обоя на Wallhaven
    wallhaven_id: Mapped[str] = mapped_column(String(50), index=True)
    # когда добавлено
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Favorite user={self.user_id} wallpaper={self.wallhaven_id}>"


class SearchRequest(Base):
    """История поисковых запросов"""
    __tablename__ = "search_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # telegram_id юзера
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    # поисковый запрос
    query: Mapped[str] = mapped_column(String(500))
    # сколько результатов вернул API
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    # когда выполнен
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<SearchRequest user={self.user_id} query={self.query!r}>"
