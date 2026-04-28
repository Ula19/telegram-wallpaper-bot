"""Конфигурация бота — все настройки из .env"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен бота
    bot_token: str

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "bot_4_wallpaper"
    db_user: str = "postgres"
    db_password: str = ""

    # юзернейм бота
    bot_username: str = ""

    # админы бота (через запятую в .env)
    admin_ids: str = ""
    admin_username: str = "admin"

    # Wallhaven API ключ (опционально — без него только SFW обои)
    wallhaven_api_key: str = ""

    # разрешение по умолчанию (для фильтрации обоев)
    default_resolution: str = "1920x1080"

    # URL Local Bot API (опционально — для файлов > 50 МБ)
    # нужен если бот шлёт файлы крупнее стандартного лимита Telegram
    local_bot_api_url: str = "https://api.telegram.org"

    # кэш обоев (дни)
    cache_ttl_days: int = 7

    @property
    def admin_id_list(self) -> list[int]:
        """Парсит admin_ids из строки в список int"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    @property
    def db_url(self) -> str:
        """URL для подключения к PostgreSQL через asyncpg"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# глобальный экземпляр настроек
settings = Settings()
