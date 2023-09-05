from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail


db = SQLAlchemy()
ckeditor = CKEditor()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    from myblog.models import Admin

    user = db.session.get(Admin, int(user_id))
    return user
