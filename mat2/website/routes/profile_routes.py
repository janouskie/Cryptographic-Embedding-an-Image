from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash
from models import User, db
from sqlalchemy.sql import text  


prof_bp = Blueprint('profile', __name__)

@prof_bp.route('/profile') #profile pagge is loaded if users is logged in 
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
   
    else:
        return redirect(url_for('auth.login'))



@prof_bp.route('/profile/update_username', methods=['POST']) #update username
def update_username():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        new_username = request.form['username']
        if User.query.filter_by(username=new_username).first():
            flash('Username Taken.')
        else:
            user.username = new_username
            db.session.commit()
        return redirect(url_for('profile.profile'))
    else:
        return redirect(url_for('auth.login'))

@prof_bp.route('/profile/update_email', methods=['POST'])   #update email 
def update_email():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        new_email = request.form['email']
        if User.query.filter_by(email=new_email).first():
            flash('Email Taken')
        else:
            user.email = new_email
            db.session.commit()
            return redirect(url_for('profile.profile'))
    else:
        return redirect(url_for('auth.login'))

@prof_bp.route('/profile/reset_password', methods=['POST'])   #password resrt
def reset_password():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')  
        user.password = hashed_password
        db.session.commit()
        return redirect(url_for('profile.profile'))
    else:
        return redirect(url_for('auth.login'))