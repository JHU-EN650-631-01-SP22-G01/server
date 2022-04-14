from flask_sqlalchemy import SQLAlchemy

db_manager: SQLAlchemy = SQLAlchemy()
db_model = db_manager.Model
