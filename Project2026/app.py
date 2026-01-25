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

#Base.metadata.create_all(engine)

@app.route("/", methods=["GET", "POST"])
def auth():
    
    return render_template('index.html')

@app.route("/teacher_auth", methods=["GET", "POST"])
def teacher_auth():
    form = RegistrationForm()

    return render_template('auth.html', form=form)

@app.route("/student_auth", methods=["GET", "POST"])
def student_auth():
    form = RegistrationForm()

    return render_template('auth.html', form=form)

@app.route("/admin_auth", methods=["GET", "POST"])
def admin_auth():
    form = RegistrationForm()

    return render_template('auth.html', form=form)

@app.route("/auth_create", methods=["GET", "POST"])
def auth_create():
    form = RegistrationForm()
    
    return render_template('auth_create.html', form=form)

@app.route("/main_page", methods=["GET", "POST"])
def main_page():
    
    return render_template('main_page.html')



if __name__ == "__main__":
    app.run(debug=True)
