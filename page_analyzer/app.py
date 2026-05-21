from page_analyzer.analyze_repo import AnalyzeRepo
import validators
from urllib.parse import urlparse
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv
import os
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
app = Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")
conn = ThreadedConnectionPool(1,10, dsn=DATABASE_URL)

repo = AnalyzeRepo(conn)

def validator(url):
    errors = []
    if not url or not validators.url(url) or len(url) > 255:
        errors.append("Некорректный URL")
    return errors

@app.route("/")
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
        return render_template("start_page.html", url_data=url_data, errors=errors), 422
    
    parsed_url = urlparse(url_data)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    existing_url = repo.check_url_exists(normalized_url)
    
    if existing_url:
        flash("Страница уже существует!", "info")
        return redirect(url_for("get_one_url", id=existing_url['id']))
    
    new_id = repo.create({"url": normalized_url})
    
    flash("Страница успешно добавлена!", "success")
    return redirect(url_for("get_one_url", id=new_id))

@app.route("/urls/<int:id>", methods=["GET"])
def get_one_url(id):
    url_data = repo.get_one_url(id)
    if not url_data:
        flash("Страница не найдена!", "danger")
        return redirect(url_for("get_urls"))
    checks = repo.get_analyze_results(id)
    return render_template("show_one_url.html", url=url_data, checks=checks)

@app.post("/urls/<int:id>/checks")
def url_check(id):
    check_data = request.form.to_dict()
    errors = []
    # В будущей, более полной версии, здесь будет код для проверки URL и получения данных для анализа
    if errors:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("get_one_url", id=id))

    repo.create_check(id, check_data)
    
    flash("Страница успешно проверена", "success")
    return redirect(url_for("get_one_url", id=id))

