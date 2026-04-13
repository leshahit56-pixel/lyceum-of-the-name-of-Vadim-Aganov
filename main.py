from flask import Flask, render_template, request, session, redirect, url_for
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
        return render_template('registration.html', info=None, code_cheker=1, email_exists=False)
    elif request.method == 'POST':
        action = request.form.get('action')
        if action == 'verify':
            input_code = request.form.get('verification_code')
            code_real = session.get('code', '')
            if input_code:
                time_code = session.get('code_date', 0)
                if input_code == code_real and time.time() - time_code < 601 :
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
                    if user_check:
                        return render_template('registration.html', info=None, code_cheker=0, email_exists=True)
                    session['last_mail'] = time.time()
                    code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
                    session['code_date'] = time.time()
                    session['code'] = code
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
                    return render_template('registration.html', info=1, code_cheker=1, email_exists=False)
                
            return render_template('registration.html', info=0, code_cheker=1, email_exists=False)
            


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session.pop('email_first', None)
        return render_template('autorization.html', email_checker=False, email_exists=False)
    
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'verify':
            code = request.form.get('verification_code')
            real_code = session.get('code_real', 0)
            code_date = session.get('code_date', 0)
            if code == real_code and time.time() - code_date < 601:
                return redirect(url_for('election_course')) 
            else:
                return render_template('autorization.html', email_checker=True, email_exists=False, code_exists=True)

        else:

            email = request.form.get('email', '').strip()
            session['email'] = email

            db_session.global_init('db/blogs.db')
            ses = db_session.create_session()
            chek_email = ses.query(User).filter(User.email == email).first()

            last_mess = session.get('last_mess', 0)

            if time.time() - last_mess < 10:
                return render_template('autorization.html', email_checker=True, email_exists=False)

                

            if chek_email:
                code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
                session['code_date'] = time.time()
                session['code_real'] = code

                session['last_mess'] = time.time()

                msg = EmailMessage()
                msg.set_content(f"Код подтверждения: {code} ")
                msg["Subject"] = f"Код {code}"
                msg["From"] = "leshahit56@gmail.com"
                msg["To"] = email

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login("leshahit56@gmail.com", "extwxvadtwvdvgji")
                    server.send_message(msg)
                return render_template('autorization.html', email=email, email_checker=True, email_exists=False)
            
            else:
                return render_template('autorization.html', email=email, email_checker=False, email_exists=True)
            






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

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
