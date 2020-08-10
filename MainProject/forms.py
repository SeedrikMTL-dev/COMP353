# Code inspired from https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog/08-Posts/flaskblog

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from MainProject.models import User


class RegistrationForm(FlaskForm):
    userType = SelectField('Type of User', choices=['Administrator', 'Employer', 'Employee'], default='Administrator')
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    cvc = StringField('CVC')
    cardNum = StringField('Card Number')
    expireDate = StringField('Expiration Date')
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('That email does not exist. Please choose a valid one.')


class UpdateAccountForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    employerMembership = SelectField('Plan', choices=['Prime - 50$/month', 'Gold - 100$/month'],
                                         default='Prime - 50$/month')
    employeeMembership = SelectField('Plan', choices=['Basic - No Charge', 'Prime - 10$/month', 'Gold - 20$/month'],
                                         default='Basic - No Charge')
    cvc = StringField('CVC')
    cardNum = StringField('Card Number')
    expireDate = StringField('Expiration Date')
    withdrawType = SelectField('Withdraw Type', choices=['Automatic', 'Manual'], default='Automatic')
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    category = SelectField('Job Category', choices=['IT', 'Video Games', 'Web Design'], default='Category 1')
    status = SelectField('Status', choices=['Open', 'Closed'], default='Open')
    submit = SubmitField('Post')
    apply = SubmitField('Apply')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class PaymentMethodForm(FlaskForm):
    withdrawType = SelectField('Withdraw Type', choices=['Automatic', 'Manual'], default='Automatic')
    cvc = StringField('CVC', validators=[DataRequired()])
    cardNum = StringField('Card Number', validators=[DataRequired()])
    expireDate = StringField('Expiration Date', validators=[DataRequired()])
    submit = SubmitField('Post')
