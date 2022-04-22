from __future__ import annotations
from flask_login import UserMixin
from ..expymysql import utils as db_utils


class UserSession(UserMixin):

    def __init__(self, id: str, username: str):
        self.__id = id
        self.__username = username

    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def is_active(self):
        return True

    def get_id(self) -> str:
        return self.__id
    
    @property
    def name(self) -> str: 
        return self.__username

    @classmethod
    def get_by_id(cls, id: str) -> UserSession: 
        db_user = db_utils.tables.users.get_user_by_id(id)
        return UserSession(db_user['id'], db_user['username'])

    @classmethod 
    def get_by_username(cls, username: str) -> UserSession: 
        db_user = db_utils.tables.users.get_user_by_username(username)
        return UserSession(db_user['id'], db_user['username'])