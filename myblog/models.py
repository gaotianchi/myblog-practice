from datetime import datetime
from turtle import st

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from myblog.extensions import db


class Admin(db.Model, UserMixin):
    """管理员模型"""

    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    password_hash = Column(String(128))
    blog_title = Column(String(60))
    blog_sub_title = Column(String(100))
    about = Column(Text)

    def set_password(self, password: str):
        """将明文密码转化为加密的字符串"""
        self.password_hash: str = generate_password_hash(password)

    def validate_password(self, password: str):
        """检测输入的明文密码与加密字符串是否匹配"""
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    """分类模型"""

    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True)

    posts = relationship("Post", back_populates="category")

    def delete(self):
        """删除分类时将分类下的物品放在默认分类下"""
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    """文章模型"""

    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    mention = Column(Integer, default=0)

    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship("Category", back_populates="posts")

    messages = relationship("Message", back_populates="post")


class Message(db.Model):
    """留言模型"""

    id = Column(Integer, primary_key=True)
    email = Column(String(254))
    site = Column(String(255))
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post", back_populates="messages")

    def update_post(self):
        """更新目标文章的留言次数"""
        if self.post_id:
            post = Post.query.get_or_404(self.post_id)
            post.mention += 1
            db.session.commit()


class Project(db.Model):
    """项目模型"""

    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    body = Column(Text)
    url = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Subscriber(db.Model):
    """订阅者模型"""

    id = Column(Integer, primary_key=True)
    email = Column(String(60))
    timestamp = Column(DateTime, default=datetime.utcnow)
