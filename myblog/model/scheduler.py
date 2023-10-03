from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from myblog.model.item import MdTextReader, TempData


class FileTrigger(PatternMatchingEventHandler):
    def __init__(
        self,
        app: Flask,
        patterns=["*.md"],
        ignore_patterns=[".*"],
        ignore_directories=True,
        case_sensitive=True,
    ):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.logger = app.logger
        self.temp = TempData(app)

    def on_any_event(self, event):
        if event.event_type in ["created", "modified"]:
            self.logger.info(f"{event.event_type}: {event.src_path}.")
            self.temp.add_to_update(event.src_path)


class Watcher:
    def __init__(self, app: Flask) -> None:
        self.app = app

        self.trigger = FileTrigger(app)
        self.observer = Observer()

    def run(self):
        self.app.logger.info("启动文件监视器")
        self.observer.schedule(
            event_handler=self.trigger,
            path=self.app.config["WATCH_DIR"],
            recursive=True,
        )

        self.observer.start()


class Scheduler:
    def __init__(self, app: Flask) -> None:
        self.app = app

        self.watcher = Watcher(app)
        self.scheduler = BackgroundScheduler()
        self.temp = TempData(app)

    def __job_1(self):
        post_paths = self.temp.posts_to_update
        if post_paths:
            for path in post_paths:
                md_text_reader = MdTextReader(self.app, path)
                self.app.logger.info(f"正在读取 {post_paths} ...")

    def run(self):
        self.app.logger.info("启动定时任务")
        self.watcher.run()

        self.scheduler.add_job(func=self.__job_1, trigger="interval", seconds=30)

        self.scheduler.start()
