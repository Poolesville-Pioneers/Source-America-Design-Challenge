from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(100))
    method = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    
class Shift(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    job = db.Column(db.Integer())
    start = db.Column(db.DateTime(timezone=True))
    end = db.Column(db.DateTime(timezone=True))
    employee = db.Column(db.Integer())
    
class Job(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    wage = db.Column(db.Integer()) #store in cents/hour
    
    
