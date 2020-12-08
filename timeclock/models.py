from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    user = db.Column(db.String(1000))
