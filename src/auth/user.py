from __future__ import annotations
from typing import Optional
from flask_login import UserMixin
from ..sqlalchemy import UserDbModel


class UserSession(UserMixin):

    def __init__(self, uname: str, db_user: Optional[UserDbModel]=None):
        self.__db_user= db_user if db_user is not None else UserDbModel.find(by_uname=uname)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def is_active(self):
        return True

    def get_id(self) -> str:
        return self.__db_user.id

    @property
    def db_orc(self) -> UserDbModel: 
        return self.__db_user
    
    @property
    def name(self) -> str: 
        return self.__db_user.username

    @classmethod
    def get(cls, by_uid: str) -> UserSession: 
        db_user = UserDbModel.find(by_uid=by_uid)
        return UserSession(db_user.username, db_user)
