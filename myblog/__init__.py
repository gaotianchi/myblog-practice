import click

from flask import Flask, render_template
from sqlalchemy import select
from flask_wtf.csrf import CSRFError
from myblog.fakes import fake_subscribers

from myblog.settings import Config
from myblog.extensions import db, ckeditor, login_manager, csrf, mail
from myblog.views import user_bp, admin_bp, auth_bp
from myblog.models import Admin, Category


def create_app():
    app = Flask("myblog")
    app.config.from_object(Config)

    register_blueprint(app)
    register_extensions(app)
    register_commands(app)
    register_template_context(app)
    register_errors(app)

    return app


def register_extensions(app: Flask):
    db.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)


def register_blueprint(app: Flask):
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)


def register_commands(app: Flask):
    @app.cli.command()
    @click.option("--username", prompt=True, help="该用户名用于登录")
    @click.option(
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="登陆密码",
    )
    def init(username, password):
        click.echo("正在初始化数据库...")
        db.create_all()

        admin = db.session.execute(select(Admin)).scalar()
        if admin is not None:
            click.echo("管理员已经存在，正在更新中...")
            admin.username = username
            admin.set_password(password)
        else:
            click.echo("创建临时管理员账号...")
            admin = Admin(
                username=username,
                blog_title="高天驰的个人博客",
                blog_sub_title="为了找工作和玩乐",
                about="我叫高天驰，爱好户外、编程和电影",
            )
            admin.set_password(password)
            db.session.add(admin)

        category = db.session.execute(select(Category)).scalar()
        if category is None:
            click.echo("正在创建默认分类...")
            category = Category(name="默认")
            db.session.add(category)

        db.session.commit()
        click.echo("完成.")

    @app.cli.command()
    @click.option("--category", default=10, help="分类的数量，默认是10个")
    @click.option("--post", default=50, help="文章的数量，默认是50篇文章")
    @click.option("--message", default=100, help="留言数量，默认是100个")
    @click.option("--project", default=3, help="项目数量，默认是3个")
    @click.option("--subscriber", default=3, help="订阅者数量，默认是3个")
    def forge(category, post, message, project, subscriber):
        from myblog.fakes import (
            fake_admin,
            fake_posts,
            fake_messages,
            fake_categories,
            fake_projects,
        )

        db.drop_all()
        db.create_all()

        click.echo("生成管理员...")
        fake_admin()

        click.echo("生成 %d 个分类..." % category)
        fake_categories()

        click.echo("生成 %d 篇文章..." % post)
        fake_posts()

        click.echo("生成 %d 个留言..." % message)
        fake_messages()

        click.echo("生成 %d 个项目..." % project)
        fake_projects()

        click.echo("生成 %d 个订阅者..." % subscriber)
        fake_subscribers()

        click.echo("完成！")


def register_template_context(app: Flask):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        return dict(admin=admin)


def register_errors(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template("errors/400.html", description=e.description), 400
