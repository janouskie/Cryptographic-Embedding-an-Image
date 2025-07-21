from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from mat2.mat2 import clean_meta
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        errors = []

        # Username validation
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        elif not re.match(r'^\w+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        elif User.query.filter_by(username=username).first():
            errors.append('Username already exists.')

        # Email validation
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not email:
            errors.append('Email is required.')
        elif not re.match(email_regex, email):
            errors.append('Enter a valid email address.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        # Password validation
        if not password:
            errors.append('Password is required.')
        else:
            if len(password) < 6:
                errors.append('Password must be at least 6 characters.')
            if not re.search(r'[A-Z]', password):
                errors.append('Password must contain at least one uppercase letter.')
            if not re.search(r'[a-z]', password):
                errors.append('Password must contain at least one lowercase letter.')
            if not re.search(r'[0-9]', password):
                errors.append('Password must contain at least one digit.')
            if not re.search(r'[\W_]', password):
                errors.append('Password must contain at least one special character.')

        # Show all errors
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['user_role'] = new_user.role
            session['username'] = new_user.username
            return redirect(url_for('home.home'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['username'] = user.username
            if user.role == 'Admin':
                return redirect(url_for('admin.admin_page'))
            else:
                file_location = "/Users/Administrator2/Downloads/Cryptographic-Embedding-an-Image-main 2/second_photos/p2.jpg"
                clean_meta(file_location)
                flash('Metadata removed from your image!', 'success')
                return redirect(url_for('home.home'))
        else:
            flash('Invalid credentials.', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        session.pop('user_role', None)
        session.pop('username', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Add logic to handle password reset (send email, etc.)
        flash('If this email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')
