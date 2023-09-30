from urllib import parse
from flask import url_for

import markdown


def md_to_html(filename: str) -> str:
    with open(filename, mode="r", encoding="UTF-8") as f:
        md = f.read()
    html = markdown.markdown(md)

    return html
