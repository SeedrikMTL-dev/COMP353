# Code inspired from https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog/08-Posts/flaskblog

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from MainProject import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    userType = db.Column(db.String(60), nullable=False)
    monthlyChargesEmployer = db.Column(db.String(60), nullable=False, default='Prime - 50$/month')
    monthlyChargesEmployee = db.Column(db.String(60), nullable=False, default='Basic - No Charge')
    posts = db.relationship('Post', backref='author', lazy=True)
    condition = db.Column(db.String(10), nullable=False, default='Active')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(10), nullable=False, default="IT")
    status = db.Column(db.String, nullable=False, default="Open")

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')

    def __repr__(self):
        return f"Application('{self.user_id}', '{self.post_id}')"

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
