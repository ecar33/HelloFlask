import os
import sys
import click
from flask import Config, Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from app.config import ProductionConfig, TestingConfig
from app.models import Movie, User
from app.extensions import db, login_manager


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else: 
    prefix = 'sqlite:////'

# Load environment variables
load_dotenv()

def create_app(config=ProductionConfig):

    # create and configure the app
    app = Flask(__name__)

    if config == None:
        config = TestingConfig
    
    app.config.from_object(config)

    if config == ProductionConfig:

        db_file_path = os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
        
        if WIN:
            db_file_path = db_file_path.replace(os.path.sep, '/')

        app.config['SQLALCHEMY_DATABASE_URI'] = prefix + db_file_path


    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from app.routes import movies_bp, games_bp, auth_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(movies_bp)

    with app.app_context():
        db.create_all()
    
    @app.context_processor
    def inject():
        name = "ecar33"
        movie_list = db.session.execute(db.select(Movie)).scalars().all()
        return dict(name=name, movies=movie_list)
    
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

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400
        
    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User 
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalars().first()
    return user


