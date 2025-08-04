import os
import sys

# add root folder to sys path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import init_db

# Blueprints
from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.profile_routes import prof_bp
# from routes.admin_routes import admin_bp
from routes.exif_routes import exiftool
from routes.stego_routes import stego_bp

# Image  metadata stuff
from PIL import Image
from PIL.ExifTags import TAGS
import subprocess

# other stuff 
from scapy.all import ARP, Ether, srp

# app setup
app = Flask(__name__)
app.secret_key = '123'
init_db(app)

# upload settings
app.config['UPLOAD_FOLDER'] = '/photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# route blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(prof_bp, url_prefix='/profile')
# app.register_blueprint(admin_bp, url_prefix='/admin')

app.register_blueprint(home_bp)
app.register_blueprint(exiftool)
app.register_blueprint(stego_bp)


# make session + year available to templates
@app.context_processor
def inject_context_vars():
    return dict(session=session, current_year=datetime.now().year)


# this handles metadata actions from a form
@app.route('/image-meta', methods=['GET', 'POST'])
def image_meta():
    if request.method == 'POST':
        file = request.files.get('file')
        action = request.form.get('action')

        if not file:
            return "<span style='color:red'>No file selected. Try again.</span>"

        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        saved_path = os.path.join(uploads_dir, file.filename)
        file.save(saved_path)

        try:
            img = Image.open(saved_path)
        except Exception:
            return "Something went wrong opening the image."

        result = ""
        link = None

        if action == "display":
            result = show_meta(img, 1)
            
        elif action == "datetime":
            result = show_meta(img, 2)

        elif action == "remove":
            cleaned_file = clean_meta(img, saved_path)
            if cleaned_file and os.path.exists(cleaned_file):
                link = url_for('download_file', filename=os.path.basename(cleaned_file))
                result = f"Metadata cleaned! <a href='{link}'>Download here</a>"
            else:
                result = "Couldn’t clean metadata. Try another file?"

        return f"<div class='metadata-result unique-meta-result'><pre>{result}</pre></div>"

    return render_template('metadata.html')


# show metadata or just the date tags
def show_meta(img, mode):
    exif = img._getexif()
    if not exif:
        return "No metadata found in this image."

    out = []
    for tag_id, val in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        if mode == 1:
            out.append(f"{tag:25}: {val}")
        elif mode == 2 and ("Date" in tag or "Time" in tag):
            out.append(f"{tag:25}: {val}")

    return "<br>".join(out)


# clean metadata using exiftool
def clean_meta(img, filepath):
    cleaned_path = filepath.rsplit('.', 1)[0] + "_cleaned." + filepath.rsplit('.', 1)[-1]
    try:
        subprocess.run(['exiftool', '-all=', '-o', cleaned_path, filepath], check=True)
        return cleaned_path
    except Exception:
        return None


@app.route('/uploads/<filename>')
def download_file(filename):
    folder = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(folder, filename, as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)

##########################################################################################################ß

    "REFERENCES"

    # https://flask.palletsprojects.com/en/2.3.x/templating/#context-processors
    # https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
    # https://flask.palletsprojects.com/en/2.3.x/api/#incoming-request-data
    # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image._getexif
    # https://exiftool.org/
    # https://flask.palletsprojects.com/en/2.3.x/api/#flask.session
    # https://flask.palletsprojects.com/en/2.3.x/quickstart/#rendering-templatesß
