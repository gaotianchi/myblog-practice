import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, send_from_directory, url_for


from myblog.settings import Config
from myblog.utils import md_to_html

app = Flask("myblog")
app.config.from_object(Config)

data_path = app.config["WORKSPACE"]

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = RotatingFileHandler(
    os.path.join(app.config["LOGS_PATH"], "myblog.log"),
    mode="a",
    maxBytes=10 * 1024,
    backupCount=10,
    encoding="UTF-8",
)
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)


@app.route("/")
def home():
    filename = os.path.join(data_path, "home.md")
    content = md_to_html(filename)
    return render_template("base.html", content=content)


@app.route("/post/<name>")
def post(name: str):
    filename = os.path.join(data_path, f"posts/{name}")
    content = md_to_html(filename)
    return render_template("base.html", content=content)


@app.route("/posts")
def posts():
    posts = []
    posts_path = os.path.join(data_path, "posts")
    files = os.listdir(posts_path)
    for file in files:
        posts.append({"title": file, "url": url_for("post", name=file)})

    return render_template("posts.html", posts=posts)


@app.route("/images/<path:image_filename>")
def image(image_filename):
    image_folder = os.path.join(data_path, "images")
    return send_from_directory(image_folder, image_filename)


if __name__ == "__main__":
    pass
