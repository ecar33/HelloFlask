from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from markupsafe import escape
from app.forms import AddMovieForm, DeleteMovieForm, LoginForm, SettingsForm, SignupForm
from app.models import GameDetails, Movie, User
from app.extensions import db

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
movies_bp = Blueprint('movies', __name__, url_prefix='/movies')
games_bp = Blueprint('games', __name__, url_prefix='/games')

@main_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        user: User = db.session.execute(db.select(User).where(User.username == username)).scalars().first()

        if user.username == username and user.validate_password(password):
            login_user(user)
            flash(f'{user.name} sucessfully logged in.')
            return redirect(url_for('main.index'))
        
        flash('Invalid username or password')
        return redirect(url_for("auth.login"))
        
    return render_template('login.html', form=form)

@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()
        user: User = db.session.execute(db.select(User).where(User.username == username)).scalars().first()

        if user:
            flash(f'Username already exists, use a different one', 'error')
            return redirect(url_for("auth.signup"))
        else:
            new_user = User(name=username, username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User succesfully created! Please sign in.', 'success')
            return redirect(url_for("auth.login"))
    return render_template('sign_up.html', form=form)
    
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye')
    return redirect(url_for('auth.login'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        new_name = form.name.data
        current_user.name = new_name
        db.session.commit()
        flash('Name change successful.')
        return redirect(url_for('main.settings'))
    
    return render_template('settings.html', form=form)


@movies_bp.route('/', methods=['GET', 'POST'])
def movies():
    add_movie_form = AddMovieForm()
    delete_movie_form = DeleteMovieForm()

    return render_template('movies.html', add_movie_form=add_movie_form, delete_movie_form=delete_movie_form)

@movies_bp.route('/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    delete_movie_form = DeleteMovieForm()

    if delete_movie_form.validate_on_submit():
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
            return redirect(url_for('movies.edit', movie_id=movie_id))
    
        movie.title = title
        movie.year = year
        db.session.commit()

        link = url_for("movies.movies")
        flash(f'Successfully updated! Click <a href={link}>here</a> to return to the movies list.')
        return redirect(url_for('movies.edit', movie_id=movie_id))
    
    return render_template('edit.html', movie=movie)

@games_bp.route('/')
def games():
    games = db.session.execute(db.select(GameDetails)).scalars().fetchmany(10)
    print(games)
    return render_template('games.html', game_details=games)