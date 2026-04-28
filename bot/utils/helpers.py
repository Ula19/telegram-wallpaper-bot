"""Вспомогательные утилиты"""


def is_search_request(text: str) -> bool:
    """Определяет, является ли текст поисковым запросом обоев.

    Возвращает True если:
    - текст не начинается с '/' (не команда)
    - текст не пустой
    - длина текста от 2 до 200 символов

    TODO: при необходимости добавить более точную фильтрацию
    (например, проверку на URL, спецсимволы и т.д.)
    """
    if not text:
        return False
    if text.startswith("/"):
        return False
    if len(text) < 2 or len(text) > 200:
        return False
    return True
