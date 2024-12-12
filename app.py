from flask import Flask, render_template, request, redirect, flash, url_for, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import os
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'games.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'

db: SQLAlchemy = SQLAlchemy(app)

class User(db.Model):  
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(20))

class Movie(db.Model): 
    __tablename__ = "my_favorite_movies"
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(60))  
    year = db.Column(db.String(4))

class AddMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    submit = SubmitField('Add')

class DeleteMovieForm(FlaskForm):
    movie_id = HiddenField('Movie ID')
    submit = SubmitField('Delete')


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user_page(name):
    return f'User page for: {escape(name)}'

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    add_movie_form = AddMovieForm()
    delete_movie_form = DeleteMovieForm()

    if request.method == 'POST':
        if add_movie_form.validate_on_submit():
            title = add_movie_form.title.data
            year = add_movie_form.year.data
        
            movie = Movie(title=title, year=year)
            db.session.add(movie)
            db.session.commit()
            flash('Item Created.')
            return redirect(url_for('movies'))
        
        elif delete_movie_form.validate_on_submit():
            print(f'Movie id is: {delete_movie_form.movie_id.data}')
            movie_id = delete_movie_form.movie_id.data
            movie = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalars().first()

            if not movie:
                flash('Movie not found.')
                return redirect(url_for('movies'))

            db.session.delete(movie)
            db.session.commit()
            flash('Item deleted')
            return redirect(url_for('movies'))
        
        elif "edit" in request.form:
            movie_id = request.form.get('movie_id')
            return redirect(url_for('edit', movie_id=movie_id))
        
    elif request.method == "GET":
        return render_template('movies.html', add_movie_form=add_movie_form, delete_movie_form=delete_movie_form)

@app.route('/movies/edit/<int:movie_id>', methods=["GET", "POST"])
def edit(movie_id):
    movie = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalars().first()

    if request.method == "POST":
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year.isdigit() or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
    
        movie.title = title
        movie.year = year
        db.session.commit()

        link = url_for("movies")
        flash(f'Successfully updated! Click <a href={link}>here</a> to return to the movies list.')
        return redirect(url_for('edit', movie_id=movie_id))
    
    if request.method == "GET":
        return render_template('edit.html')


@app.route('/games')
def games():
    games_list_start = []
    games_list = []

    stmnt = db.select(GameDetails.name, GameDetails.released).where(GameDetails.name.like("Metal Gear%"))
    games_list_start.append(db.session.execute(stmnt).fetchmany(3))

    stmnt = db.select(GameDetails.name, GameDetails.released).where(GameDetails.metacritic > 90).order_by(GameDetails.metacritic)
    games_list_start.append(db.session.execute(stmnt).fetchmany(7))

    games_list = [item for sub_list in games_list_start for item in sub_list]

    print(games_list)
    return render_template('games.html', game_details=games_list)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html')

@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html')

# To force a 500 http error for testing
# @app.route('/force500')
# def force_500():
#     abort(500)

@app.context_processor
def inject_user():
    stmnt = db.select(User)
    user = db.session.execute(stmnt).scalars().first()
    movie_list = db.session.execute(db.select(Movie)).scalars().all()
    return dict(user=user, movies=movie_list)
    

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

# To insert a list of dictionaries like so into a table:
# movies_table = db.Table(
#     'my_favorite_movies',  # Name of the table in the database
#     db.metadata,  # SQLAlchemy metadata
#     autoload_with=db.engine  # Automatically load the table's schema
# )
# db.session.execute(movies_table.insert(), movies_data)
# db.session.commit()


with app.app_context():
    class GameDetails(db.Model):
        __table__ = db.Table('game_details', db.metadata, autoload_with=db.engine)

    class GamesPlatforms(db.Model):
        __table__ = db.Table("games_platforms", db.metadata, autoload_with=db.engine)

if __name__ == '__main__':
    app.run(debug=True)

