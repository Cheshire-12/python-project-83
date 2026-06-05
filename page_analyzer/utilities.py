from urllib.parse import urlparse

import requests
import validators


def validator(url):
    """Вспомогательная функция валидации URL адресса"""
    errors = []
    if not url or not validators.url(url) or len(url) > 255:
        errors.append("Некорректный URL")
    return errors


def analyze_url(url: str):
    """Вспомогательная функция для получения статуса и контента страницы"""
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.status_code, r.text
    except requests.RequestException:
        return None, None
    

def get_normalized_url(url: str | None) -> str | None:
    """Вспомогательная функция для приведения url к нормализованному виду"""
    parsed_url = urlparse(url)
    return (f"{parsed_url.scheme}://{parsed_url.netloc}".lower()
            if parsed_url.scheme and parsed_url.netloc else None
           )
