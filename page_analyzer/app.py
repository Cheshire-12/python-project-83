from dotenv import load_dotenv
import os
from flask import (
    Flask,
    render_template
)


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return render_template("start_page.html")