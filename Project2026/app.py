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
from model import *

app = Flask(__name__)
app.secret_key = "VERMILION"

Base.metadata.create_all(engine)

@app.route("/", methods=["GET", "POST"])
def auth():
    
    return render_template('index.html')

@app.route("/teacher_auth", methods=["GET", "POST"])
def teacher_auth():
    role = request.args.get('role')
    print(role)
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        username = request.form.get('username')
        password_hash = hashlib.md5(request.form.get('password').encode('utf-8')).hexdigest()

        users_list = session.query(Users).all()
        for el in users_list:
            if username == el.username and password_hash == el.password_hash and role == el.role:
                return redirect(url_for("main_page", login=username))
        flash("Учётная запись не найдена.", "error")

    return render_template('auth.html', form=form, role=role)

@app.route("/student_auth", methods=["GET", "POST"])
def student_auth():
    role = request.args.get('role')
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        username = request.form.get('username')
        password_hash = hashlib.md5(request.form.get('password').encode('utf-8')).hexdigest()

        users_list = session.query(Users).all()
        for el in users_list:
            if username == el.username and password_hash == el.password_hash and role == el.role:
                return redirect(url_for("main_page", login=username))
        flash("Учётная запись не найдена.", "error")

    return render_template('auth.html', form=form, role=role)

@app.route("/admin_auth", methods=["GET", "POST"])
def admin_auth():
    role = request.args.get('role')
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        username = request.form.get('username')
        password_hash = hashlib.md5(request.form.get('password').encode('utf-8')).hexdigest()

        users_list = session.query(Users).all()
        for el in users_list:
            if username == el.username and password_hash == el.password_hash and role == el.role:
                return redirect(url_for("main_page", login=username))
        flash("Учётная запись не найдена.", "error")

    return render_template('auth.html', form=form, role=role)

@app.route("/auth_create", methods=["GET", "POST"])
def auth_create():
    role = request.args.get('role')
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        username = request.form.get('username')
        password_hash = hashlib.md5(request.form.get('password').encode('utf-8')).hexdigest()

        users_list = session.query(Users).all()
        for el in users_list:
            if username == el.username:
                flash("Имя пользователя занято", "error")
                return redirect(url_for('auth_create'))
        new_user = Users(username = username, password_hash = password_hash, role = role)
        session.add_all([new_user])
        session.commit()

    return render_template('auth_create.html', form=form)

@app.route("/main_page", methods=["GET", "POST"])
def main_page():
    login = request.args.get('login')

    return render_template('main_page.html', login=login)



if __name__ == "__main__":
    app.run(debug=True)
