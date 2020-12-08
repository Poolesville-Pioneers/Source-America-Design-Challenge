import functools
from flask import Flask, redirect, url_for, render_template, request, session, flash
from collections import namedtuple
from datetime import datetime, date, time, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import or_


app = Flask(__name__)
app.secret_key = "themitochondriaisthepowerhouseofthecell"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farmers.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(hours=2)
db = SQLAlchemy(app)



@app.route("/")
def home():
    return render_template("home.html")


'''
def ensure_logged_in(func):
    @functools.wraps(func)
    def wrapper_ensure_logged_in(*args, **kwargs):
        if not is_user_valid():
            return render_template("message.html", message=f"You must be logged in the access this page", nextlink=url_for("login"))
        return func(*args, **kwargs)
    return wrapper_ensure_logged_in
'''


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True) # Should be turned off in production #