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
from datetime import datetime, timedelta
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
                return redirect(url_for("teacher_page", login=username, role=role))
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
                return redirect(url_for("teacher_page", login=username, role=role))
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

    start_date_str = request.args.get('start_date')
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            # Приводим к понедельнику (если нужно строго по неделям)
            # Но можно оставить как есть — просто сдвиг на 7 дней
        except ValueError:
            start_date = datetime.today().date()
    else:
        start_date = datetime.today().date()

    week_dates = [start_date + timedelta(days=i) for i in range(7)]
    

    for el in session.query(Users).all():
        if el.username == login and role==el.role:
            CURRENT_TEACHER_ID = el.id

    if request.method == "POST" and form.validate_on_submit():
        selected_date = form.date.data
        selected_hour = int(form.hour.data)
        slot_datetime = datetime.combine(selected_date, datetime.min.time().replace(hour=selected_hour))

        existing = session.query(Consultation).filter_by(
            teacher_id=CURRENT_TEACHER_ID,
            start_time=slot_datetime
        ).first()

        if existing:
            flash("Слот на это время уже существует!", "warning")
        else:
            new_slot = Consultation(
                teacher_id=CURRENT_TEACHER_ID,
                start_time=slot_datetime,
                is_open=True
            )
            session.add(new_slot)
            session.commit()
            flash("Слот успешно открыт!", "success")
            # Перенаправляем на ту же неделю
            return redirect(url_for('teacher_page', login=login, role=role, start_date=start_date.strftime('%Y-%m-%d')))

    # === Получаем слоты для текущей недели (для подсветки) ===
    week_start = datetime.combine(start_date, datetime.min.time())
    week_end = week_start + timedelta(days=7)
    week_slots = session.query(Consultation).filter(
        Consultation.teacher_id == CURRENT_TEACHER_ID,
        Consultation.start_time >= week_start,
        Consultation.start_time < week_end
    ).all()
    slot_set = {(s.start_time.date(), s.start_time.hour) for s in week_slots}

    # === Все слоты (для списка внизу) ===
    all_slots = session.query(Consultation).filter_by(
        teacher_id=CURRENT_TEACHER_ID
    ).order_by(Consultation.start_time.desc()).all()

    prev_week = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')

    return render_template(
        'teacher_page.html',
        login=login,
        role=role,
        form=form,
        week_dates=week_dates,
        slot_set=slot_set,
        all_slots=all_slots,
        prev_week=prev_week,
        next_week=next_week
    )

@app.route('/delete_slot/<int:slot_id>', methods=['POST'])
def delete_slot(slot_id):
    login = request.args.get('login')
    role = request.args.get('role')
    CURRENT_TEACHER_ID = 1

    for el in session.query(Users).all():
        if el.username == login and role==el.role:
            CURRENT_TEACHER_ID = el.id


    slot = session.query(Consultation).filter_by(
        id=slot_id,
        teacher_id=CURRENT_TEACHER_ID  # защита: только свои слоты
    ).first()

    if not slot:
        flash("Слот не найден.", "error")
        return redirect(url_for("teacher_page", login=login, role=role))

    if slot.student_id is not None:
        flash("Нельзя удалить слот: на него записан студент.", "error")
        return redirect(url_for("teacher_page", login=login, role=role))

    session.delete(slot)
    session.commit()
    flash("Слот успешно удалён.", "success")
    return redirect(url_for("teacher_page", login=login, role=role))

@app.route("/anonym")
def anonym_page():
    teachers = session.query(Users).filter(Users.role == 'teacher').all()
    return render_template('anonym_page.html', teachers=teachers)



if __name__ == "__main__":
    app.run(debug=True)
