from flask import Flask, render_template, request, url_for, send_from_directory
import uuid
import os

app = Flask(__name__)

root = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(root, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_unique_id():
  return str(uuid.uuid4())

uploaded_files = []
pathes = []
dates = []

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']
        if file.filename == '':
            return 'No selected file'

        uploaded_files.append(file.filename)

        type = os.path.splitext(file.filename)

        file.filename = generate_unique_id() + type[1]
        file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_save_path)


        pathes.append(file_save_path[59:])

    return render_template('index.html', fls = uploaded_files, pathes = pathes)

@app.route("/uploads")
def show():
    file = request.args.get('file')
    return send_from_directory(app.config['UPLOAD_FOLDER'], file[8:])

if __name__ == "__main__":
    app.run(debug=True)