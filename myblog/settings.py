import os
import sys

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default")

    NUMBER_POST_PER_PAGE = 10

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", prefix + os.path.join(basedir, "data.db")
    )
