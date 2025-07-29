import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a database object
db = SQLAlchemy()

# This is our User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Every user has a unique ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username can't be empty or repeated
    email = db.Column(db.String(120), unique=True, nullable=False)    # Same thing for email
    password = db.Column(db.String(120), nullable=False)              # Password must be provided
    role = db.Column(db.String(80), nullable=False, default='User')   # Default role is just 'User'


# This function sets up the database
def init_db(app):
    # Figure out where to store the database file
    current_folder = os.path.dirname(__file__)
    db_file = os.path.join(current_folder, 'database.db')

    # Tell Flask where the database is and to not track every change
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Connect the app to the database
    db.init_app(app)

    # If the database file doesn't exist yet, let's create it
    if not os.path.exists(db_file):
        with app.app_context():  # this is needed to work with the database properly
            db.create_all()  # this makes all the tables from our models

            # See if there's a SQL script we can run
            sql_script_path = os.path.join(current_folder, 'database.sql')

            if os.path.exists(sql_script_path):
                with open(sql_script_path, 'r') as file:
                    script_contents = file.read()

                # Open a basic sqlite connection and run the script
                connection = sqlite3.connect(db_file)
                cursor = connection.cursor()
                cursor.executescript(script_contents)
                connection.commit()
                connection.close()
