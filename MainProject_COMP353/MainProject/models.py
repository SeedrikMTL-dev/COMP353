# Code inspired from https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog/08-Posts/flaskblog

from datetime import datetime
from MainProject import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    userType = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Employee(User):
    #def __init__(self, id, username, email, password, posts, userType):
    #    super().__init__(id, username, email, password, posts, userType)
    employeeCategory = db.Column(db.String(20), nullable=False, default='Basic - Free')
    employeeMonthlyCharges = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Employee('{self.username}', '{self.email}')"

class Employer(User):
    #def __init__(self, id, username, email, password, posts, userType):
    #    super().__init__(id, username, email, password, posts, userType)
    employerCategory = db.Column(db.String(20), nullable=False, default='Prime - 50$/month')
    employerMonthlyCharges = db.Column(db.Integer, nullable=False, default=50)

    def __repr__(self):
       return f"Employer('{self.username}', '{self.email}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
