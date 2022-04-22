import os, pymysql, logging
from typing import Optional
from .user import UserTable
from .article import ArticleTable


class __TableBuilder(object):

    def __init__(self):
        host = os.environ.get('DB_URI')
        port = os.environ.get('DB_PORT')
        user = os.environ.get('DB_ACCOUNT')
        password = os.environ.get('DB_PASSWORD')
        self.__post_connection = pymysql.connect(
            host=host, port=int(port), user=user, password=password,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.__main_connection = pymysql.connect(
            host=host, port=int(port), user=user, password=password,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.__article_tb: Optional[ArticleTable] = None
        self.__author_tb: Optional[AuthorTable] = None
        self.__user_tb: Optional[UserTable] = None

    @property
    def article(self) -> ArticleTable:
        if self.__article_tb is None:
            self.__article_tb = ArticleTable(self.__post_connection)
        return self.__article_tb

    @property
    def author(self) -> AuthorTable:
        if self.__author_tb is None:
            self.__author_tb = AuthorTable(self.__post_connection)
        return self.__author_tb

    @property
    def user(self) -> UserTable:
        if self.__user_tb is None:
            self.__user_tb = UserTable(self.__main_connection)
        return self.__user_tb

try:
    tables = __TableBuilder()
except TypeError as error:
    logging.exception('CANNOT INITIALISE SERVER, PLEASE CHECK THE CORRECTION OF THE ".env" FILE.')
    exit()
