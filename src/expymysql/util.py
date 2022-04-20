import os, json 
from flask import Flask
from typing import Optional
from .user_table_builder import UserTableBuilder
from .tables.user import UserTable, UserStmts


def init_dbmanager(
    app: Flask, 
    init_json: Optional[str] = None
) -> UserTable:
    db_uri, db_port = os.environ.get('DB_URI'), os.environ.get('DB_PORT')
    db_account, db_password = os.environ.get('DB_ACCOUNT'), os.environ.get('DB_PASSWORD')
    db_manager = UserTableBuilder().host(db_uri).port(db_port).username(db_account).password(db_password).build()
    with app.app_context():
        db_manager.create_all()
        if init_json is None: return db_manager
        for data in json.loads(init_json): 
            db_manager.register(data['username'], data['password'])
        db_manager.flash()
    return db_manager


def is_correct(username: str, password: str) -> bool: 
    user:UserDbModel = UserDbModel.find(by_uname=username)
    return user is not None and user.validate_password(password)