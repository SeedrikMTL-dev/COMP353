# Code inspired from https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog/08-Posts/flaskblog

import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from MainProject import app, db, bcrypt, mail
from MainProject.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                               PostForm, RequestResetForm, ResetPasswordForm)
from MainProject.models import User, Post, Application, History
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    appliedToPost = []
    if current_user.is_authenticated:
        for p in posts.items:
            q = Application.query.filter(Application.post_id == p.id).filter(Application.user_id == current_user.id)
            appliedToPost.append(db.session.query(q.exists()).scalar())
    return render_template('home.html', posts=posts, appliedToPost=appliedToPost)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, name=form.name.data, password=hashed_password, userType=form.userType.data)
        db.session.add(user)
        flash(user.userType, 'warning')
        flash('Your account has been created! You are now able to log in', 'success')
        historyContent = user.email + "'s account has been created!"
        history = History(content= historyContent)
        db.session.add(history)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.condition == 'Inactive':
            flash('Login Unsuccessful. Account currently deactivated.', 'danger')
            history = History(content="Unsuccessful login attempt by deactivated account.")
            db.session.add(history)
            db.session.commit()
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful!', 'success')
            historyContent = user.email + " has successfully logged in."
            history = History(content=historyContent)
            db.session.add(history)
            db.session.commit()
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            history = History(content="Unsuccessful login attempt.")
            db.session.add(history)
            db.session.commit()
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    historyContent=current_user.email + " User has logged out."
    history = History(content=historyContent)
    logout_user()
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.name = form.name.data
        if current_user.userType == 'Employer':
            current_user.monthlyChargesEmployer = form.monthlyChargesEmployer.data
        if current_user.userType == 'Employee':
            current_user.monthlyChargesEmployee = form.monthlyChargesEmployee.data
        flash('Your profile has been updated!', 'success')
        historyContent=current_user.email + " has updated their profile."
        history = History(content=historyContent)
        db.session.add(history)
        db.session.commit()
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.name.data = current_user.name
        if current_user.userType == 'Employer':
            form.monthlyChargesEmployer.data = current_user.monthlyChargesEmployer
        if current_user.userType == 'Employee':
            form.monthlyChargesEmployee.data = current_user.monthlyChargesEmployee
    return render_template('profile.html', title='Profile', form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    user = User.query.filter_by(name=current_user.name).first_or_404()
#    posts = Post.query.filter_by(author=user)
    postCount = Post.query.filter_by(author=user).count()
    if postCount < 5 or current_user.monthlyChargesEmployer == 'Gold - 100$/month':
        form = PostForm()
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, author=current_user, category=form.category.data,
                        status=form.status.data)
            db.session.add(post)
            flash('Your post has been created!', 'success')
            historyContent=current_user.email + " has created a post."
            history = History(content=historyContent)
            db.session.add(history)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('create_post.html', title='New Post',
                               form=form, legend='New Post')
    else:
        flash('Maximum 5 posts for Prime members. Consider upgrading for more!', 'info')
        historyContent=current_user.email + " attempted to make more than 5 posts as a Prime member."
        history = History(content=historyContent)
        db.session.add(history)
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    applicationStatus = 'Pending'
    applications = Application.query.filter_by(post_id=post.id).all()
    userApplicants = []
    for application in applications:
        userApplicants.append(User.query.filter_by(id=application.user_id).all())
    numOfApplications = Application.query.filter_by(post_id= post_id).count()
    appliedToPost = False
    if current_user.is_authenticated:
        q = db.session.query(Application.id).filter(Application.post_id == post_id).filter(Application.user_id
                                                                                            == current_user.id)
        appliedToPost = db.session.query(q.exists()).scalar()
        application = Application.query.filter_by(user_id=current_user.id).first()
        if (application != None):
            applicationStatus = application.status
    return render_template('post.html', title=post.title, post=post, numOfApplications=numOfApplications,
                           appliedToPost=appliedToPost, userApplicants=userApplicants, applications=applications,
                           applicationStatus=applicationStatus)



