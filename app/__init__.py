import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from app.config import TestingConfig

db: SQLAlchemy = SQLAlchemy()
login_manager = LoginManager()

def create_app(config=TestingConfig):
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app

@login_manager.user_loader
def load_user(user_id):
    from models import User 
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalars().first()
    return user
