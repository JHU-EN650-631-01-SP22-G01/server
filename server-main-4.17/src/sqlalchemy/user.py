from __future__ import annotations
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from .shared import db_manager as db, db_model

class UserDbModel(db_model):

    __tablename__= 'UserTable'

    id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    db.UniqueConstraint(username)
    password_hash = db.Column(db.String(128), nullable=False) 
    

    def set_password(self, password): 
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password): 
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def find(
        by_uid: Optional[str]=None, 
        by_uname: Optional[str]=None
    ) -> Optional[UserDbModel]: 
        if by_uid is not None: 
            return UserDbModel.query.filter_by(id=by_uid).first()
        elif by_uname is not None: 
            return UserDbModel.query.filter_by(username=by_uname).first()
        else: 
            return None
        
        
