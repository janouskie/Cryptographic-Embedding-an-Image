from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import User

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('index.html')  


@home_bp.route('/home')
def home():
     return render_template('home.html')

@home_bp.route('/mdstrip')
def mdstrip():
    return render_template('mdstrip.html')

@home_bp.route('/hash')
def hash():
    return render_template('hash.html')
