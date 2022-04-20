from __future__ import annotations
from typing import Optional
from .tables.user import UserTable
import expymysql

class UserTableBuilder(object):

    def __init__(self):
        self.__host: Optional[str] = None
        self.__port: Optional[int] = None
        self.__username: Optional[str] = None
        self.__password: Optional[str] = None

    def host(self, new_val: str) -> UserTableBuilder: 
        self.__host = new_val
        return self

    def port(self, new_val: int) -> UserTableBuilder: 
        self.__port = new_val
        return self
    
    def username(self, new_val: str) -> UserTableBuilder: 
        self.__username = new_val
        return self
    
    def password(self, new_val: str) -> UserTableBuilder: 
        self.__password = new_val
        return self

    def build(self) -> UserTable: 
        main_connection = expymysql.connect(
            host=self.__host, port=self.__port, 
            user=self.__username, password=self.__password,
            cursorclass=expymysql.cursors.DictCursor
        )
        return UserTable(main_connection)
