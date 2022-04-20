from flask import Flask
from flask_login import LoginManager, logout_user, login_required, login_user, logout_user, current_user
from .user import UserSession

login_manager = LoginManager()

@login_manager.user_loader
def load_user(uid):
    return UserSession.get(by_uid=uid)

def init_manager(app: Flask) -> LoginManager:
    login_manager.init_app(app)
    return login_manager

