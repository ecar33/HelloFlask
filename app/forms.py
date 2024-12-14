from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField


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