"""Сервис для работы с Wallhaven API.

Документация: https://wallhaven.cc/help/api

Эндпоинты:
  GET https://wallhaven.cc/api/v1/search   — поиск обоев (q, categories, purity, sorting,
                                              order, topRange, atleast, resolutions, page)
  GET https://wallhaven.cc/api/v1/w/{id}   — детали обоя

Авторизация:
  Без API-ключа — только purity=100 (SFW), 45 запросов/минуту.
  С API-ключом — доступ к sketchy/nsfw, выше лимиты.
  Передаётся через header X-API-Key или query apikey=...

categories битмаска: General(100) / Anime(010) / People(001) — комбинируется ("110" = General+Anime).
purity битмаска:    SFW(100) / Sketchy(010) / NSFW(001).
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import ClassVar

import aiofiles
import httpx
from PIL import Image, ImageOps

from bot.config import settings

logger = logging.getLogger(__name__)


class WallhavenError(Exception):
    """Ошибка Wallhaven API."""


class WallhavenRateLimit(WallhavenError):
    """HTTP 429 — превышен лимит запросов."""


class WallhavenService:
    """Клиент Wallhaven API + утилиты скачивания/ресайза."""

    BASE = "https://wallhaven.cc/api/v1"
    # семафор общий на все инстансы (защита канала)
    _sem: ClassVar[asyncio.Semaphore] = asyncio.Semaphore(5)

    def __init__(self, api_key: str | None = None):
        # пустую строку приводим к None, чтобы не слать пустой header
        self.api_key = (api_key or settings.wallhaven_api_key) or None
        # ленивый shared httpx-клиент
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------ helpers

    def _headers(self) -> dict:
        if self.api_key:
            return {"X-API-Key": self.api_key}
        return {}

    async def _get_client(self) -> httpx.AsyncClient:
        """Лениво создаёт shared httpx-клиент."""
        if self._client is None or self._client.is_closed:
            timeout = httpx.Timeout(connect=5, read=30, write=10, pool=5)
            self._client = httpx.AsyncClient(timeout=timeout)
        return self._client

    async def close(self) -> None:
        """Корректно закрыть shared клиент (вызывается на shutdown бота)."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        max_retries: int = 3,
    ) -> dict:
        """HTTP запрос с retry на 429/5xx (exponential backoff: 1s, 2s, 4s).
        На 429 уважает заголовок Retry-After.
        """
        delay = 1.0
        last_exc: Exception | None = None
        client = await self._get_client()

        for attempt in range(1, max_retries + 1):
            try:
                resp = await client.request(
                    method, url, params=params, headers=self._headers()
                )

                # 429 — rate limit
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    try:
                        wait = float(retry_after) if retry_after else delay
                    except ValueError:
                        wait = delay
                    logger.warning(
                        "Wallhaven 429 (попытка %d/%d), ждём %.1fs",
                        attempt, max_retries, wait,
                    )
                    if attempt == max_retries:
                        raise WallhavenRateLimit("rate limited")
                    await asyncio.sleep(wait)
                    delay *= 2
                    continue

                # 5xx — серверная ошибка, делаем retry
                if 500 <= resp.status_code < 600:
                    logger.warning(
                        "Wallhaven %d (попытка %d/%d), ждём %.1fs",
                        resp.status_code, attempt, max_retries, delay,
                    )
                    if attempt == max_retries:
                        raise WallhavenError(f"HTTP {resp.status_code}")
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue

                resp.raise_for_status()

                try:
                    return resp.json()
                except ValueError as e:
                    logger.error("Wallhaven invalid json: %s", e)
                    raise WallhavenError("invalid json") from e

            except httpx.HTTPStatusError as e:
                logger.error("Wallhaven HTTP %s: %s", e.response.status_code, e)
                raise WallhavenError(f"HTTP {e.response.status_code}") from e
            except httpx.RequestError as e:
                last_exc = e
                logger.warning("Wallhaven сетевая ошибка (попытка %d): %s", attempt, e)
                if attempt == max_retries:
                    raise WallhavenError(f"network error: {e}") from e
                await asyncio.sleep(delay)
                delay *= 2

        raise WallhavenError(f"unreachable: {last_exc}")

    # ------------------------------------------------------------------ search

    async def search(
        self,
        query: str,
        *,
        page: int = 1,
        categories: str = "111",
        purity: str = "100",
        sorting: str = "relevance",
        resolutions: str | None = None,
        atleast: str | None = None,
        top_range: str | None = None,
    ) -> dict:
        """Поиск обоев. Возвращает сырой ответ API: {data: [...], meta: {...}}."""
        params: dict = {
            "q": query,
            "categories": categories,
            "purity": purity,
            "sorting": sorting,
            "page": page,
        }
        if resolutions:
            params["resolutions"] = resolutions
        if atleast:
            params["atleast"] = atleast
        if sorting == "toplist" and top_range:
            params["topRange"] = top_range
        # без ключа purity всегда 100
        if not self.api_key:
            params["purity"] = "100"

        return await self._request("GET", f"{self.BASE}/search", params=params)

    async def get_random(
        self,
        *,
        categories: str = "111",
        purity: str = "100",
    ) -> list[dict]:
        """Случайные обои (sorting=random). Возвращает список (обычно 24 шт)."""
        data = await self.search(
            query="", categories=categories, purity=purity, sorting="random"
        )
        return data.get("data", [])

    async def get_top(
        self,
        *,
        categories: str = "111",
        purity: str = "100",
        top_range: str = "1w",
    ) -> list[dict]:
        """Топ обоев за период."""
        data = await self.search(
            query="",
            categories=categories,
            purity=purity,
            sorting="toplist",
            top_range=top_range,
        )
        return data.get("data", [])

    async def get_wallpaper(self, wallhaven_id: str) -> dict | None:
        """Детали одного обоя или None если 404."""
        try:
            data = await self._request("GET", f"{self.BASE}/w/{wallhaven_id}")
            return data.get("data")
        except WallhavenError as e:
            logger.warning("get_wallpaper(%s) failed: %s", wallhaven_id, e)
            return None

    # ------------------------------------------------------------------ download

    async def download_image(self, url: str, dest: Path) -> Path:
        """Скачивает картинку по URL в dest. Возвращает путь."""
        # валидация URL — должен быть с домена wallhaven CDN
        if not url.startswith("https://w.wallhaven.cc/"):
            raise WallhavenError(f"bad url domain: {url!r}")

        async with self._sem:
            client = await self._get_client()
            try:
                async with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    async with aiofiles.open(dest, "wb") as f:
                        async for chunk in resp.aiter_bytes(chunk_size=64 * 1024):
                            await f.write(chunk)
            except httpx.HTTPError as e:
                logger.error("download_image(%s) failed: %s", url, e)
                raise WallhavenError(f"download error: {e}") from e
        return dest

    async def fetch_bytes(self, url: str, *, max_size: int = 5_000_000) -> bytes | None:
        """Скачивает картинку в память для отправки превью. Возвращает None при ошибке/превышении размера."""
        if not url.startswith("https://w.wallhaven.cc/") and not url.startswith("https://th.wallhaven.cc/"):
            return None
        async with self._sem:
            client = await self._get_client()
            try:
                resp = await client.get(url, timeout=20)
                if resp.status_code != 200:
                    return None
                content = resp.content
                if len(content) > max_size:
                    return None
                return content
            except httpx.HTTPError as e:
                logger.warning("fetch_bytes(%s) failed: %s", url, e)
                return None

    async def resize_image(self, src: Path, target_resolution: str) -> Path:
        """Ресайз картинки до target_resolution ('WIDTHxHEIGHT'). Pillow в executor."""
        try:
            w, h = (int(x) for x in target_resolution.lower().split("x"))
        except Exception as e:
            raise WallhavenError(f"bad resolution {target_resolution!r}") from e

        dest = src.with_name(f"{src.stem}_{w}x{h}{src.suffix or '.jpg'}")

        def _do() -> Path:
            with Image.open(src) as im:
                # учитываем EXIF-ориентацию
                im = ImageOps.exif_transpose(im)
                # alpha → composite на белый фон
                if im.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    alpha = im.split()[-1]
                    bg.paste(im.convert("RGB"), mask=alpha)
                    im = bg
                else:
                    im = im.convert("RGB")
                # cover-ресайз с сохранением пропорций (центрированный кроп)
                src_w, src_h = im.size
                ratio_src = src_w / src_h
                ratio_dst = w / h
                if ratio_src > ratio_dst:
                    # шире чем нужно — режем по бокам
                    new_w = int(src_h * ratio_dst)
                    left = (src_w - new_w) // 2
                    im = im.crop((left, 0, left + new_w, src_h))
                else:
                    new_h = int(src_w / ratio_dst)
                    top = (src_h - new_h) // 2
                    im = im.crop((0, top, src_w, top + new_h))
                im = im.resize((w, h), Image.LANCZOS)
                im.save(dest, format="JPEG", quality=92, optimize=True)
            return dest

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _do)


# глобальный экземпляр сервиса
wallhaven_service = WallhavenService()
