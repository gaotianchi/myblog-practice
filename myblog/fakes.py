import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from myblog.models import Admin, Category, Post, Messageboard, Project
from myblog.extensions import db


fake = Faker("zh-cn")


def fake_admin():
    admin = Admin(
        username="gaotianchi",
        blog_title="高天驰的个人博客",
        blog_sub_title="为了玩乐和找工作",
        about="我叫高天驰，爱好户外徒步、编程和电影。",
    )
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name="Default")
    db.session.add(category)

    for _ in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for _ in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year(),
        )
        db.session.add(post)
    db.session.commit()


def fake_messages(count=100):
    for _ in range(count):
        message = Messageboard(
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(message)
    db.session.commit()


def fake_projects(count=3):
    for _ in range(count):
        project = Project(
            title=fake.sentence(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
        )
        db.session.add(project)
    db.session.commit()
