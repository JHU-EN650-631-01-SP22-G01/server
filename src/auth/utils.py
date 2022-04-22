from flask import Flask
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from .user import UserSession

login_manager = LoginManager()

@login_manager.user_loader
def load_user_by_id(uid):
    return UserSession.get_by_id(uid)

def load_user_by_name(uname):
    return UserSession.get_by_username(uname)

def init_manager(app: Flask, login_route: str) -> LoginManager:
    login_manager.init_app(app)
    login_manager.login_view = login_route
    return login_manager
