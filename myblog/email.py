import os
from flask_mail import Message
from flask import render_template

from myblog.extensions import mail


def send_new_post_mail(subject, to, **kwargs):
    message = Message(
        subject,
        recipients=to,
        sender="gaotianchi <%s>" % os.getenv("MAIL_USERNAME"),
    )
    message.body = render_template("email/subscribe.txt", **kwargs)
    mail.send(message)
