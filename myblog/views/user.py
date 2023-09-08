from flask import (
    Blueprint,
    flash,
    render_template,
    request,
    redirect,
    url_for,
)

from myblog.models import Post, Category, Message, Project, Subscriber
from myblog.forms import MessageForm, SubscribeForm
from myblog.extensions import db
from myblog.utlis import page_break


user_bp = Blueprint("user", __name__)


@user_bp.route("/", methods=["GET", "POST"])
def home():
    form = SubscribeForm()
    if form.validate_on_submit():
        email = form.email.data
        subscriber = Subscriber(email=email)
        db.session.add(subscriber)
        db.session.commit()
        flash("成功订阅博客！")
        return redirect(url_for("user.home"))
    return render_template("blog/home.html", form=form)


@user_bp.route("/posts", defaults={"page": 1})
@user_bp.route("/posts/<int:page>")
def show_posts(page):
    filter = request.args.get("filter")
    if filter == "mention":
        posts = Post.query.order_by(Post.mention.desc()).all()
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()

    page_posts = page_break(posts, page).get("page_items")
    number_of_page = page_break(posts, page).get("number_of_page")

    return render_template(
        "blog/posts.html", posts=page_posts, page_number=number_of_page
    )


@user_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    post = Post.query.get_or_404(post_id)
    index = posts.index(post)
    has_pre = True
    has_next = True
    if index == Post.query.count():
        has_pre = False
    if index == 0:
        has_next = False

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
    filter = request.args.get("filter")
    page = request.args.get("page", 1, type=int)

    category = Category.query.get_or_404(category_id)
    if filter == "mention":
        posts = Post.query.with_parent(category).order_by(Post.mention.desc()).all()
    else:
        posts = Post.query.with_parent(category).order_by(Post.timestamp.desc()).all()

    page_posts = page_break(posts, page).get("page_items")
    number_of_page = page_break(posts, page).get("number_of_page")

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
    message_count = len(messages)
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
        post = None
        if post_url:
            import re

            if re.match(f"{request.host_url}post/\d+", post_url):
                post = Post.query.get_or_404(int(post_url.split("/").pop()))
            else:
                flash(f"如需引用文章，请输入文章链接！例如：{request.host_url}post/7")

        message = Message(email=email, body=body, site=site, post=post)
        db.session.add(message)
        db.session.commit()
        flash("成功添加留言！")
        message.update_post()
        if post_id:
            return redirect(url_for("user.show_messages", post_id=post_id))
        else:
            return redirect(url_for("user.show_messages"))
    if post_id:
        form.post_url.data = request.host_url + "post" + "/" + str(post_id)
    return render_template(
        "blog/message.html", form=form, messages=messages, message_count=message_count
    )


@user_bp.route("/projects")
def show_projects():
    projects = Project.query.order_by(Project.timestamp.desc()).all()

    return render_template("blog/project.html", projects=projects)
