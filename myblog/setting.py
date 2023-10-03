import os

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig:
    # 环境变量
    SECRET_KEY = os.getenv("SECRET_KEY")

    # 配置默认路径
    LOG_DIR = os.path.join(basedir, "logs")
    DATA_DIR = os.path.join(basedir, "data")
    WATCH_DIR = os.path.join(basedir, *["data", "posts"])

    for path in [LOG_DIR, DATA_DIR, WATCH_DIR]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    FLASK_HOST = os.getenv("DEV_HOST")
    FLASK_PORT = os.getenv("DEV_PORT")
    DEBUG = True


config = {"development": DevelopmentConfig}
