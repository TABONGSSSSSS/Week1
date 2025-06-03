from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    birthday = db.Column(db.String(20), nullable=False)  # Store as string for simplicity
    address = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(200), nullable=True)

def calculate_age(birthday_str):
    try:
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
    except ValueError:
        try:
            birthday = datetime.strptime(birthday_str, '%m/%d/%Y')
        except ValueError:
            return "Unknown"
    today = datetime.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    return age

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    address = request.form['address']

    # Get the birthdate parts
    birth_month = request.form['birth_month']
    birth_day = request.form['birth_day']
    birth_year = request.form['birth_year']

    birthday = f"{birth_year}-{birth_month.zfill(2)}-{birth_day.zfill(2)}"

    image = request.files['image']
    image_filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    image.save(image_path)

    # Check if username exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return "Username already exists", 400

    new_user = User(
        username=username,
        password=password,
        name=name,
        birthday=birthday,
        address=address,
        image=image_filename
    )
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        return redirect(url_for('profile', username=username))
    return "Invalid credentials", 401

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        age = calculate_age(user.birthday)
        return render_template('profile.html', user=user, username=username, age=age)
    return "User not found", 404

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')

    # Create the SQLite DB tables if they don't exist
    with app.app_context():
        db.create_all()

    app.run(debug=True)
