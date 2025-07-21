from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import User
import os
import subprocess
import urllib.request
import urllib.parse
import json

exif_bp = Blueprint('exif', __name__)


      


@exif_bp.route('/mdstrip', methods=['GET', 'POST'])
def mdstrip():
    if request.method == 'POST':
        file = request.files['file']
        exif_option = request.form['exif_option']
        
        if file and exif_option:
            filename = file.filename
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
       
            exiftool_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'exif', 'exiftool-13.32_64', 'exiftool.exe')
            
            if not os.path.exists(exiftool_path):
                flash(f"Exiftool not found at: {exiftool_path}", 'error')
                return render_template('mdstrip.html')
                
            exiftool_cmd = [exiftool_path]
            
            if exif_option == 'comment':
                exif_value = request.form['exif_value']
                exiftool_cmd.extend([f'-Comment={exif_value}'])
            
            elif exif_option == 'creation_time':
                exif_value = request.form['exif_value']
                exiftool_cmd.extend([
                    f'-DateTime={exif_value}',
                    f'-DateTimeOriginal={exif_value}',
                    f'-CreateDate={exif_value}'
                ])
            
            elif exif_option == 'gps_location':
                location_name = request.form['exif_value']
               
          
            
            elif exif_option == 'artist':
                exif_value = request.form['exif_value']
                exiftool_cmd.extend([f'-Artist={exif_value}'])
            
            exiftool_cmd.extend(['-overwrite_original', filepath])
            
            try:
                result = subprocess.run(exiftool_cmd, capture_output=True, text=True, check=True)
                print(f"Exiftool output: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Exiftool error: {e.stderr}")
                flash(f"Error modifying EXIF data: {e.stderr}", 'error')
                return render_template('mdstrip.html')
            
            updated_filepath = filepath  
            from flask import send_file
            return send_file(updated_filepath, as_attachment=True)
            
        else:
            flash('Please select a file and EXIF option', 'error')
            
    return render_template('mdstrip.html')