from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    registration = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {
            "registration": self.registration,
            "username": self.username,
            "email": self.email,
            "password": self.password
        }

@app.route('/')
def index():
    cafe = User.query.all()
    random_user = random.choice(cafe)
    return jsonify (cafe ={
        "registration": random_user.registration,
        "username": random_user.username,
        "email": random_user.email,
        "password": random_user.password

    })

@app.route('/all')
def all():
    cafe = User.query.all()
    random_user = random.choice(cafe)
    return jsonify (random_user.to_dict())

@app.route('/a')
def a():
    cafes = User.query.all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

if __name__ == '__main__':
    app.run(debug=True)
