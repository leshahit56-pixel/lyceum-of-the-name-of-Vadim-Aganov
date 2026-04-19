from flask import Flask, render_template, request, session, redirect, url_for
from functools import wraps
import smtplib
from email.message import EmailMessage
import secrets
import time
from data.user import User
from data import db_session
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'f8874661e03139f344aa90692fd4d642b1e7a89b9b817bba')
app.permanent_session_lifetime = timedelta(days=30)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('if_not_auth'))
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    email = session.get('email')
    if not email:
        return None
    try:
        db_session.global_init('db/blogs.db')
        ses = db_session.create_session()
        user = ses.query(User).filter(User.email == email).first()
        ses.close()
        return user
    except:
        return None


@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())


@app.route('/')
def hello_window():
    if 'email' in session:
        return redirect(url_for('election_course'))
    return render_template('hello_window.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if 'email' in session:
            return redirect(url_for('election_course'))
        session.pop('email_true', None)
        return render_template('registration.html', info=None, code_cheker=1, email_exists=False)
    elif request.method == 'POST':
        action = request.form.get('action')
        if action == 'verify':
            input_code = request.form.get('verification_code')
            code_real = session.get('code', '')
            if input_code:
                time_code = session.get('code_date', 0)
                if input_code == code_real and time.time() - time_code < 601:
                    db_session.global_init('db/blogs.db')
                    email = session.get('email', '')
                    name = request.form.get('name')
                    surname = request.form.get('surname')
                    patronymic = request.form.get('patronymic')
                    new_user = User()
                    new_user.email = email
                    new_user.name = name
                    new_user.surname = surname
                    new_user.patronymic = patronymic
                    ses = db_session.create_session()
                    ses.add(new_user)
                    ses.commit()
                    ses.close()
                    session.permanent = True
                    session['email'] = email
                    return redirect(url_for('election_course'))
                else:
                    return render_template('registration.html', info=1, code_cheker=0, email_exists=False)
            else:
                return render_template('registration.html', info=1, code_cheker=0, email_exists=False)
        else:
            email = request.form.get('email', '').strip()
            session['email'] = email

            last_mail = session.get('last_mail', 0)
            if time.time() - last_mail < 10:
                return render_template('registration.html', info=1, code_cheker=1, email_exists=False)
            if email:
                db_session.global_init('db/blogs.db')
                ses = db_session.create_session()
                user_check = ses.query(User).filter(User.email == email).first()
                ses.close()
                if user_check:
                    return render_template('registration.html', info=None, code_cheker=0, email_exists=True)
                session['last_mail'] = time.time()
                code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
                session['code_date'] = time.time()
                session['code'] = code

                try:
                    msg = EmailMessage()
                    msg.set_content(f"Код подтверждения: {code}")
                    msg["Subject"] = f"Код {code}"
                    msg["From"] = "leshahit56@gmail.com"
                    msg["To"] = email

                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
                        server.send_message(msg)
                except:
                    pass

                session['email_true'] = True
                return render_template('registration.html', info=1, code_cheker=1, email_exists=False)

            return render_template('registration.html', info=0, code_cheker=1, email_exists=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'email' in session:
            return redirect(url_for('election_course'))
        session.pop('email_first', None)
        return render_template('autorization.html', email_checker=False, email_exists=False)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'verify':
            code = request.form.get('verification_code')
            real_code = session.get('code_real', '')
            code_date = session.get('code_date', 0)
            if code == real_code and time.time() - code_date < 601:
                session.permanent = True
                return redirect(url_for('election_course'))
            else:
                return render_template('autorization.html', email_checker=True, email_exists=False, code_exists=True)

        else:
            email = request.form.get('email', '').strip()
            session['email'] = email

            db_session.global_init('db/blogs.db')
            ses = db_session.create_session()
            chek_email = ses.query(User).filter(User.email == email).first()
            ses.close()

            last_mess = session.get('last_mess', 0)

            if time.time() - last_mess < 10:
                return render_template('autorization.html', email_checker=True, email_exists=False)

            if chek_email:
                code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
                session['code_date'] = time.time()
                session['code_real'] = code
                session['last_mess'] = time.time()

                try:
                    msg = EmailMessage()
                    msg.set_content(f"Код подтверждения: {code}")
                    msg["Subject"] = f"Код {code}"
                    msg["From"] = "leshahit56@gmail.com"
                    msg["To"] = email

                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
                        server.send_message(msg)
                except:
                    pass

                return render_template('autorization.html', email=email, email_checker=True, email_exists=False)
            else:
                return render_template('autorization.html', email=email, email_checker=False, email_exists=True)


@app.route('/election_course')
@login_required
def election_course():
    user = get_current_user()
    return render_template('election_course.html', Name=user.name, Surname=user.surname)


@app.route('/if_not_auth', methods=['GET', 'POST'])
def if_not_auth():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'reg':
            return redirect(url_for('register'))
        elif action == 'aut':
            return redirect(url_for('login'))

    return render_template('if_not_autorization.html')


@app.route('/settings')
@login_required
def settings():
    user = get_current_user()
    return render_template('settings.html', Name=user.name, Surname=user.surname)


@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    return render_template('profile.html', Name=user.name, Surname=user.surname)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello_window'))


@app.route('/course')
@login_required
def course():
    return redirect(url_for('election_course'))


@app.route('/course/python')
@login_required
def coursepython():
    return render_template('course_python.html')


@app.route('/test')
def test_selection():
    return render_template('test_selection.html')


@app.route('/test/1')
def test_1():
    return render_template('test_1.html')


@app.route('/test/2')
def test_2():
    return render_template('test_2.html')


@app.route('/test/3')
def test_3():
    return render_template('test_3.html')


@app.route('/test/4')
def test_4():
    return render_template('test_4.html')


@app.route('/test/5')
def test_5():
    return render_template('test_5.html')


@app.route('/test/6')
def test_6():
    return render_template('test_6.html')


@app.route('/course/python/hello_world')
def hello_world():
    return render_template('first_lesson.html')


@app.route('/book_for_first_lessonn')
def book_for_first():
    return render_template('book_for_first_lessonn.html')


@app.route('/course/python/lesson/<int:lesson_id>/task/<int:task_order>')
@login_required
def task(lesson_id, task_order):
    task = {
        'title': 'Ваша первая программа',
        'points': 10,
        'description': '<p>Напишите программу, которая выводит "Привет, мир!"</p>',
    }

    return render_template('task.html', task=task)


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
