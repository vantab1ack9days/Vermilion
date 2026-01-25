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
from forms import *
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
                return redirect(url_for("teacher_page", login=username, role=role))
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
                return redirect(url_for("main_page", login=username, role=role))
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
                return redirect(url_for("main_page", login=username, role=role))
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


@app.route("/teacher_page", methods=["GET", "POST"])
def teacher_page():
    login = request.args.get('login')
    role = request.args.get('role')
    form = OpenSlotForm()
    CURRENT_TEACHER_ID = 1

    for el in session.query(Users).all():
        if el.username == login and role==el.role:
            CURRENT_TEACHER_ID = el.id

    if request.method == "POST" and form.validate_on_submit():
        selected_date = form.date.data  # это объект date
        selected_hour = int(form.hour.data)

        slot_datetime = datetime.combine(selected_date, datetime.min.time().replace(hour=selected_hour))

        existing = session.query(Consultation).filter_by(
            teacher_id=CURRENT_TEACHER_ID,
            start_time=slot_datetime
        ).first()

        if existing:
            flash("Слот на это время уже существует!", "error")
        else:
            new_slot = Consultation(
                teacher_id=CURRENT_TEACHER_ID,
                start_time=slot_datetime,
                is_open=True
            )
            session.add(new_slot)
            session.commit()
            flash("Слот успешно открыт!", "success")
            return redirect(url_for('teacher_page', login=login, role=role))

    from datetime import timedelta
    today = datetime.today().date()
    week_dates = [today + timedelta(days=i) for i in range(7)]

    slots = session.query(Consultation).filter(
        Consultation.teacher_id == CURRENT_TEACHER_ID,
        Consultation.start_time >= datetime.combine(today, datetime.min.time()),
        Consultation.start_time < datetime.combine(today + timedelta(days=7), datetime.min.time())
    ).all()

    slot_set = {(s.start_time.date(), s.start_time.hour) for s in slots}

    return render_template('teacher_page.html', login=login, role=role, form=form, week_dates=week_dates, slot_set=slot_set)




if __name__ == "__main__":
    app.run(debug=True)
