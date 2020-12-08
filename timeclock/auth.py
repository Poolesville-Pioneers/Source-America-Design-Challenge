from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return 'Login'

@auth.route('/logout')
def logout():
    return 'Logout'
    
@auth.route('/admin')
def admin():
    return 'Admin'

@auth.route('/setup', methods=['GET','POST'])
def setup():
    if request.method=='GET':
        return 'Setup'
    else:
        user = request.form.get('user')
        password = request.form.get('password')
        
        if User.query.filter_by(user=user).first():
            flash("User already exists.")
            return redirect(url_for('auth.setup'))

