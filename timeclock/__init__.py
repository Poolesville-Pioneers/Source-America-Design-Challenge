from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import urandom
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = urandom(32);
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User, Shift, Job

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    

    return app
