import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import sqlite3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import requests
from scapy.all import ARP, Ether, srp
from models import init_db
from routes.auth_routes import auth_bp
#from routes.admin_routes import admin_bp
from routes.home_routes import home_bp
from routes.profile_routes import prof_bp  
from PIL import Image
from PIL.ExifTags import TAGS



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
    from datetime import datetime
    return dict(session=session, current_year=datetime.now().year)

if __name__ == '__main__':
    app.run(debug=True, port=8080)



UPLOAD_FOLDER = '/photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/image-meta', methods=['GET', 'POST'])
def image_meta():
    result = ""
    download_link = None
    if request.method == 'POST':
        file = request.files['file']
        action = int(request.form['action'])
        if file:
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, file.filename)
            file.save(filepath)
            img = Image.open(filepath)
            if action in [1, 2]:
                result = show_meta(img, action)
            elif action == 3:
                output_file = clean_meta(img, filepath)
                download_link = url_for('download_file', filename=os.path.basename(output_file))
                result = f"Metadata removed. <a href='{download_link}'>Download cleaned image</a>"
    return render_template('image_meta.html', result=result, download_link=download_link)

def show_meta(img, mode):
    exif_data = img._getexif()
    if not exif_data:
        return "No EXIF metadata found."
    output = []
    if mode == 1:
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            output.append(f"{tag:25}: {value}")
    elif mode == 2:
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if "Date" in str(tag) or "Time" in str(tag):
                output.append(f"{tag:25}: {value}")
    return "<br>".join(output)

def clean_meta(img, filename):
    data = list(img.getdata())
    img_no_exif = Image.new(img.mode, img.size)
    img_no_exif.putdata(data)
    output_file = filename.replace(".jpg", "_cleaned.jpg")
    img_no_exif.save(output_file)
    return output_file

@app.route('/uploads/<filename>')
def download_file(filename):
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(upload_dir, filename, as_attachment=True)

from flask import session, redirect, url_for

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('home.html')
