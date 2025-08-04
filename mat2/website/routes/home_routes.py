from flask import Blueprint, render_template, request
from models import User
from mat2.metadata_tools import display_metadata, display_datetime, remove_metadata
from werkzeug.utils import secure_filename
import os
import hashlib

home_bp = Blueprint('home', __name__)
UPLOAD_DIR = "uploads"

# make sure upload dir is always there
os.makedirs(UPLOAD_DIR, exist_ok=True)


@home_bp.route('/')
def index():
    return render_template('index.html')


@home_bp.route('/home')
def home():
    return render_template('home.html')

@home_bp.route('/stego')
def stego():
    return render_template('steg.html')



@home_bp.route('/mdstrip')
def mdstrip():
    return render_template('mdstrip.html')


def get_file_hash(file_obj):
    """Just returns the sha256 for a file stream."""
    h = hashlib.sha256()
    for chunk in iter(lambda: file_obj.read(4096), b""):
        h.update(chunk)
    file_obj.seek(0)
    return h.hexdigest()


@home_bp.route('/hash', methods=['GET', 'POST'])
def hash():
    result = None

    if request.method == 'POST':
        file_a = request.files.get('file1')
        file_b = request.files.get('file2')

        if not file_a or not file_b:
            result = "Both files need to be selected."
        else:
            hash_a = get_file_hash(file_a)
            hash_b = get_file_hash(file_b)

            if hash_a == hash_b:
                result = f"Files match. Hash: {hash_a}"
            else:
                result = (
                    "Files are different.<br>"
                    f"File 1: {hash_a}<br>"
                    f"File 2: {hash_b}"
                )

    return render_template('hash.html', result=result)


def save_uploaded_file(file):
    """Saves the file to uploads/ and returns the full path"""
    name = secure_filename(file.filename)
    full_path = os.path.join(UPLOAD_DIR, name)
    file.save(full_path)
    return full_path


@home_bp.route('/metadata', methods=['GET', 'POST'])
def metadata():
    result = None

    if request.method == 'POST':
        uploaded = request.files.get('file')
        action = request.form.get('action')

        if not uploaded or not uploaded.filename:
            result = "You forgot to select a file."
        else:
            path = save_uploaded_file(uploaded)

            if action == 'display':
                result = display_metadata(path)
            elif action == 'datetime':
                result = display_datetime(path)
            elif action == 'remove':
                cleaned_path = remove_metadata(path)
                result = f"Metadata cleared. Clean version saved as: {cleaned_path}"
            else:
                result = "Not sure what you wanted to do."

    return render_template('metadata.html', result=result)
