from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model): 
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(60))  
    year = db.Column(db.String(4))

class GameDetails(db.Model):
    __tablename__ = "game_details"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String)
    name = db.Column(db.String)
    description = db.Column(db.String)
    metacritic = db.Column(db.Integer)
    released = db.Column(db.String)
    website = db.Column(db.String)

# class GamesPlatforms(db.Model):
#     __table__ = db.Table("game_platforms", db.metadata, autoload_with=db.engine)
    