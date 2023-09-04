from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from myblog.extensions import db


class Admin(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    password_hash = Column(String(128))
    blog_title = Column(String(60))
    blog_sub_title = Column(String(100))
    about = Column(Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True)

    posts = relationship("Post", back_populates="category")

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    mention = Column(Integer, default=0)

    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category", back_populates="posts")

    messages = relationship("Message", back_populates="post")


class Message(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(254))
    site = Column(String(255))
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", back_populates="messages")

    def update_post(self):
        if self.post.id:
            self.post.mention += 1


class Project(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    body = Column(Text)
    url = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
