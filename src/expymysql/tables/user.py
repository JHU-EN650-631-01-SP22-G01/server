import hashlib
from pymysql import Connection
from pymysql.cursors import Cursor

from .abs_table import AbsTableHandler, AbsSqlStmtHolder


class UserStmts(AbsSqlStmtHolder):

    @property
    def create_db(self) -> str: return """
        create table IF NOT EXISTS main.User (
            id              int auto_increment                  primary key,
            account_name    varchar(128)                        not null,
            password_hash   varchar(128)                        not null,
            last_login_time timestamp default CURRENT_TIMESTAMP not null,
            constraint      User_account_name_uindex            unique (account_name)
        );
    """

    @property
    def insert_new_user(self) -> str: return """
        INSERT INTO main.User(account_name, password_hash)
        VALUE (%(account_name)s, %(password_hash)s)
    """

    @property
    def whether_username_match_password(self) -> str: return """
        SELECT 1 FROM main.User
        WHERE account_name = %(account_name)s 
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

    def register(self, account_name: str, password: str) -> None:
        password_hash = hashlib.sha224(str.encode(password)).hexdigest()
        with self._db_connection.cursor(Cursor) as cursor: 
            cursor.execute(
                query=self._stmts.insert_new_user, 
                args={'account_name': account_name, 'password_hash': password_hash}
            )
        self._db_connection.commit()
        return None

    def is_correct_password(self, account_name: str, password: str) -> bool:
        password_hash = hashlib.sha224(str.encode(password)).hexdigest()
        with self._db_connection.cursor(Cursor) as cursor: 
            cursor.execute(
                query=self._stmts.whether_username_match_password, 
                args={'account_name': account_name, 'password_hash': password_hash}
            )
            return cursor.fetchone() is not None
