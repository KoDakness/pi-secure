from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a long, random secret key!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Ensure encryption key exists or generate a new one
if not os.path.exists('encryption.key'):
    key = Fernet.generate_key()
    with open('encryption.key', 'wb') as key_file:
        key_file.write(key)

# Load encryption key
with open('encryption.key', 'rb') as key_file:
    cipher = Fernet(key_file.read())


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Password Model
class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    website = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.Text, nullable=False)

# Initialize database
with app.app_context():
    db.create_all()


# Home Route
@app.route('/')
def home():
    return redirect(url_for('login'))


# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Try a different one."

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Add user to the database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))

        return "Invalid credentials. Try again."

    return render_template('login.html')


# Dashboard (View & Add Passwords)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        website = request.form['website']
        username = request.form['username']
        plaintext_password = request.form['password']

        # Encrypt the password
        encrypted_password = cipher.encrypt(plaintext_password.encode())

        # Save to database
        new_password = Password(user_id=session['user_id'], website=website, username=username, password=encrypted_password)
        db.session.add(new_password)
        db.session.commit()

    # Retrieve and decrypt user's passwords
    passwords = Password.query.filter_by(user_id=session['user_id']).all()
    decrypted_passwords = [
        {
            'id': p.id,
            'website': p.website,
            'username': p.username,
            'password': cipher.decrypt(p.password).decode()
        }
        for p in passwords
    ]

    return render_template('dashboard.html', passwords=decrypted_passwords)


# Delete a Password
@app.route('/delete/<int:password_id>', methods=['POST'])
def delete_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    password = Password.query.get(password_id)
    if password and password.user_id == session['user_id']:
        db.session.delete(password)
        db.session.commit()

    return redirect(url_for('dashboard'))


# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

