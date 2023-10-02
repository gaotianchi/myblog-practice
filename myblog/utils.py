import re

import markdown
from flask import url_for


def md_file_to_html(filename: str) -> str:
    with open(filename, mode="r", encoding="UTF-8") as f:
        md = format_image_url(f.read())
    html = markdown.markdown(md)

    return html


def md_content_to_html(text):
    result = format_image_url(text)
    return markdown.markdown(result)


def format_image_url(text) -> str:
    pattern = r"!\[\[(.*?)\]\]"

    def replace(match):
        image_name = match.group(1)
        return f"![{image_name}]({url_for('image', image_filename=image_name)})"

    result = re.sub(pattern, replace, text)
    return result


def get_ymal(text: str) -> str:
    pattern = r"---\n(.+?)\n---"

    matches = re.findall(pattern, text, re.DOTALL)

    return matches[0] if matches else ""


def get_content(text: str) -> str:
    pattern = r"---\n.*?\n---\n(.*)"
    match = re.search(pattern, text, re.DOTALL)

    return match.group(1) if match else ""


if __name__ == "__main__":
    pass
