import hashlib
from typing import Dict
from pymysql import Connection
from pymysql.cursors import Cursor, DictCursor

from .abs_table import AbsTableHandler, AbsSqlStmtHolder


class UserStmts(AbsSqlStmtHolder):

    @property
    def create_db(self) -> str: return """
        create table IF NOT EXISTS G01.User (
            id              int auto_increment                  primary key,
            username    varchar(128)                        not null,
            password_hash   varchar(128)                        not null,
            last_login_time timestamp default CURRENT_TIMESTAMP not null,
            constraint      User_username_uindex            unique (username)
        );
    """

    @property
    def insert_new_user(self) -> str: return """
        INSERT INTO G01.User(username, password_hash)
        VALUE (%(username)s, %(password_hash)s)
    """

    @property
    def select_user_by_id(self) -> str: return """
        SELECT id, username FROM G01.User
        WHERE id = %(id)s
    """
    
    @property
    def select_user_by_username(self) -> str: return """
        SELECT id, username FROM G01.User
        WHERE username = %(username)s
    """

    @property
    def whether_is_empty(self) -> str: return """
        SELECT 1 FROM G01.User
        LIMIT 1
    """

    @property
    def whether_username_exist(self) -> str: return """
        SELECT 1 FROM G01.User
        WHERE username = %(username)s
        LIMIT 1
    """

    @property
    def whether_username_match_password(self) -> str: return """
        SELECT 1 FROM G01.User
        WHERE username = %(username)s 
            AND password_hash = %(password_hash)s
        LIMIT 1
    """


class UserTable(AbsTableHandler):

    def __init__(self, connection: Connection):
        super().__init__(connection, UserStmts())

    @property
    def _stmts(self) -> UserStmts:
        holder = super(UserTable, self)._stmts
        if not isinstance(holder, UserStmts): raise TypeError("IMPOSSIBLE")
        return holder

    def register(self, username: str, password: str) -> None:
        password_hash = hashlib.sha224(str.encode(password)).hexdigest()
        with self._db_connection.cursor(Cursor) as cursor: 
            cursor.execute(
                query=self._stmts.insert_new_user, 
                args={'username': username, 'password_hash': password_hash}
            )
        self._db_connection.commit()
        return None

    def get_user_by_id(self, id: int) -> Dict: 
        with self._db_connection.cursor(DictCursor) as cursor:
            cursor.execute(self._stmts.select_user_by_id, {"id": id})
            return cursor.fetchone()
    
    def get_user_by_username(self, username: int) -> Dict: 
        with self._db_connection.cursor(DictCursor) as cursor:
            cursor.execute(self._stmts.select_user_by_username, {"username": username})
            return cursor.fetchone()
    
    def contains(self, username: str) -> bool: 
        with self._db_connection.cursor(Cursor) as cursor: 
            cursor.execute(self._stmts.whether_username_exist, args={'username': username})
            return cursor.fetchone() is not None
    
    def is_empty(self) -> bool: 
        with self._db_connection.cursor(Cursor) as cursor: 
            cursor.execute(self._stmts.whether_is_empty)
            return cursor.fetchone() is None

    def is_correct_password(self, username: str, password: str) -> bool:
        password_hash = hashlib.sha224(str.encode(password)).hexdigest()
        with self._db_connection.cursor(Cursor) as cursor: 
            cursor.execute(
                query=self._stmts.whether_username_match_password, 
                args={'username': username, 'password_hash': password_hash}
            )
            return cursor.fetchone() is not None
