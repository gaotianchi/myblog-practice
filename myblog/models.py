from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from myblog.extensions import db


class Admin(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    password_hash = Column(String(128))
    blog_title = Column(String(60))
    blog_sub_title = Column(String(100))
    about = Column(Text)


class Category(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True)

    posts = relationship("Post", back_populates="category")


class Post(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category", back_populates="posts")

    messages = relationship("Messageboard", back_populates="post")


class Messageboard(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(254))
    site = Column(String(255))
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", back_populates="messages")


class Project(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
