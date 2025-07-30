from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from mat2 import *
import re

auth_bp = Blueprint('auth', __name__)

# REG - does sign up stuff
@auth_bp.route('/register', methods=['GET','POST'])
def reg():
 if request.method == 'POST':
  u = request.form['username'].strip()
  e = request.form['email'].strip()
  p = request.form['password']
  oops = []

  # validation checks
  if not u: oops.append("Enter username")
  elif len(u)<3: oops.append("username too shorrt")
  elif not re.match(r'^\w+$',u): oops.append("Letters & Numbers only")
  elif User.query.filter_by(username=u).first(): oops.append("Username tajen")

  if not e:
   oops.append("No email")
  elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$',e):
   oops.append("email format is incorrect")
  elif User.query.filter_by(email=e).first():
   oops.append("email already exists")

  # pass rules (bare min)
  if not p: oops.append("insert a password")
  else:
   if len(p)<6: oops.append("too weak")
   if not re.search(r'[A-Z]',p): oops.append("Full caps required")
   if not re.search(r'[a-z]',p): oops.append("Lowercase required")
   if not re.search(r'[0-9]',p): oops.append("insert a number")
   if not re.search(r'[\W_]',p): oops.append("insert a special character")

  if oops:
   for msg in oops: flash(msg,'error')
  else:
   guy = User(username=u, email=e, password=p)
   db.session.add(guy)
   db.session.commit()
   session['user_id']=guy.id
   session['user_role']=guy.role
   session['username']=guy.username
   session.pop('_flashes',None)
   return redirect(url_for('home.home'))

 return render_template('register.html')


# This section is where user logins to their profile account
@auth_bp.route('/login', methods=['GET','POST'])
def login():
 if request.method=='POST':
  u = request.form['username'].strip()
  p = request.form['password']
  dude = User.query.filter_by(username=u,password=p).first()  

  if dude:
   session['user_id']=dude.id
   session['user_role']=dude.role
   session['username']=dude.username
   session.pop('_flashes',None)
   if dude.role == 'Admin':
    return redirect(url_for('admin.admin_page'))
   else:
    pic = "/Users/Administrator2/Downloads/Cryptographic-Embedding-an-Image-main 2/second_photos/p2.jpg"
    clean_meta(pic)
    flash("✨ metadata been wiped", "metadata")
    return redirect(url_for('home.home'))
  else:
   flash("try again", 'error')
   return redirect(url_for('auth.login'))

 return render_template('login.html')


# This where the user logs out from their profile
@auth_bp.route('/logout')
def logout():
 if 'user_id' in session:
  session.pop('user_id')
  session.pop('user_role')
  session.pop('username')
 return redirect(url_for('auth.login'))


# This where user can reset their password but incomplete 
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
 if request.method=='POST':
  e = request.form.get('email')
  flash("Link been sent to your email address", 'info')
  return redirect(url_for('auth.login'))
 return render_template('forgot_password.html')
