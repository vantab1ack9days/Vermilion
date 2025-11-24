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
from datetime import datetime
import hashlib
from utils import load_json, save_json
from forms import RegistrationForm
import os


app = Flask(__name__)
app.secret_key = "VERMILION"

@app.route("/", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    users_db = load_json("flask 3/data", "users_db.json")
    if request.method == "POST" and form.validate_on_submit():
        tmp_user = {
            "username": form.username.data,
            "password": hashlib.md5(form.password.data.encode('utf-8')).hexdigest()
        }
        for i in range(1, len(users_db)+1):
            print(12)
            if (users_db[str(i)]["username"] == tmp_user["username"] and users_db[str(i)]["password"] == tmp_user["password"]):
                users_db[str(i)]["last_authorize"] = datetime.now().isoformat()
                save_json("flask 3/data", "users_db.json", users_db)
                return redirect(url_for("create"))
        flash("Пользователь не найден.", "error")
    else:
        print(form.errors)
    return render_template("index.html", form=form)

@app.route("/create", methods=["GET", "POST"])
def create():
    form = RegistrationForm()
    users_db = load_json("flask 3/data", "users_db.json")
    if request.method == "POST" and form.validate_on_submit():
        new_user = {
            "username": form.username.data,
            "password": hashlib.md5(form.password.data.encode('utf-8')).hexdigest(),
            "confirm": hashlib.md5(form.confirm.data.encode('utf-8')).hexdigest(),
            "registration_date": datetime.now().isoformat(),
            "last_authorize": None
        }
        for i in range(1, len(users_db)+1):
            if users_db[str(i)]["username"] == new_user["username"]:
                flash("Имя пользователя занято", "error")
                return redirect(url_for('create'))
        users_db[str(len(users_db) + 1)] = new_user
        save_json("flask 3/data", "users_db.json", users_db)
        flash("Учетная запись добавлена.", "success")
    else:
        print(form.errors)
    return render_template("create.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
