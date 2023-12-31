from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    SelectField,
    ValidationError,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, Optional, URL
from flask_ckeditor import CKEditorField

from myblog.models import Category, Post


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField("密码", validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField("记住我")
    submit = SubmitField("登录")


class PostForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(1, 60)])
    category = SelectField("分类", coerce=int, default=1)
    body = CKEditorField("正文", validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name)
            for category in Category.query.order_by(Category.name).all()
        ]


class CategoryForm(FlaskForm):
    name = StringField("名称", validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError("该分类已经存在！")


class ProjectForm(FlaskForm):
    title = StringField("项目名称", validators=[DataRequired(), Length(1, 30)])
    body = TextAreaField("简介", validators=[DataRequired()])
    url = StringField("链接", validators=[Optional(), URL(), Length(0, 255)])
    submit = SubmitField()


class MessageForm(FlaskForm):
    email = StringField(
        "邮箱 *",
        validators=[DataRequired(), Email(), Length(1, 254)],
        render_kw={"placeholder": "你的个人邮箱"},
    )
    body = TextAreaField(
        "留言 *", validators=[DataRequired()], render_kw={"placeholder": "写下你的留言..."}
    )
    site = StringField(
        "个人网址",
        validators=[Optional(), URL(), Length(0, 255)],
        render_kw={"placeholder": "你的个人网址(选填)"},
    )
    post_url = StringField(
        "提及",
        validators=[Optional(), URL(), Length(0, 255)],
        render_kw={
            "placeholder": "你想引用或者评论的[本站]文章完整链接(选填)",
        },
    )
    submit = SubmitField("留言", render_kw={"style": "color: #EC53B0;"})


class SubscribeForm(FlaskForm):
    email = StringField(
        "邮箱",
        validators=[DataRequired(), Email(), Length(1, 254)],
        render_kw={"placeholder": "邮箱"},
    )
    submit = SubmitField("订阅")
