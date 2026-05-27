from datetime import datetime
from unittest.mock import MagicMock

import pook
import psycopg2.pool
import pytest

psycopg2.pool.ThreadedConnectionPool = MagicMock()

from page_analyzer.app import app  # noqa: E402


@pytest.fixture()
def client():
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key"
    })
    with app.test_client() as client:
        yield client


@pytest.fixture()
def mock_repo(monkeypatch):
    class MockRepo:
        def get_one_url(self, id): return None
        def create_check(self, id, data): pass
        def check_url_exists(self, url): return None
        def create(self, data): return 1
        def get_content(self): return []
        def get_analyze_results(self, id): return []

    mocked = MockRepo()
    
    globals_dict = app.view_functions['index'].__globals__
    monkeypatch.setitem(globals_dict, "repo", mocked)
    
    return mocked


# --- ТЕСТЫ ДОБАВЛЕНИЯ И ПРОСМОТРА URL ---

def test_index_page(client):
    """Проверка главной страницы."""
    response = client.get("/")
    assert response.status_code == 200


def test_get_urls_page(client):
    """Проверка страницы списка URL."""
    response = client.get("/urls")
    assert response.status_code == 200


def test_url_new_invalid(client):
    """Проверка отправки невалидного URL."""
    response = client.post("/urls", data={"url": "invalid-url"})
    assert response.status_code == 422
    assert "Некорректный URL" in response.text


def test_url_new_existing(client, mock_repo, monkeypatch):
    """Проверка добавления URL, который уже есть в базе."""
    monkeypatch.setattr(mock_repo, "check_url_exists", lambda url: {"id": 10})
    
    response = client.post(
        "/urls",
        data={"url": "https://hexlet.io"},
        follow_redirects=True
        )
    
    assert response.status_code == 200
    assert "Страница уже существует" in response.text


def test_url_new_success(client, mock_repo, monkeypatch):
    """Проверка успешного добавления нового URL."""
    monkeypatch.setattr(mock_repo, "check_url_exists", lambda url: None)
    monkeypatch.setattr(mock_repo, "create", lambda data: 99)
    monkeypatch.setattr(mock_repo, "get_one_url", lambda id: {
        "id": 99,
        "name": "https://hexlet.io",
        "created_at": datetime.now()
        })

    response = client.post(
        "/urls",
        data={"url": "https://hexlet.io"},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert "Страница успешно добавлена" in response.text


# --- ТЕСТЫ ПРОВЕРКИ (РОУТ /checks) ---

def test_url_check_not_found(client, mock_repo, monkeypatch):
    """Проверка запуска проверки для несуществующего ID."""
    monkeypatch.setattr(mock_repo, "get_one_url", lambda id: None)

    response = client.post("/urls/999/checks", follow_redirects=True)
    assert response.status_code == 200
    assert "Страница не найдена" in response.text


@pook.on
def test_url_check_network_error(client, mock_repo, monkeypatch):
    """Проверка ситуации, когда проверяемый сайт упал (ошибка сети/500)."""
    target_url = "https://broken-site.com"
    
    monkeypatch.setattr(mock_repo, "get_one_url", lambda id: {
        "id": 1,
        "name": target_url,
        "created_at": datetime.now()})
    
    pook.get(target_url).reply(500)

    response = client.post("/urls/1/checks", follow_redirects=True)
    
    assert response.status_code == 200
    assert "Произошла ошибка при проверке" in response.text


@pook.on
def test_url_check_success(client, mock_repo, monkeypatch):
    """Проверка успешного сканирования сайта и парсинга SEO-тегов."""
    target_url = "https://good-site.com"
    
    monkeypatch.setattr(mock_repo, "get_one_url", lambda id: {
        "id": 1,
        "name": target_url,
        "created_at": datetime.now()
    })
    
    test_html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Test Title</title>
                <meta name="description" content="Test Description">
            </head>
            <body>
                <h1>Test H1</h1>
            </body>
        </html>
    """
    
    pook.get(target_url).reply(200).body(test_html)

    saved_data = {}

    def fake_create_check(id, data):
        saved_data.update(data)
        
    monkeypatch.setattr(mock_repo, "create_check", fake_create_check)

    response = client.post("/urls/1/checks", follow_redirects=True)

    assert response.status_code == 200
    assert "Страница успешно проверена" in response.text
    
    assert saved_data["status_code"] == 200
    assert saved_data["title"] == "Test Title"
    assert saved_data["h1"] == "Test H1"
    assert saved_data["description"] == "Test Description"
