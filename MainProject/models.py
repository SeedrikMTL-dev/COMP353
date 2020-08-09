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
    email = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    userType = db.Column(db.String(60), nullable=False)
    employerMembership = db.Column(db.String(60), nullable=False, default='Prime - 50$/month')
    employeeMembership = db.Column(db.String(60), nullable=False, default='Basic - No Charge')
    posts = db.relationship('Post', backref='author', lazy=True)
    condition = db.Column(db.String(10), nullable=False, default='Active')
    cardNum = db.Column(db.String(10), nullable=False, default='')
    cvc = db.Column(db.String(10), nullable=False, default='')
    expireDate = db.Column(db.String(10), nullable=False, default='')
    withdrawType = db.Column(db.String(60), nullable=False, default='Automatic')
    frozen = db.Column(db.Boolean, nullable=False, default=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)

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


class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('user.email'), unique=True, nullable=False)
    name = db.Column(db.String(50), db.ForeignKey('user.name'), nullable=False)
    password = db.Column(db.String(50), db.ForeignKey('user.password'), nullable=False)
    userType = db.Column(db.String(60), db.ForeignKey('user.userType'), nullable=False)
    employerMembership = db.Column(db.String(60), nullable=False, default='Basic - Free')
    condition = db.Column(db.String(10), db.ForeignKey('user.condition'), nullable=False, default='Active')
    cardNum = db.Column(db.String(10), db.ForeignKey('user.cardNum'), nullable=False, default='')
    cvc = db.Column(db.String(10), db.ForeignKey('user.cvc'), nullable=False, default='')
    expireDate = db.Column(db.String(10), db.ForeignKey('user.expireDate'), nullable=False, default='')
    frozen = db.Column(db.Boolean, db.ForeignKey('user.frozen'), nullable=False, default=True)
    balance = db.Column(db.Float, db.ForeignKey('user.balance'), nullable=False, default=0.0)

    def __repr__(self):
        return f"Employer('{self.email}', '{self.employerMembership}')"


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('user.email'), unique=True, nullable=False)
    name = db.Column(db.String(50), db.ForeignKey('user.name'), nullable=False)
    password = db.Column(db.String(50), db.ForeignKey('user.password'), nullable=False)
    userType = db.Column(db.String(60), db.ForeignKey('user.userType'), nullable=False)
    employeeMembership = db.Column(db.String(60), nullable=False, default='Basic - No Charge')
    condition = db.Column(db.String(10), db.ForeignKey('user.condition'), nullable=False, default='Active')
    cardNum = db.Column(db.String(10), db.ForeignKey('user.cardNum'), nullable=False, default='')
    cvc = db.Column(db.String(10), db.ForeignKey('user.cvc'), nullable=False, default='')
    expireDate = db.Column(db.String(10), db.ForeignKey('user.expireDate'), nullable=False, default='')
    frozen = db.Column(db.Boolean, db.ForeignKey('user.frozen'), nullable=False, default=True)
    balance = db.Column(db.Float, db.ForeignKey('user.balance'), nullable=False, default=0.0)

    def __repr__(self):
        return f"Employee('{self.email}', '{self.employeeMembership}')"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('user.email'), unique=True, nullable=False)
    name = db.Column(db.String(50), db.ForeignKey('user.name'), nullable=False)
    password = db.Column(db.String(50), db.ForeignKey('user.password'), nullable=False)
    userType = db.Column(db.String(60), db.ForeignKey('user.userType'), nullable=False)

    def __repr__(self):
        return f"User('{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(10), nullable=False, default="IT")
    status = db.Column(db.String, nullable=False, default="Open")
    numOfNeededEmployees = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cardNum = db.Column(db.String(10), db.ForeignKey('user.cardNum'), nullable=False, default='')
    cvc = db.Column(db.String(10), db.ForeignKey('user.cvc'), nullable=False, default='')
    expireDate = db.Column(db.String(10), db.ForeignKey('user.expireDate'), nullable=False, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    withdrawType = db.Column(db.String(60), nullable=False, default='Automatic')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')
    dateOfApplication = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Application('{self.user_id}', '{self.post_id}')"


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
