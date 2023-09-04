from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required

from myblog.models import Post, Category, Message, Project
from myblog.extensions import db
from myblog.utlis import redirect_back, page_break
from myblog.forms import PostForm, ProjectForm, CategoryForm


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect_back()


@admin_bp.route("/post/manage")
@login_required
def manage_post():
    filter = request.args.get("filter")
    if filter == "timestamp":
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    else:
        posts = Post.query.order_by(Post.mention.desc()).all()

    page = request.args.get("page")
    page_posts = page_break(posts, page).get("page_items")
    number_of_page = page_break(posts, page).get("number_of_page")

    return render_template(
        "admin/manage_post.html", posts=page_posts, page_number=number_of_page
    )


@admin_bp.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        category = Category.query.get(form.category.data)
        body = form.body.data
        post = Post(title=title, category=category, body=body)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for("user.show_post", post_id=post.id))
    return render_template("admin/new_post.html", form=form)


@admin_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for("user.show_post", post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template("admin/edit_post.html", form=form)


@admin_bp.route("/category/manage")
@login_required
def manage_category():
    categories = Category.query.all()

    return render_template("admin/manage_category.html", categories=categories)


@admin_bp.route("/category/new")
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("admin.manage_category"))
    return render_template("admin/new_category", form=form)


@admin_bp.route("/category/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get(category_id)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        return redirect(url_for("admin.manage_category"))
    form.name.data = category.name
    return render_template("admin/edit_category.html", form=form)


@admin_bp.route("/category/<int:category_id>/delete", methods=["GET", "POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        return redirect(url_for("admin.manage_category"))
    category.delete()
    return redirect(url_for("admin.manage_category"))


@admin_bp.route("/message/manage")
@login_required
def manage_message():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    message_count = len(messages)
    page = request.args.get("page")

    page_messages = page_break(messages, page).get("page_items")
    number_of_page = page_break(messages, page).get("number_of_page")

    return render_template(
        "admin/manage_message.html",
        messages=page_messages,
        message_count=message_count,
        page_number=number_of_page,
    )


@admin_bp.route("/message/<message_id>/delete", methods=["GET", "POST"])
@login_required
def delete_message(message_id):
    message = Message.query.get(message_id)
    db.session.delete(message)
    db.session.commit()
    return redirect_back()


@admin_bp.route("/project/manage")
@login_required
def manage_project():
    projects = Project.query.order_by(Project.timestamp.desc()).all()

    return render_template("admin/manage_project.html", projects=projects)


@admin_bp.route("/project/<int:project_id>/delete", methods=["GET", "POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get(project_id)

    db.session.delete(project)
    db.session.commit()

    return redirect_back()


@admin_bp.route("/project/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    form = ProjectForm()
    project = Project.query.get(project_id)
    if form.validate_on_submit():
        project.title = form.title.data
        project.url = form.url.data
        project.body = form.body.data
        db.session.commit()
        return redirect(url_for("user.show_posts"))
    form.title.data = project.title
    form.url.data = project.url
    form.body.data = project.body
    return render_template("admin/edit_project.html", form=form)


@admin_bp.route("/project/new", methods=["GET", "POST"])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        title = form.title.data
        url = form.url.data
        body = form.body.data

        project = Project(title=title, url=url, body=body)
        db.session.add(project)
        db.session.commit()

        return redirect(url_for("user.show_projects"))
    return render_template("admin/new_project.html", form=form)
