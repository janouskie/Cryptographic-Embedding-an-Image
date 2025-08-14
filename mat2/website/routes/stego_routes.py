from flask import Blueprint, render_template, request, url_for, send_from_directory, current_app
import os
import subprocess
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import platform

stego_bp = Blueprint('stego', __name__)

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Path to exiftool (Mac/Linux version, must be installed and in PATH)
#EXIFTOOL_PATH = '/opt/homebrew/bin/exiftool'
"ON WINDOWS MACHINE use:" 
EXIFTOOL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'exif', 'exiftool-13.32_64', 'exiftool.exe'))

# Only these fields can be embedded
EMBED_FIELDS = {
    'author': ['Artist', 'Author', 'Creator'],
    'creation_time': ['DateTimeOriginal', 'CreateDate', 'ModifyDate'],
    'location': ['GPSLatitude', 'GPSLongitude', 'GPSPosition'],
    'device_type': ['Model', 'Make']
}


@stego_bp.route('/stego', methods=['GET', 'POST'])
def stego():
    result = None
    error = None
    download_link = None
    extracted_data = None
    action = None
    
    if request.method == 'POST':
        action = request.form.get('action', 'embed')
        file = request.files.get('file')
        
        if not file:
            error = "No file selected."
            return render_template('steg.html', error=error, action=action)
        
        saved_path = os.path.join(UPLOADS_DIR, secure_filename(file.filename))
        file.save(saved_path)

        if action == 'embed':
           
            selected_types = request.form.getlist('metadata_types')
            if not selected_types:
                error = "Please select at least one metadata type to embed."
                return render_template('steg.html', error=error, action=action)

            # Extract only the selected data 
            txtfile = meta_parse(saved_path, selected_types)
            if txtfile:
                lsbfile = lsbembed(saved_path, txtfile)
                if lsbfile:
                    download_link = url_for('stego.getfile', filename=os.path.basename(lsbfile))
                    result = "Metadata embedded via LSB!"
                else:
                    error = "LSB embedding failed"
            else:
                error = "Metadata extraction failed"
                
        elif action == 'extract':
            # extraction logic
            extracted_text = lsbextract(saved_path)
            if extracted_text:
                extracted_data = extracted_text
                result = "Metadata extracted successfully!"
            else:
                error = "No hidden metadata found or extraction failed"

    return render_template('steg.html', result=result, error=error, download_link=download_link, 
                         extracted_data=extracted_data, action=action)

@stego_bp.route('/stego/download/<filename>')
def getfile(filename):
    return send_from_directory(UPLOADS_DIR, filename, as_attachment=True)

#function to write device name if author not in metadata
def get_current_device():
    try:
        return platform.node()  
    except:
        return "Unknown Device"

def meta_parse(imagepath, selectedtypes):
    try:
        result = subprocess.run([EXIFTOOL_PATH, '-j', imagepath], capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout)[0]
        
        txtpath = os.path.splitext(imagepath)[0] + '_metadata.txt'
        hasdata = False
        
        with open(txtpath, 'w', encoding='utf-8') as f:
            # Author
            if 'author' in selectedtypes:
                author = next((metadata.get(tag) for tag in EMBED_FIELDS['author'] if metadata.get(tag)), None)
                if author:
                    f.write(f"Author: {author}\n")
                    hasdata = True
                else:
                    # If no author found use current device name
                    current_device = get_current_device()
                    f.write(f"Author: {current_device}\n")
                    hasdata = True
                    
            # Creation Time
            if 'creation_time' in selectedtypes:
                creation = next((metadata.get(tag) for tag in EMBED_FIELDS['creation_time'] if metadata.get(tag)), None)
                if creation:
                    f.write(f"CreationTime: {creation}\n")
                    hasdata = True
                    
            # Location
            if 'location' in selectedtypes:
                lat = metadata.get('GPSLatitude')
                lon = metadata.get('GPSLongitude')
                if lat and lon:
                    f.write(f"Location: {lat}, {lon}\n")
                    hasdata = True
                    
            # Device Type
            if 'device_type' in selectedtypes:
                model = metadata.get('Model')
                make = metadata.get('Make')
                if model and make:
                    f.write(f"DeviceType: {make} {model}\n")
                    hasdata = True
                elif model:
                    f.write(f"DeviceType: {model}\n")
                    hasdata = True
                elif make:
                    f.write(f"DeviceType: {make}\n")
                    hasdata = True
        
        if hasdata:
            return txtpath
        else:
            return None
            
    except Exception as e:
        return None

def lsbembed(imagepath, txtfile):
    try:
        # Support PNG and JPG
        fileext = os.path.splitext(imagepath)[1].lower()
        if fileext not in ['.png', '.jpg', '.jpeg']:
            return None
            
        with open(txtfile, 'r', encoding='utf-8') as f:
            data = f.read()
        data += chr(0)  # Null terminator tells its end of lsb embedding

        # Convert data to bits
        bits = []
        for char in data:
            bits.extend([int(b) for b in format(ord(char), '08b')])

        img = Image.open(imagepath)
        img = img.convert('RGB')
        pixels = img.load()
        w, h = img.size

        totalpixels = w * h
        if len(bits) > totalpixels * 3:
            return None

        outimg = img.copy()
        idx = 0
        for y in range(h):
            for x in range(w):
                if idx >= len(bits):
                    break
                r, g, b = pixels[x, y]
                r = (r & ~1) | bits[idx] if idx < len(bits) else r
                idx += 1
                g = (g & ~1) | bits[idx] if idx < len(bits) else g
                idx += 1
                b = (b & ~1) | bits[idx] if idx < len(bits) else b
                idx += 1
                outimg.putpixel((x, y), (r, g, b))
            if idx >= len(bits):
                break

        # Save as PNG to preserve LSB
        outpath = os.path.splitext(imagepath)[0] + '_lsb.png'
        outimg.save(outpath, 'PNG')
        return outpath
    except Exception as e:
        return None

def lsbextract(imagepath):
    """Extract hidden data from LSB-embedded image"""
    try:
        img = Image.open(imagepath)
        img = img.convert('RGB')
        pixels = img.load()
        w, h = img.size

        # Extract bits from LSB of R/G/B
        bits = []
        for y in range(h):
            for x in range(w):
                r, g, b = pixels[x, y]
                bits.append(r & 1)  
                bits.append(g & 1)  
                bits.append(b & 1)  

        # Convert bits back to characters
        chars = []
        for i in range(0, len(bits), 8):
            if i + 7 < len(bits):
                byte_bits = bits[i:i+8]
                byte_value = 0
                for j, bit in enumerate(byte_bits):
                    byte_value |= (bit << (7-j))

                if byte_value == 0:  # Stops once null is found
                    break
                    
                chars.append(chr(byte_value))

        extracted_text = ''.join(chars)
        
        # Only return if we found  data
        if extracted_text and len(extracted_text.strip()) > 0:
            return extracted_text
        else:
            return None
            
    except Exception as e:
        return None
