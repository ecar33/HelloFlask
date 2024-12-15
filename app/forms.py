from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField


class AddMovieForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(1, max=50)])
    year = StringField('Year', validators=[
        DataRequired(),
        Length(4,4)])
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

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(5,20, message="Username must be between 3 and 20 characters")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long.")])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Password confirmation is required."), 
        EqualTo('password', message="Passwords must match."),])
