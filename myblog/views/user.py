from flask import Blueprint, render_template, current_app, request, redirect, url_for

from myblog.models import Post, Category, Message, Project
from myblog.forms import MessageForm
from myblog.extensions import db


user_bp = Blueprint("user", __name__)


@user_bp.route("/")
def home():
    return render_template("blog/home.html")


@user_bp.route("/posts", defaults={"page": 1})
@user_bp.route("/posts/<int:page>")
def show_posts(page):
    posts = Post.query.order_by(Post.timestamp.desc()).all()

    number_of_posts_per_page = current_app.config["NUMBER_POST_PER_PAGE"]

    start_post = number_of_posts_per_page * (page - 1)
    end_post = start_post + number_of_posts_per_page - 1

    page_posts = posts[start_post:end_post]

    if len(posts) % number_of_posts_per_page == 0:
        number_of_page = len(posts) // number_of_posts_per_page
    else:
        number_of_page = (len(posts) // number_of_posts_per_page) + 1

    return render_template(
        "blog/posts.html", posts=page_posts, page_number=number_of_page
    )


@user_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    has_pre = True
    has_next = True
    if post_id <= 1:
        has_pre = False
    if post_id >= Post.query.count():
        has_next = False

    post = Post.query.get_or_404(post_id)
    message_count = Message.query.filter_by(post_id=post_id).count()

    return render_template(
        "blog/post.html",
        post=post,
        message_count=message_count,
        has_pre=has_pre,
        has_next=has_next,
    )


@user_bp.route("/category/<int:category_id>")
def show_category(category_id):
    number_of_posts_per_page = current_app.config["NUMBER_POST_PER_PAGE"]
    page = request.args.get("page", 1, type=int)

    category = Category.query.get_or_404(category_id)
    posts = Post.query.with_parent(category).order_by(Post.timestamp.desc()).all()

    start_post = number_of_posts_per_page * (page - 1)
    end_post = start_post + number_of_posts_per_page - 1

    page_posts = posts[start_post:end_post]

    if len(posts) % number_of_posts_per_page == 0:
        number_of_page = len(posts) // number_of_posts_per_page
    else:
        number_of_page = (len(posts) // number_of_posts_per_page) + 1

    return render_template(
        "blog/category.html",
        category=category,
        posts=page_posts,
        page_number=number_of_page,
    )


@user_bp.route("/messages", defaults={"post_id": 0}, methods=["GET", "POST"])
@user_bp.route("/messages/<int:post_id>", methods=["GET", "POST"])
def show_messages(post_id):
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    if post_id:
        messages = (
            Message.query.filter_by(post_id=post_id)
            .order_by(Message.timestamp.desc())
            .all()
        )
    form = MessageForm()
    if form.validate_on_submit():
        email = form.email.data
        body = form.body.data
        site = form.site.data
        post_url = form.post_url.data

        # TODO 验证 post_url 的有效性，如无效则发送 flash 消息提醒用户.

        post = Post.query.get_or_404(int(post_url.split("/").pop()))
        message = Message(email=email, body=body, site=site, post=post)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for("user.show_messages"))
    if post_id:
        form.post_url.data = request.host_url + "post" + "/" + str(post_id)
    return render_template("blog/message.html", form=form, messages=messages)


@user_bp.route("/projects")
def show_projects():
    projects = Project.query.order_by(Project.timestamp.desc()).all()

    return render_template("blog/project.html", projects=projects)