@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.status = form.status.data
        flash('Your post has been updated!', 'success')
        historyContent=current_user.email + " updated a post."
        history = History(content=historyContent)
        db.session.add(history)
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
        form.status.data = post.status
    return render_template('update_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    flash('Your post has been deleted!', 'success')
    historyContent=current_user.email + " deleted a post."
    history = History(content=historyContent)
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/profile/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        abort(403)
    for post in user.posts:
        db.session.delete(post)
    db.session.delete(user)
    flash('Your account has been deleted!', 'success')
    historyContent=current_user.email + " deleted their profile."
    history = History(content=historyContent)
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/user/<string:name>")  # route to show all posts of that email
def user_posts(name):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(name=name).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    appliedToPost = []
    if current_user.is_authenticated:
        for p in Post.query.all():
            q = db.session.query(Application.id).filter(Application.post_id == p.id).filter(Application.user_id
                                                                                            == current_user.id)
            appliedToPost.append(db.session.query(q.exists()).scalar())
    return render_template('user_post.html', posts=posts, user=user, appliedToPost=appliedToPost)

@app.route("/category/<string:category>")  # route to show all posts of that email
def category_posts(category):
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category=category).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    appliedToPost = []
    if current_user.is_authenticated:
        for p in Post.query.all():
            q = db.session.query(Application.id).filter(Application.post_id == p.id).filter(Application.user_id
                                                                                            == current_user.id)
            appliedToPost.append(db.session.query(q.exists()).scalar())
    return render_template('category_post.html', posts=posts, category=category, appliedToPost=appliedToPost)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        historyContent=user.email + " has requested a password reset."
        history = History(content=historyContent)
        db.session.add(history)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/post/<int:post_id>/apply", methods=['GET', 'POST'])
@login_required
def apply_post(post_id):
    post = Post.query.get_or_404(post_id)
    applicationCount = Application.query.filter_by(user_id=current_user.id).count()
    if applicationCount < 5 or current_user.monthlyChargesEmployee == 'Gold - 20$/month':
        application = Application(user_id=current_user.id, post_id=post.id)
        db.session.add(application)
        flash('Application Submitted', 'success')
        historyContent=current_user.email + " submitted an application."
        history = History(content=historyContent)
        db.session.add(history)
    else:
        flash('Maximum 5 applications for Prime members. Consider upgrading for more!', 'info')
        historyContent=current_user.email + " attempted to submit more than 5 applications as a Prime member."
        history = History(content=historyContent)
        db.session.add(history)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/withdraw", methods=['GET', 'POST'])
@login_required
def withdraw_post(post_id):
    db.session.query(Application.id).filter(Application.post_id == post_id).filter(Application.user_id
                                                                                == current_user.id).delete()
    db.session.commit()
    flash('Application Withdrawn', 'success')
    historyContent=current_user.email + " withdrew an application."
    history = History(content=historyContent)
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/post/<int:application_id>/accept", methods=['GET', 'POST'])
@login_required
def accept_application(application_id):
    application = Application.query.filter_by(id=application_id).first()
    postID = application.post_id
    application.status = 'Accepted'
    flash('Application Accepted', 'success')
    historyContent=current_user.email + " accepted an application."
    history = History(content=historyContent)
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('post',post_id=postID))

@app.route("/post/<int:application_id>/reject", methods=['GET', 'POST'])
@login_required
def reject_application(application_id):
    application = Application.query.filter_by(id=application_id).first()
    postID = application.post_id
    application.status = 'Rejected'
    flash('Application Rejected', 'success')
    historyContent=current_user.email + " rejected an application."
    history = History(content=historyContent)
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('post',post_id=postID))

@app.route("/history", methods=['GET','POST'])
@login_required
def history():
    history = History.query.order_by(History.date_posted.desc())
    return render_template('system_activity.html', title='History', history=history)

@app.route("/activate", methods=['GET', 'POST'])
@login_required
def activate():
    users = User.query.order_by(User.email)
    return render_template('activate.html', title='List of Users', users=users)

@app.route("/activate/<int:user_id>/activate", methods=['GET', 'POST'])
@login_required
def activate_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.condition = 'Active'
    historyContent = current_user.email + " has been activated."
    history = History(content=historyContent)
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('activate'))

@app.route("/activate/<int:user_id>/deactive", methods=['GET', 'POST'])
@login_required
def deactivate_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.condition = 'Inactive'
    historyContent = current_user.email + " has been deactivated."
    history = History(content=historyContent)
    db.session.add(history)
    db.session.commit()
    return redirect(url_for('activate'))