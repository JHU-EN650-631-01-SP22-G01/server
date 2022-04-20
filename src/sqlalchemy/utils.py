from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, json, uuid

from .user import UserDbModel
from .shared import db_manager

def init_dbmanager(
    app: Flask, 
    db_uri: Optional[str] = None, 
    init_json: Optional[str] = None
) -> SQLAlchemy:
    if db_uri is None or len(db_uri) == 0: 
        db_uri = 'sqlite:///'+ os.path.join(app.root_path,'data.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db_manager.init_app(app)
    with app.app_context():
        db_manager.create_all()
        if init_json is None: return db_manager
        for data in json.loads(init_json): 
            if UserDbModel.find(by_uname=data['username']) is not None: continue
            new_user = UserDbModel(id=uuid.uuid4().hex, username=data['username'])
            new_user.set_password(data['password'])
            db_manager.session.add(new_user)
        db_manager.session.commit()
    return db_manager


def is_correct(username: str, password: str) -> bool: 
    user:UserDbModel = UserDbModel.find(by_uname=username)
    return user is not None and user.validate_password(password)
    

