from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  # Updated import
from cryptography.fernet import Fernet
import os
from utils import generate_password

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a long, random secret key!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder for storing files
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}  # Allowed file types
db = SQLAlchemy(app)

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

# File Model (Updated to match the actual name)
class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# File Upload Route
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            # Securely save the file using a unique filename
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Save file info in the database
            new_file = UploadedFile(user_id=session['user_id'], filename=filename, filepath=filepath)
            db.session.add(new_file)
            db.session.commit()

            return redirect(url_for('dashboard'))

    return render_template('upload.html')

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

        # Hash the password using werkzeug.security
        hashed_password = generate_password_hash(password)

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
        if user and check_password_hash(user.password, password):  # Updated to use werkzeug
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

    # Retrieve uploaded files for the user
    files = UploadedFile.query.filter_by(user_id=session['user_id']).all()

    return render_template('dashboard.html', passwords=decrypted_passwords, files=files)

# Password Generation (API endpoint)
@app.route('/generate-password', methods=['GET'])
def generate():
    password_length = request.args.get("length", default=12, type=int)
    password = generate_password(password_length)
    return jsonify(password=password)

# Delete a Password
@app.route('/delete_password/<int:password_id>', methods=['POST'])
def delete_password(password_id):
    password = Password.query.get(password_id)
    if password:
        db.session.delete(password)
        db.session.commit()
    return redirect(url_for('dashboard'))

# Delete a File (Updated Route)
@app.route('/delete_file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    file = UploadedFile.query.get(file_id)  # Corrected reference to the model
    if file:
        db.session.delete(file)
        db.session.commit()
    return redirect(url_for('dashboard'))

# Download File
@app.route('/download/<int:file_id>')
def download_file(file_id):
    file = UploadedFile.query.get(file_id)
    if file and file.user_id == session['user_id']:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True)
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Make the app accessible on the local network (accessible via Wi-Fi)
    app.run(host='0.0.0.0', port=5000, debug=False)

