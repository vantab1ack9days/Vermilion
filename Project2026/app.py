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
import mimetypes
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "VERMILION"

Base.metadata.create_all(engine)

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}

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
                return redirect(url_for("student_page", login=username, role=role))
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




#--------------------- ПРЕПОДАВАТЕЛЬ ---------------------


@app.route("/teacher_page", methods=["GET", "POST"])
def teacher_page():
    login = request.args.get('login')
    role = request.args.get('role')
    form = OpenSlotForm()
    bio_form = BioForm()
    user = session.query(Users).filter_by(username=login, role=role).first()
    CURRENT_TEACHER_ID = user.id
    photo_url = user.photo_path or None  # будет None, если нет аватарки

    if request.method == "POST" and bio_form.submit_bio.data and bio_form.validate_on_submit():
        user.bio = bio_form.bio.data.strip() or ""
        session.commit()
        flash("Биография успешно обновлена!", "success")
        return redirect(url_for('teacher_page', login=login, role=role))

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

    # Свободные: is_open=True И student_id=None
    open_slot_set = {
        (s.start_time.date(), s.start_time.hour)
        for s in week_slots
        if s.is_open and s.student_id is None
    }

    # Занятые: student_id IS NOT NULL (или is_open=False — зависит от логики)
    booked_slot_set = {
        (s.start_time.date(), s.start_time.hour)
        for s in week_slots
        if not s.is_open  # или: not s.is_open
    }

    # === Все слоты (для списка внизу) ===
    all_slots = session.query(Consultation).filter_by(
        teacher_id=CURRENT_TEACHER_ID
    ).order_by(Consultation.start_time.desc()).all()

    for i in all_slots:
        for j in session.query(Users).filter_by(role = 'student').all():
            if i.student_id == j.id:
                i.student_id = j.username
                print(i.student_id)
        

    prev_week = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')

    return render_template(
        'teacher_page.html',
        login=login,
        role=role,
        form=form,
        bio_form=bio_form,
        week_dates=week_dates,
        open_slot_set=open_slot_set,
        booked_slot_set=booked_slot_set,
        all_slots=all_slots,
        prev_week=prev_week,
        next_week=next_week,
        photo_url=photo_url,
        current_bio=user.bio or ""
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


#--------------------- АНОНИМ ---------------------

@app.route("/anonym")
def anonym_page():
    teachers = session.query(Users).filter(Users.role == 'teacher').all()
    return render_template('anonym_page.html', teachers=teachers)

@app.route("/upload_avatar", methods=["POST"])
def upload_avatar():
    login = request.args.get('login')
    role = request.args.get('role')
    user = session.query(Users).filter_by(username=login, role=role).first()
    file = request.files['avatar']
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type not in ALLOWED_MIME_TYPES:
        flash("Недопустимый формат файла. Разрешены: JPG, PNG, GIF.", "error")
        return redirect(url_for('teacher_page', login=login, role=role))
    filename = secure_filename(f"{user.id}_{file.filename.lower()}")
    filepath = os.path.join("static", "avatars", filename)
    file.save(filepath)
    user.photo_path = f"avatars/{filename}"
    session.commit()
    flash("Аватар успешно обновлён!", "success")
    return redirect(url_for('teacher_page', login=login, role=role))







#--------------------- СТУДЕНТ ---------------------

@app.route("/student_page", methods=["GET", "POST"])
def student_page():
    login = request.args.get('login')
    role = request.args.get('role')
    teachers = session.query(Users).filter(Users.role == 'teacher').all()

    student = session.query(Users).filter_by(username=login, role='student').first()
    
    bookings = session.query(Consultation)\
            .filter(Consultation.student_id == student.id)\
            .order_by(Consultation.start_time.desc())\
            .all()

    return render_template(
        'student_page.html',
        login=login,
        role=role,
        bookings=bookings,
        teachers=teachers
    )

@app.route('/schedule/<int:teacher_id>')
def student_schedule(teacher_id):
    login = request.args.get('login')
    role = request.args.get('role')
    teacher = session.query(Users).filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        flash("Преподаватель не найден", "error")
        return redirect(url_for('index'))

    start_date_str = request.args.get('start_date')
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = datetime.today().date()
    else:
        start_date = datetime.today().date()

    week_dates = [start_date + timedelta(days=i) for i in range(7)]
    week_start = datetime.combine(start_date, datetime.min.time())
    week_end = week_start + timedelta(days=7)

    # Свободные слоты: открыты + нет студента
    available_slots = session.query(Consultation).filter(
        Consultation.teacher_id == teacher_id,
        Consultation.is_open == True,
        Consultation.student_id.is_(None),
        Consultation.start_time >= week_start,
        Consultation.start_time < week_end
    ).all()

    # Карта: (дата, час) → slot_id
    slot_map = {
        (s.start_time.date(), s.start_time.hour): s.id
        for s in available_slots
    }

    prev_week = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')


    return render_template(
        'student_schedule.html',
        login=login,
        role=role,
        teacher=teacher,
        week_dates=week_dates,
        slot_map=slot_map,
        prev_week=prev_week,
        next_week=next_week,
        current_teacher_id=teacher_id
    )

@app.route('/book_slot/<int:slot_id>', methods=['POST'])
def book_slot(slot_id):
    login = request.args.get('login')
    role = request.args.get('role')
    CURRENT_STUDENT_ID = 1
    for el in session.query(Users).all():
        if el.username == login and role==el.role:
            CURRENT_STUDENT_ID = el.id
    
    slot = session.query(Consultation).filter_by(
        id=slot_id,
        is_open=True,
        student_id=None
    ).first()

    if not slot:
        flash("Слот недоступен", "error")
        return redirect(request.referrer or url_for('index'))

    # Проверка конфликта времени (опционально)
    conflict = session.query(Consultation).filter_by(
        student_id=CURRENT_STUDENT_ID,
        start_time=slot.start_time
    ).first()
    if conflict:
        flash("Вы уже записаны на другую консультацию в это время", "warning")
        return redirect(request.referrer)

    slot.student_id = CURRENT_STUDENT_ID
    slot.is_open = False  # можно оставить True — зависит от логики
    session.commit()
    flash("Вы успешно записались!", "success")
    return redirect(request.referrer)


if __name__ == "__main__":
    app.run(debug=True)
