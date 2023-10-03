import logging
import os
from logging.handlers import RotatingFileHandler

import click
from flask import Flask

from myblog.api.resource import api
from myblog.model import pool
from myblog.setting import config


def create_app(config_name: str = "development"):
    app = Flask("myblog")
    app.config.from_object(config[config_name])

    Register.register(app)

    return app


class Register:
    @classmethod
    def register(cls, app: Flask):
        cls.app = app

        cls.__register_blueprint(cls)
        cls.__register_logger(cls)
        cls.__register_command(cls)

    def __register_logger(cls):
        formatter = logging.Formatter(
            "[%(asctime)s]-[%(module)s]-[%(lineno)d]-[%(funcName)s]-[%(levelname)s]-[%(message)s]"
        )
        handler = RotatingFileHandler(
            os.path.join(cls.app.config["LOG_DIR"], "myblog.log"),
            mode="a",
            maxBytes=10 * 1024,
            backupCount=3,
            encoding="UTF-8",
        )
        handler.setFormatter(formatter)
        cls.app.logger.addHandler(handler)
        cls.app.logger.setLevel(logging.DEBUG)

    def __register_blueprint(cls):
        cls.app.register_blueprint(api)

    def __register_command(cls):
        @cls.app.cli.command(help="初始化用户数据")
        @click.option("--post", is_flag=True, help="只删除文章")
        def init(post):
            click.confirm("确定要清除所有数据吗？")
            import shutil

            import redis

            conn = redis.Redis(connection_pool=pool)

            conn.flushall()
            click.echo("成功清除 redis 中的所有数据!")

            path = cls.app.config["DATA_DIR"]
            if post:
                path = cls.app.config["WATCH_DIR"]

            try:
                shutil.rmtree(path)
                click.echo("成功清除工作区中的数据！")
            except:
                click.echo("工作区中的数据未成功清除，请手动清除数据！")
            finally:
                os.makedirs(path)
