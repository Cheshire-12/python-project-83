import os
from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from psycopg2.pool import ThreadedConnectionPool

from page_analyzer.analyze_repo import AnalyzeRepo

app = Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")  # NOSONAR

DATABASE_URL = os.getenv("DATABASE_URL")
conn = ThreadedConnectionPool(1, 10, dsn=DATABASE_URL)

repo = AnalyzeRepo(conn)


def validator(url):
    """Вспомогательная функция валидации URL адресса"""
    errors = []
    if not url or not validators.url(url) or len(url) > 255:
        errors.append("Некорректный URL")
    return errors


def analyze_url(url):
    """Вспомогательная функция для получения статуса и контента страницы"""
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.status_code, r.text
    except requests.RequestException:
        return None, None
        

@app.get("/")
def index():
    return render_template("start_page.html")


@app.get("/urls")
def get_urls():
    urls_data = repo.get_content()
    return render_template("show_urls.html", urls=urls_data)


@app.post("/urls")
def url_new():
    url_data = request.form.get("url")
    
    errors = validator(url_data)
    if errors:
        flash("Некорректный URL. Пожалуйста, введите правильный URL.", "danger")
        return render_template(
            "start_page.html", url_data=url_data, errors=errors
            ), 422
    
    parsed_url = urlparse(url_data)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    existing_url = repo.check_url_exists(normalized_url)
    
    if existing_url:
        flash("Страница уже существует!", "info")
        return redirect(url_for("get_one_url", id=existing_url['id']))
    
    new_id = repo.create({"url": normalized_url})
    
    flash("Страница успешно добавлена!", "success")
    return redirect(url_for("get_one_url", id=new_id))


@app.get("/urls/<int:id>")
def get_one_url(id):
    url_data = repo.get_one_url(id)
    if not url_data:
        flash("Страница не найдена!", "danger")
        return redirect(url_for("get_urls"))
    checks = repo.get_analyze_results(id)
    return render_template("show_one_url.html", url=url_data, checks=checks)


@app.post("/urls/<int:id>/checks")
def url_check(id):
    url_data = repo.get_one_url(id)
    
    if not url_data:
        flash("Страница не найдена", "danger")
        return redirect(url_for("get_urls"))
    
    status_code, content = analyze_url(url_data['name'])
    
    if status_code is None:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("get_one_url", id=id))
    
    if content is None:
        flash("Не удалось получить содержимое страницы", "danger")
        return redirect(url_for("get_one_url", id=id))
    
    soup = BeautifulSoup(content, "html.parser")
    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else ''
    
    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag else ''
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '').strip() if meta_desc else ''  # type: ignore
    
    gathered_data = {
        "status_code": status_code,
        "h1": h1,
        "title": title,
        "description": description
    }
    
    repo.create_check(id, gathered_data)
    
    flash("Страница успешно проверена", "success")
    return redirect(url_for("get_one_url", id=id))
