from flask import Flask, render_template, request, url_for, send_from_directory
import uuid
import os
from datetime import datetime
import hashlib

app = Flask(__name__)

root = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(root, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_unique_id():
  return str(uuid.uuid4())

def calculate_md5_hash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

uploaded_files = []
pathes = []
dates = []
hashes = []

not_allowed_types = ['.exe', '.sh', '.php', '.js']

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']
        if file.filename == '':
            return 'No selected file'

        type = os.path.splitext(file.filename)[1]
        if type in not_allowed_types:
            return 'This type of file is not allowed.'

        uploaded_files.append(file.filename)

        file.filename = generate_unique_id() + type
        file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_save_path)
        
        file_hash = calculate_md5_hash(file_save_path)
        if file_hash in hashes:
           os.remove(file_save_path)
           uploaded_files.pop()
           return 'This file has already been uploaded.'
        else:
           hashes.append(file_hash)

        dates.append(datetime.now())

        pathes.append(file_save_path[59:])

    return render_template('index.html', fls = uploaded_files, pathes = pathes, dates = dates)

@app.route("/uploads")
def show():
    file = request.args.get('file')
    return send_from_directory(app.config['UPLOAD_FOLDER'], file[8:])

if __name__ == "__main__":
    app.run(debug=True)