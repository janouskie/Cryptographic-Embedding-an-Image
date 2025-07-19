from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        session['user_role'] = new_user.role
        session['username'] = new_user.username  # <-- Add this line
        return redirect(url_for('home.home'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['username'] = user.username  # <-- Add this line
            if user.role == 'Admin':
                return redirect(url_for('admin.admin_page'))
            else:
                return redirect(url_for('home.home'))
        else:
            flash('Invalid credentials.')
            return redirect(url_for('auth.login'))
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        session.pop('user_id', None)
        session.pop('user_role', None)
        session.pop('username', None)  # <-- Also clear username on logout
    return redirect(url_for('auth.login'))
