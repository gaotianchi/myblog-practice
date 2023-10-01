from datetime import datetime
import os

import redis
import yaml
from flask import Flask
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apscheduler.schedulers.background import BackgroundScheduler


from myblog.utils import get_ymal

POOL = redis.ConnectionPool(
    host="127.0.0.1", port=6379, max_connections=100, decode_responses=True
)

conn = redis.Redis(connection_pool=POOL)


class MyEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

    def on_any_event(self, event):
        if event.is_directory:
            return None
        elif (event.event_type == "created") or (event.event_type == "modified"):
            conn.sadd("modified", event.src_path)

        elif event.event_type == "deleted":
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
        self.post_updater = PostUpdater()

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
    def set_post(self, path: str):
        self._path = path
        with open(path, mode="r", encoding="UTF-8") as f:
            md = f.read()
        self.post = md

    def update(self):
        self.__update_metadata()

    def __get_metadata(self):
        default_date = datetime.now().strftime("%Y%m%d")

        metadata_dict: dict = yaml.safe_load(get_ymal(self.post))
        if not metadata_dict:
            metadata_dict = {}
        date = metadata_dict.get("date", "")
        if date:
            d = datetime.strptime(str(date), "%Y-%m-%d")
            date = d.strftime("%Y%m%d")
        else:
            date = default_date

        tags = metadata_dict.get("tags", ["默认"])

        return dict(date=date, tags=tags)

    def __update_metadata(self):
        self.__update_recently()
        self.__update_tags()

    def __update_recently(self):
        metadata_dict = self.__get_metadata()
        post_name = os.path.basename(self._path)
        date = int(metadata_dict["date"])

        name = "post:recently"
        mapping = {post_name: date}
        conn.zadd(name, mapping)

    def __update_tags(self):
        metadata_dict = self.__get_metadata()
        tags = metadata_dict["tags"]
        post_name = os.path.basename(self._path)
        name = f"{post_name}:tag"

        conn.sadd(name, *tags)
