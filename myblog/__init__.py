import click

from flask import Flask

from myblog.settings import Config
from myblog.extensions import db, ckeditor
from myblog.views import user_bp, admin_bp, auth_bp


def create_app():
    app = Flask("myblog")
    app.config.from_object(Config)

    register_blueprint(app)
    register_extensions(app)
    register_commands(app)

    return app


def register_extensions(app: Flask):
    db.init_app(app)
    ckeditor.init_app(app)


def register_blueprint(app: Flask):
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)


def register_commands(app: Flask):
    @app.cli.command()
    @click.option("--category", default=10, help="分类的数量，默认是10个")
    @click.option("--post", default=50, help="文章的数量，默认是50篇文章")
    @click.option("--message", default=100, help="留言数量，默认是100个")
    @click.option("--project", default=3, help="项目数量，默认是3个")
    def forge(category, post, message, project):
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

        click.echo("完成！")
