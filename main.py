from flask import Flask, render_template, request, session, redirect
import smtplib
from email.message import EmailMessage
import secrets
import time
from data.user import User
from data import db_session

app = Flask(__name__)
app.secret_key = 'f8874661e03139f344aa90692fd4d642b1e7a89b9b817bba'


@app.route('/')
def hello_window():
    return render_template('hello_window.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        session.pop('email_true', None)
        return render_template('registration.html', info=None, code_cheker=1)
    elif request.method == 'POST':
        action = request.form.get('action')
        if action == 'verify':
            input_code = request.form.get('verification_code')
            code_real = session.get('code', '')
            if input_code:
                if input_code == code_real:
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
                    return render_template('election_course.html')
                else:
                    return render_template('registration.html', info=1, code_cheker=0)
            else:
                return render_template('registration.html', info=1, code_cheker=0)
        email = request.form.get('email', '').strip()
        session['email'] = email
        if not session.get('email_true'):
            if email:
                code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
                session['code'] = code
                session['last_mess'] = time.time()
                session['last_mail'] = time.time()
                msg = EmailMessage()
                msg.set_content(f"Код подтверждения: {code} ")
                msg["Subject"] = f"Код {code}"
                msg["From"] = "leshahit56@gmail.com"
                msg["To"] = email

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login("leshahit56@gmail.com", "extwxvadtwvdvgji")
                    server.send_message(msg)

                session['email_true'] = True
                return render_template('registration.html', info=1, code_cheker=1)
            else:
                return render_template('registration.html', info=0, code_cheker=1)
        else:
            if email:
                last_mail = session.get('last_mail', 0)
                if time.time() - last_mail > 10:
                    code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
                    session['code'] = code
                    msg = EmailMessage()
                    msg.set_content(f"Код подтверждения: {code}")
                    msg["Subject"] = f"Код {code}"
                    msg["From"] = "leshahit56@gmail.com"
                    msg["To"] = email

                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login("leshahit56@gmail.com", "extwxvadtwvdvgji")
                        server.send_message(msg)
                        session['last_mail'] = time.time()
                
                return render_template('registration.html', info=1, code_cheker=1)

            else:
                return render_template('registration.html', info=1, code_cheker=1)


@app.route('/login')
def login():
    return "<h1>авторизация</h1>"


@app.route('/election_course')
def election_course():
    return render_template('election_course.html')


@app.route('/settings')
def settings():
    return "<h1>settings</h1>"


@app.route('/profile')
def profile():
    return "<h1>profile</h1>"


@app.route('/course')
def course():
    return redirect('/election_course')

@app.route('/course/python')
def coursepython():
    return "<h1>/course/python</h1>"

@app.route('/test')
def test_selection():
    return render_template('test_selection.html')

@app.route('/test/1')
def test_1():
    return render_template('test_1.html')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
