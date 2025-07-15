import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from scapy.all import ARP, Ether, srp
import pywifi
from pywifi import const
from models import init_db
from routes.auth_routes import auth_bp
#from routes.admin_routes import admin_bp
from routes.home_routes import home_bp
from routes.profile_routes import prof_bp  



app = Flask(__name__)

# Initialize the database
init_db(app)
app.secret_key = '123'


# Register blueprints
app.register_blueprint(prof_bp, url_prefix='/profile')  
app.register_blueprint(auth_bp, url_prefix='/auth')
#app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(home_bp)

# Make session available in templates
@app.context_processor
def inject_user():
    from flask import session
    return dict(session=session)

if __name__ == '__main__':
    app.run(debug=True, port=80)



UPLOAD_FOLDER = '/photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



