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

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_FILE_UPLOADER = "admin.upload_image"

    BLUELOG_UPLOAD_PATH = os.path.join(basedir, "uploads")
    BLUELOG_ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", prefix + os.path.join(basedir, "data.db")
    )
