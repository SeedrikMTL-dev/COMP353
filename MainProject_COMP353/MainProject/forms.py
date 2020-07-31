from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, EqualTo, Email, Length, Regexp, ValidationError, DataRequired
from MainProject.models import User


# taken from the notes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# taken from the notes, except added a variable for favourite character
# wanted to be an option for the user therefore needed to import SelectField
class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(),
                                       Length(4, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must start with a letter and must have only letters, '
                                              'numbers, dots or underscores')])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(8)])
    password2 = PasswordField('Repeat password',
                              validators=[InputRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')



class UpdateProfileForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(),
                                       Length(4, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must start with a letter and must have only letters, '
                                              'numbers, dots or underscores')])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


