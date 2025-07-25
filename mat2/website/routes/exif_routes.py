from flask import Blueprint, render_template, request, flash, send_file
import os
import subprocess

exif_bp = Blueprint('exif', __name__)

@exif_bp.route('/mdstrip', methods=['GET', 'POST'])


def mdstrip():
    metadata_output = []
    
    if request.method == 'POST':
        up = request.files.get('file')
        opt = request.form.get('exif_option')
        action = request.form.get('action', 'view')

        if not up or not opt:
            flash("Oops — you need both a file and an EXIF option.", "error")
            return render_template('mdstrip.html')

        fname = up.filename
        uploads = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(uploads, exist_ok=True)
        path = os.path.join(uploads, fname)
        up.save(path)

        exiftool = 'exiftool'
        cmd = [exiftool]

        # try:
        #     read_cmd = ['exiftool', path]
        #     read_result = subprocess.run(read_cmd, capture_output=True, text=True)
        #     metadata_output.append("METADATA ")
        #     if read_result.stdout:
        #         lines = read_result.stdout.strip().split('\n')
        #         for line in lines:
        #             if line.strip():
        #                 metadata_output.append(line.strip())
                        
        # except Exception as e:
        #     print("Error!")
            
            
        if opt == 'comment':
            val = request.form.get('exif_value', '')
            cmd.append(f'-Comment={val}')

        elif opt == 'creation_time':
            dt = request.form.get('exif_value', '')
            cmd.extend([
                f'-DateTime={dt}',
                f'-DateTimeOriginal={dt}',
                f'-CreateDate={dt}'
            ])

        elif opt == 'gps_location':
            loc = request.form.get('exif_value', '')
            # sketch: geo lookup could go here
            print("GPS tweak placeholder:", loc)

        elif opt == 'artist':
            art = request.form.get('exif_value', '')
            cmd.append(f'-Artist={art}')
            
        elif opt == 'view':
            try: 
                result = subprocess.run(
                    [exiftool, path],
                    capture_output=True,
                    text=True,
                    check = True
                )
                
                metadata_output = result.stdout
                return render_template('mdstrip.html', metadata_output=metadata_output)
            except subprocess.CalledProcessError as e:
                print("Error!")

        cmd.extend(['-overwrite_original', path])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("Exiftool output:", result.stdout.strip())
        except subprocess.CalledProcessError as ex:
            print("Exiftool error:", ex.stderr.strip())
            flash("Exif operation failed — please check your input.", "error")
            return render_template('mdstrip.html')

        return send_file(path, as_attachment=True)

    return render_template('mdstrip.html')
