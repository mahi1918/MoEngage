from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    brewery_id = db.Column(db.Integer, db.ForeignKey('brewery.id'), nullable=False)
    
    def __repr__(self):
        return f'<Review {self.id}>'



class Brewery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    website_url = db.Column(db.String(255))
    current_rating = db.Column(db.Float)
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))


    reviews = db.relationship('Review', backref='brewery', lazy=True)

    def __repr__(self):
        return f'<Brewery {self.name}>'
