import re
from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def redirect_back(default="user.home", **kwargs):
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["BLUELOG_ALLOWED_IMAGE_EXTENSIONS"]
    )


def page_break(total_items, current_page=1, number_per_page=10):
    if not current_page:
        current_page = 1
    start = number_per_page * (int(current_page) - 1)
    end = start + number_per_page

    page_items = total_items[start:end]

    if len(total_items) % number_per_page == 0:
        number_of_page = len(total_items) // number_per_page
    else:
        number_of_page = (len(total_items) // number_per_page) + 1

    return dict(page_items=page_items, number_of_page=number_of_page)


# as per recommendation from @freylis, compile once only


def cleanhtml(raw_html) -> str:
    pattern = re.compile("<.*?>")
    cleantext = re.sub(pattern, "", raw_html)
    return cleantext
