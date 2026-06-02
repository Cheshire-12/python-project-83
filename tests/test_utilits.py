from page_analyzer.utilits import get_normalized_url, validator


# --- ТЕСТЫ ВАЛИДАТОРА URL ---
def test_validator_valid_url():
    """Проверка валидного URL."""
    url = "https://example.com"
    errors = validator(url)
    assert not errors
    

def test_validator_invalid_url():
    """Проверка невалидного URL."""
    url = "invalid-url"
    errors = validator(url)
    assert errors
    assert "Некорректный URL" in errors


def test_validator_long_url():
    """Проверка URL, превышающего 255 символов."""
    url = "https://" + "a" * 250 + ".com"
    errors = validator(url)
    assert errors
    assert "Некорректный URL" in errors


def test_validator_empty_url():
    """Проверка пустого URL."""
    url = ""
    errors = validator(url)
    assert errors
    assert "Некорректный URL" in errors


# --- ТЕСТЫ НОРМАЛИЗАЦИИ URL ---
def test_get_normalized_url_valid():
    """Проверка нормализации валидного URL."""
    url = "https://Example.com/some/path?query=123"
    normalized = get_normalized_url(url)
    assert normalized == "https://example.com"


def test_get_normalized_url_no_scheme():
    """Проверка нормализации URL без схемы."""
    url = "example.com/some/path"
    normalized = get_normalized_url(url)
    assert normalized is None


def test_get_normalized_url_no_netloc():
    """Проверка нормализации URL без сетевого расположения."""
    url = "https:///some/path"
    normalized = get_normalized_url(url)
    assert normalized is None
