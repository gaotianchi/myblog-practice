import os


from dotenv import load_dotenv


load_dotenv()


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    WORKSPACE = os.path.join(basedir, "data")

    LOGS_PATH = os.path.join(basedir, "logs")
