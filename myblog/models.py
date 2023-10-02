from datetime import datetime
import os

import redis
from redis.client import Pipeline
import yaml
from flask import Flask
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apscheduler.schedulers.background import BackgroundScheduler


from myblog.utils import get_content, get_ymal, md_content_to_html

POOL = redis.ConnectionPool(
    host="127.0.0.1", port=6379, max_connections=100, decode_responses=True
)

conn = redis.Redis(connection_pool=POOL)


class MyEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

    def on_any_event(self, event):
        filename = os.path.basename(event.src_path)
        if event.is_directory:
            return None
        elif (event.event_type == "created") or (event.event_type == "modified"):
            if str(event.src_path).endswith(".md") and filename != "home.md":
                conn.sadd("modified", event.src_path)

        elif event.event_type == "deleted":
            if str(event.src_path).endswith(".md") and filename != "home.md":
                conn.sadd("deleted", event.src_path)


class Watcher:
    def __init__(self, app: Flask):
        self.observer = Observer()
        self.app = app

    def run(self):
        self.app.logger.info("启动文件监视器")
        event_handler = MyEventHandler()
        self.observer.schedule(
            event_handler, self.app.config["WORKSPACE"], recursive=True
        )
        self.observer.start()


class Schedule:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.post_updater = PostUpdater(self.app)

    def _update_post(self):
        count = conn.scard("modified")
        if count > 0:
            self.app.logger.info(f"共有{count}个文章等待更新")
            for _ in range(count):
                post_path = conn.spop("modified")

                self.app.logger.info(f"正在更新 {os.path.basename(post_path)}")
                self.post_updater.set_post(post_path)
                self.post_updater.update()
                self.app.logger.info(f"更新完成 {os.path.basename(post_path)}")

    def run(self):
        self.app.logger.info("启动定时更新程序")
        self.scheduler.add_job(self._update_post, trigger="interval", seconds=30)
        self.scheduler.start()


class PostUpdater:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.post = Post(app)

    def set_post(self, path: str):
        self.post._path = path

        with open(path, mode="r", encoding="UTF-8") as f:
            md = f.read()
        self.post._content = md

    def update(self):
        self.__set_metadata()
        self.__update_metadata()

    def __set_metadata(self):
        default_date = datetime.now().strftime("%Y%m%d")
        default_category = os.path.dirname(self.post._path)

        metadata_dict: dict = yaml.safe_load(get_ymal(self.post._content))
        if not metadata_dict:
            metadata_dict = {}
        date = metadata_dict.get("date", "")
        self.post._author = metadata_dict.get("author", "高天驰")
        if date:
            d = datetime.strptime(str(date), "%Y-%m-%d")
            self.post._date = d.strftime("%Y%m%d")
        else:
            self.post._date = default_date

        self.post._tags = metadata_dict.get("tags", ["默认"])
        self.post._category = metadata_dict.get("category", default_category)

        self.post._title = (
            str(os.path.basename(self.post._path)).replace(" ", "").replace(".md", "")
        )

    def __update_metadata(self):
        self.app.logger.info(f"开始更新文章{self.post.title}的元数据")

        pipe = conn.pipeline()
        self.__update_recently(pipe)
        self.__update_tags(pipe)
        self.__update_category(pipe)
        self.__update_author(pipe)
        self.__update_path(pipe)
        pipe.execute()

    def __update_path(self, pipe: Pipeline):
        pipe.set(f"{self.post._title}:path", self.post._path)

    def __update_recently(self, pipe: Pipeline):
        self.app.logger.info("正在更新日期")
        date = int(self.post._date)

        name = "post:recently"
        mapping = {self.post._title: date}
        pipe.zadd(name, mapping)

        pipe.set(f"{self.post._title}:date", str(date))

    def __update_tags(self, pipe: Pipeline):
        self.app.logger.info("正在更新标签")
        tags = self.post._tags
        name = f"{self.post._title}:tag"

        pipe.sadd(name, *tags)

    def __update_category(self, pipe: Pipeline):
        self.app.logger.info("正在更新分类")

        name = f"{self.post._title}:category"

        pipe.set(name, self.post._category)

    def __update_author(self, pipe: Pipeline):
        self.app.logger.info("正在更新作者")

        pipe.set(f"{self.post._title}:author", self.post._author)


class Post:
    def __init__(self, app: Flask) -> None:
        self.logger = app.logger
        self._path = None
        self._content = None
        self._author = None
        self._title = None
        self._date = None
        self._category = None
        self._tags = None

    def init_post_by_title(self, title: str):
        self.logger.info(f"正在实例化文章 {title}")
        self._title = title

        pipe = conn.pipeline()

        self._author = pipe.get(f"{self._title}:author")
        self._category = pipe.get(f"{self._title}:category")
        self._tags = pipe.smembers(f"{self._title}:tags")
        self._path = pipe.get(f"{self._title}:path")

        pipe.execute()
        self._date = self.__formated_date()

    def __formated_date(self):
        date: str = conn.get(f"{self._title}:date")
        d = datetime.strptime(date, "%Y%m%d")

        return d.strftime("%Y/%m/%d")

    @property
    def date(self):
        return self._date

    @property
    def title(self):
        return self._title

    @property
    def html_content(self):
        with open(self._path, mode="r", encoding="UTF-8") as f:
            md = f.read()

        return md_content_to_html(get_content(md))
