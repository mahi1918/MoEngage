from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import requests 
from forms import AddReviewForm
from models import db, Review, Brewery 
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)

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

class Review(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   brewery_id = db.Column(db.Integer, db.ForeignKey('brewery.id'), nullable=False)
   review_text = db.Column(db.Text)
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

   def __repr__(self):
       return f'<Review {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def login_signup():
    return render_template('login_signup.html')


@app.route('/login', methods=['POST'])
def login():
    try:
        if current_user.is_authenticated:
            logout_user()

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        print(username,password)


        if user and user.password == password:
            login_user(user)
            flash('Login successful', 'success')
            print("success")
            return redirect(url_for('search'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
            print("fail")
            return redirect(url_for('login_signup'))
    except Exception as e:
        print(str(e))
        flash('An error occurred during login.', 'danger')
        return redirect(url_for('login_signup'))


@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('login_signup'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Signup successful', 'success')
        return redirect(url_for('search'))
    except Exception as e:
        print(str(e))
        flash('An error occurred during signup.', 'danger')
        return redirect(url_for('login_signup'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form.get('query')

        api_url = f'https://api.openbrewerydb.org/breweries/search?query={query}'
        response = requests.get(api_url)

        if response.status_code == 200:
            breweries_data = response.json()
            return render_template('breweries.html', user=current_user, breweries_data=breweries_data)
        else:
            flash('Failed to retrieve brewery data from the API.', 'danger')
            return redirect(url_for('search'))

    return render_template('search.html', user=current_user)

@app.route('/add_review', methods=['GET', 'POST'])
@login_required
def add_review():
    form = AddReviewForm()

    if request.method == 'POST' and form.validate_on_submit():
        brewery_name = form.brewery_name.data
        review_text = form.review_text.data
        
        print(f"Brewery Name: {brewery_name}")
        print(f"Review Text: {review_text}")

        brewery = Brewery.query.filter_by(name=brewery_name).first()

        if brewery:
            new_review = Review(review_text=review_text, user=current_user, brewery=brewery)
            db.session.add(new_review)
            db.session.commit()

            flash('Review added successfully!', 'success')

            breweries_data = get_breweries_with_reviews()
            return render_template('breweries.html', user=current_user, breweries_data=breweries_data)

        flash('Brewery not found. Please enter a valid brewery name.', 'danger')

    return render_template('add_review.html', user=current_user, form=form)


@app.route('/brewery/<brewery_name>', methods=['GET', 'POST'])
@login_required
def brewery_page(brewery_name):
    brewery = Brewery.query.filter_by(name=brewery_name).first()

    if not brewery:
        flash('Brewery not found.', 'danger')
        return redirect(url_for('search'))

    if request.method == 'POST':
        rating = int(request.form['rating'])
        description = request.form['description']

        new_review = Review(rating=rating, description=description, user=current_user, brewery=brewery)
        db.session.add(new_review)
        db.session.commit()

        flash('Review added successfully', 'success')

    reviews = Review.query.filter_by(brewery=brewery).all()
    print("Brewery Name:", brewery.name)
    print("Reviews:", reviews)
    breweries_data = get_breweries_with_reviews()
    print(f"Breweries Data in brewery_page: {breweries_data}")

    return render_template('brewery.html', brewery=brewery, reviews=reviews)

def get_breweries_with_reviews():
    breweries = Brewery.query.all()
    breweries_data = []

    for brewery in breweries:
        reviews = Review.query.filter_by(brewery_id=brewery.id).all()
        print(f"Brewery: {brewery.name}, Reviews: {reviews}")
        breweries_data.append({'brewery': brewery, 'reviews': reviews})

    print(f"Breweries Data: {breweries_data}")
    return breweries_data

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login_signup'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

