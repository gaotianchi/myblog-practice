from flask import Blueprint, render_template


user_bp = Blueprint("user", __name__)


@user_bp.route("/")
def hello():
    return render_template("base.html")
