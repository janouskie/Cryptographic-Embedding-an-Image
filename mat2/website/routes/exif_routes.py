from flask import Blueprint, render_template, request, send_file
import os
import subprocess


exiftool = Blueprint('exif', __name__)

# Section for metadata removal & viewing

@exiftool.route('/mdstrip', methods=['GET', 'POST']) #

def mdstrip():

  if request.method == 'POST':

    # if User decided to save their metadata

    if 'save' in request.form:

      metadata = request.form.get('metadata')
      file = request.form.get('original_file')
      upload = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
      path =os.path.join(upload, file)

      # Then saved into JSON file

      temp = os.path.join(upload, 'temp_metadata.json')

      with open(temp, 'w') as f:
        f.write(metadata)

      subprocess.run(['exiftool', f'-json={temp}', '-overwrite_original', path])
      return send_file(path, as_attachment=True)

    up = request.files.get('file')
    opt =request.form.get('exif_option')
    val= request.form.get('exif_val', '')



    # if user has selected an option of their choice

    if not up or not opt:
      
      return render_template('mdstrip.html')

    fname = up.filename
    upload = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(upload, exist_ok=True)
    path = os.path.join(upload, fname)
    up.save(path)



    # if the file you uploaded has .jpg

    if opt == 'view':

      try: # get the metadata

        result = subprocess.run(['exiftool', '-j', path], capture_output=True, text=True, check=True)
        output = result.stdout
      except subprocess.CalledProcessError: # case of failure
        output = ""

      # Only pass metadata_output when viewing

      return render_template('mdstrip.html', metadata_output=output, original_file=fname)

    # For all other options, don't pass metadata_output

    cmd = ['exiftool', '-overwrite_original']

    if opt == 'comment':
      cmd.append(f'-Comment={val}')
    elif opt == 'artist':
      cmd.append(f'-Artist={val}')
    cmd.append(path)

    # Clean the metadata
    try:

     subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:

     return render_template('mdstrip.html')
    return send_file(path, as_attachment=True)



  # On GET, don't pass metadata_output
  return render_template('mdstrip.html')
