import os


from flask import Flask, render_template, send_from_directory, url_for


from myblog.settings import Config
from myblog.utils import md_to_html

app = Flask("myblog")
app.config.from_object(Config)

data_path = app.config["DATA_PATH"]


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
