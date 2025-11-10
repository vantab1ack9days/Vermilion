from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
    flash,
    get_flashed_messages,
)
import uuid
import os
from datetime import datetime
import hashlib
import json
import os


app = Flask(__name__)
app.secret_key = "VERMILION"

root = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(root, "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def load_json(folder_name, file_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    full_path = os.path.join(folder_name, file_name)
    if not os.path.exists(full_path):
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(folder_name, file_name, data):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    full_path = os.path.join(folder_name, file_name)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_unique_id():
    return str(uuid.uuid4())


def calculate_md5_hash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


uploaded_files = load_json("data", "files.json")


not_allowed_types = [".exe", ".sh", ".php", ".js"]


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Ошибка: файл не выбран!", "error")
            return redirect(url_for("main"))

        file = request.files["file"]
        if file.filename == "":
            flash("Ошибка: файл не выбран!", "error")
            return redirect(url_for("main"))

        type = os.path.splitext(file.filename)[1]
        if type in not_allowed_types:
            flash("Ошибка: тип данных не поддерживается!", "error")
            return redirect(url_for("main"))

        filename = file.filename

        file.filename = generate_unique_id() + type
        folders = os.path.join(app.config["UPLOAD_FOLDER"], file.filename[:2], file.filename[2:4])
        if not os.path.exists(folders):
            os.makedirs(folders)
        file_save_path = os.path.join(folders, file.filename)
        file.save(file_save_path)

        file_hash = calculate_md5_hash(file_save_path)
        for file_data in uploaded_files:
            if file_hash == file_data["hash"]:
                os.remove(file_save_path)
                uploaded_files.pop()
                flash("Ошибка: файл уже загружен!", "error")
                return redirect(url_for("main"))

        dates = datetime.now().isoformat()
        path = "\\".join(file_save_path.split("\\")[-4:])

        flash("Файл успешно загружен!", "success")
        files_data = {
            "filename": filename,
            "dates": dates,
            "path": path,
            "hash": file_hash,
        }
        uploaded_files.append(files_data)
        save_json("data", "files.json", uploaded_files)

    return render_template("index.html", fls=uploaded_files[::-1])


@app.route("/uploads")
def show():
    file = request.args.get("file")
    return send_from_directory(app.config["UPLOAD_FOLDER"], '/'.join(file.split("\\")[-3:]))


if __name__ == "__main__":
    app.run(debug=True)
