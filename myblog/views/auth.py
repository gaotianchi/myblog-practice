from flask import Blueprint, redirect, render_template, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user

from myblog.forms import LoginForm
from myblog.models import Admin
from myblog.utlis import redirect_back


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user.home"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash("登录成功！欢迎 %s " % username)
                return redirect_back()
            flash("用户名或者密码错误！")
        else:
            flash("账户不存在！")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect_back()
