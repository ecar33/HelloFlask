from flask import Flask, render_template, request, redirect, flash, url_for, Blueprint
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import PasswordField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import os
import click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'games.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

db: SQLAlchemy = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalars().first()
    return user

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

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SettingsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField('Update Name')


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login')
def admin(username, password):
    db.create_all()

    user = db.session.execute(db.select(User)).scalars().first()

    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    
    db.session.commit()
    click.echo('Done.')

@app.cli.command()
@click.option('--username', prompt="Enter the username: ", help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login')
def check_password(username, password):    
    while True:
        user: User = db.session.execute(db.select(User).where(User.username == username)).scalars().first()

        if user is not None:
            break
        else:
            click.echo('User does not exist!')
            username = click.prompt('Enter the username: ')

    while True:
        if user.validate_password(password):
            print("Password is correct.")
            break
        else:
            print("Password is incorrect")

        password = click.prompt('Enter the correct password: ', hide_input=True, confirmation_prompt=True)

    click.echo("Done.")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        user: User = db.session.execute(db.select(User).where(User.username == username)).scalars().first()

        if user.username == username and user.validate_password(password):
            login_user(user)
            flash(f'{user.name} sucessfully logged in.')
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
        return redirect(url_for("login"))
        
    return render_template('login.html', form=form)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye')
    return redirect(url_for('login'))

@app.route('/user/<name>')
@login_required
def user_page(name):
    return f'User page for: {escape(name)}'

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Must be signed in to change name.')
            return redirect(url_for('index'))
        
        new_name = form.name.data
        current_user.name = new_name
        db.session.commit()

    return render_template('settings.html', form=form)


@movies_bp.route('/', methods=['GET', 'POST'])
def movies():
    add_movie_form = AddMovieForm()
    delete_movie_form = DeleteMovieForm()

    return render_template('movies.html', add_movie_form=add_movie_form, delete_movie_form=delete_movie_form)

@movies_bp.route('/delete', methods=['POST'])
@login_required
def delete_movie():
    delete_movie_form = DeleteMovieForm()

    if delete_movie_form.validate_on_submit():
        movie_id = delete_movie_form.movie_id.data
        movie = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalars().first()

        if not movie:
            flash('Movie not found.')
            return redirect(url_for('movies.movies'))

        db.session.delete(movie)
        db.session.commit()
        flash('Item deleted')
        return redirect(url_for('movies.movies'))
    
@movies_bp.route('/add', methods=['POST'])
@login_required
def add_movie():
    add_movie_form = AddMovieForm()

    if add_movie_form.validate_on_submit():
        movie = Movie()
        movie.title = add_movie_form.title.data
        movie.year = add_movie_form.year.data
        db.session.add(movie)
        db.session.commit()
        flash('Item added')
        return redirect(url_for('movies.movies'))

@movies_bp.route('/edit/<int:movie_id>', methods=["GET", "POST"])
def edit(movie_id):
    movie = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalars().first()

    if request.method == "POST":
        if not current_user.is_authenticated:
            flash('Sign in to edit movies.')
            return redirect(url_for('movies.movies'))
        
        title = request.form.get('title')
        year = request.form.get('year')

        if not title or not year.isdigit() or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
    
        movie.title = title
        movie.year = year
        db.session.commit()

        link = url_for("movies.movies")
        flash(f'Successfully updated! Click <a href={link}>here</a> to return to the movies list.')
        return redirect(url_for('edit', movie_id=movie_id))
    
    return render_template('edit.html', movie=movie)


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
    
# Set up movies blueprint
app.register_blueprint(movies_bp)

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

