import os
import logging
from logging.handlers import RotatingFileHandler


import redis
from flask import Flask, render_template, send_from_directory, url_for, request


from myblog.models import POOL, Post
from myblog.settings import Config
from myblog.utils import md_to_html

conn = redis.Redis(connection_pool=POOL)
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
    if not os.path.exists(filename):
        return render_template("base.html", content="还没有编写主页页面")
    content = md_to_html(filename)
    return render_template("base.html", content=content)


@app.route("/post/<title>")
def post(title: str):
    post = Post(app)
    post.init_post_by_title(title)

    return render_template("base.html", post=post)


@app.route("/posts")
def posts():
    desc = True
    filter = request.args.get("filter", "recently")
    match filter:
        case "recently":
            desc = True
        case "notrecent":
            desc = False

    items = conn.zrange(name="recently", start=0, end=-1, desc=desc, withscores=True)

    posts = []
    for item in items:
        title = item[0]
        post = Post(app).init_post_by_title(title=title)
        posts.append(post)

    return render_template("posts.html", posts=posts)


@app.route("/images/<path:image_filename>")
def image(image_filename):
    image_folder = os.path.join(data_path, "images")
    return send_from_directory(image_folder, image_filename)


if __name__ == "__main__":
    pass
