import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from psycopg2.pool import ThreadedConnectionPool

from page_analyzer.analyze_repo import AnalyzeRepo
from page_analyzer.parser import parse_html
from page_analyzer.utilits import analyze_url, get_normalized_url, validator

app = Flask(__name__)  # NOSONAR

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")  # NOSONAR

DATABASE_URL = os.getenv("DATABASE_URL")
conn = ThreadedConnectionPool(1, 10, dsn=DATABASE_URL)

repo = AnalyzeRepo(conn)


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
    
    normalized_url = get_normalized_url(url_data)
    
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
    
    parsed_data = parse_html(content)
  
    gathered_data = {
        "status_code": status_code,
        "h1": parsed_data['h1'],
        "title": parsed_data['title'],
        "description": parsed_data['description']
    }
    
    repo.create_check(id, gathered_data)
    
    flash("Страница успешно проверена", "success")
    return redirect(url_for("get_one_url", id=id))
