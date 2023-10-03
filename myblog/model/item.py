import os
import re

import redis
import yaml
from flask import Flask

from myblog.model import pool

conn = redis.Redis(connection_pool=pool)


class PersistentData:
    pass


class TempData:
    def __init__(self, app: Flask) -> None:
        self.logger = app.logger

    def add_to_update(self, path: str) -> None:
        conn.sadd("to:update", path)

    @property
    def posts_to_update(self) -> list:
        item_count = conn.scard("to:update")
        if item_count:
            self.logger.info(f"共有 {item_count} 个文章等待更新...")

        return conn.spop("to:update", item_count)


class MdTextReader:
    def __init__(self, app: Flask, path: str) -> None:
        self.logger = app.logger
        self.path = path

        self.__mdtext = self.__read_mdtext()

    def __read_mdtext(self):
        with open(self.path, "r", encoding="UTF-8") as f:
            md_text = f.read()

        if not md_text:
            self.logger.debug(f"检测到[{self.path}]文件为空.")

            return ""

        return md_text

    def __get_metadata(self):
        if not self.__mdtext:
            return ""

        pattern = r"---\n(.*?)\n---"
        match = re.search(pattern, self.__mdtext, re.DOTALL)
        if match:
            yaml_text = match.group(1)
            data = yaml.safe_load(yaml_text)
            self.logger.debug(f"获取{os.path.basename(self.path)}的元数据: {data}")

            return data

    def __get_mdtext_body(self):
        if not self.__mdtext:
            return ""

        pattern = r"---\n.*?\n---(.*)"
        match = re.search(pattern, self.__mdtext, re.DOTALL)
        if match:
            data = match.group(1)
            self.logger.debug(f"获取{os.path.basename(self.path)}的正文: {data[0:100]}...")
            return data

    @property
    def md_metadata(self) -> str:
        return self.__get_metadata()

    @property
    def md_body(self) -> str:
        return self.__get_mdtext_body()


class MetaProcesser:
    def __init__(self, md_metadata: str) -> None:
        self.__metadata = md_metadata

    @property
    def metadata(self) -> str:
        pass


class BodyProcesser:
    def __init__(self, body: str) -> None:
        self.__body = body

    @property
    def body(self) -> str:
        pass


class PostProcesser:
    pass
