from flask import Flask
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/')
def hello():
    return 'intro intro'

app.run(host="0.0.0.0", port=80)



UPLOAD_FOLDER = '/photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



