from flask import Flask, render_template
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import os
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'games.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db: SQLAlchemy = SQLAlchemy(app)

class User(db.Model):  
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(20))


class Movie(db.Model): 
    __tablename__ = "my_favorite_movies"
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(60))  
    year = db.Column(db.String(4))

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/user/<name>')
def user_page(name):
    return f'User page for: {escape(name)}'

@app.route('/movies')
def movies():
    stmnt = db.select(Movie)
    result = db.session.execute(stmnt).scalars().all()
    return render_template('movies.html', name=name, movies=result)

@app.route('/games')
def games():
    stmnt = db.select(GameDetails.name, GameDetails.released)
    result = db.session.execute(stmnt).fetchmany(10)
    print(result)
    return render_template('games.html', name=name, game_details=result)


name = 'Evan Carlile'
movies_data = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]

with app.app_context():
    class GameDetails(db.Model):
        __table__ = db.Table('game_details', db.metadata, autoload_with=db.engine)

    class GamesPlatforms(db.Model):
        __table__ = db.Table("games_platforms", db.metadata, autoload_with=db.engine)


if __name__ == '__main__':
    app.run(debug=True)