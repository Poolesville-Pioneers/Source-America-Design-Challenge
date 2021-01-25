from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user, login_user, logout_user
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from .hash import hashImage

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        user = request.form.get('user')
        password = request.form.get('password')
        method = request.form.get('method')
        
        user = User.query.filter_by(user=user).first()
        
        if method == 'image':
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
            # if user does not select file, browser also
            # submit an empty part without filename
            if password.filename == '':
                flash('No selected file')
                return redirect(url_for('auth.login'))
            if password and password.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                if not user or not check_image_hash(user.password, password):
                    flash('Please check your login details and try again.') #To do: add visuals to error messages
                    return redirect(url_for('auth.login'))
            else:
                flash('Bad file type')
                return redirect(url_for('auth.login'))
            
        elif method == "text":
            if not user or not check_password_hash(user.password, password) or not user.method == method:
                flash('Please check your login details and try again.') #To do: add visuals to error messages
                return redirect(url_for('auth.login'))
        
        
            
        login_user(user)
        return redirect(url_for('main.dashboard'))
    
    

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
    
@auth.route('/admin-login', methods = ['GET','POST'])
def admin_login():
    if request.method=='GET':
        return render_template('admin-login.html')
        
    if request.method=='POST':
        user = request.form.get('user')
        password = request.form.get('password')
        
        user = User.query.filter_by(user=user).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.') #To do: add visuals to error messages
            return redirect(url_for('auth.login'))
            
        login_user(user)
        return redirect(url_for('main.admin_dashboard'))
        
@auth.route('/admin-signup', methods = ['GET','POST'])
def admin_signup():
    if request.method=='GET':
        return render_template("admin-signup.html")
        
    if request.method=='POST':
        user = request.form.get('user')
        password = request.form.get('password')
        
        if User.query.filter_by(user=user).first():
            flash("User already exists.")
            return redirect(url_for('auth.admin_signup'))
            
        new_user = User(user=user, password=generate_password_hash(password), method="text", admin=True)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('auth.admin_login'))
        
        

@auth.route('/setup', methods=['GET','POST'])
def setup():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))
        
    if request.method=='GET':
        return render_template('setup.html')
    else:
        user = request.form.get('user')
        password = request.form.get('password')
        method = request.form.get('method')
        
        if User.query.filter_by(user=user).first():
            flash("User already exists.")
            return redirect(url_for('auth.setup'))
        
        if method == 'image':
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
            # if user does not select file, browser also
            # submit an empty part without filename
            if password.filename == '':
                flash('No selected file')
                return redirect(url_for('auth.setup'))
            if password and password.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                new_user = User(user=user, password=hashImage(password), method=method)
            else:
                flash('Bad file type')
                return redirect(url_for('auth.setup'))
            
        elif method == "text":
            new_user = User(user=user, password=generate_password_hash(password), method=method)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('main.admin_dashboard'))
