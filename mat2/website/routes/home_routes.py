from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import User
# from mat2.metadata_tools import display_metadata, display_datetime, remove_metadata
import os
from werkzeug.utils import secure_filename

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

@home_bp.route('/metadata', methods=['GET', 'POST'])
def metadata():
    result = None
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    if request.method == 'POST':
        file = request.files.get('file')
        action = request.form.get('action')
        if not file or file.filename == '':
            result = "No file uploaded."
        else:
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            if action == 'display':
                result = display_metadata(file_path)
            elif action == 'datetime':
                result = display_datetime(file_path)
            elif action == 'remove':
                result = "Metadata removed and cleaned image saved as " + remove_metadata(file_path)
            else:
                result = "Unknown action."
    return render_template('metadata.html', result=result)
