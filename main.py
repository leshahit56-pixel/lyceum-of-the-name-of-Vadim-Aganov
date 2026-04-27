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
from checker import first_first
from flask import jsonify
from data.lesson_first import First_lesson
from data.lesson_second import Second_lesson
from data.third_lesson import Third_lesson
from data.fourth_lesson import Fourth_lesson
from data.fifth_lesson import Fifth_lesson
from data.sixth_lesson import Sixth_lesson
from data.seventh_lesson import Seventh_lesson
from data.eighth_lesson import Eighth_lesson
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'f8874661e03139f344aa90692fd4d642b1e7a89b9b817bba')
app.permanent_session_lifetime = timedelta(days=30)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/logout_force')
def logout_force():
    session.clear()
    return redirect(url_for('register'))


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


def get_status_dict(lesson_id):
    email = session.get('email')
    if not email:
        return {i: 0 for i in range(1, 10)}

    db_session.global_init('db/blogs.db')
    ses = db_session.create_session()

    lesson_models = {1: First_lesson, 2: Second_lesson, 3: Third_lesson, 4: Fourth_lesson, 5: Fifth_lesson,
                     6: Sixth_lesson, 7: Seventh_lesson, 8: Eighth_lesson}
    model = lesson_models.get(lesson_id)

    status_dict = {}
    if model:
        solution = ses.query(model).filter(model.user_email == email).first()
        if solution:
            for num, col in {
                1: "exersize_one", 2: "exersize_two", 3: "exersize_three",
                4: "exersize_four", 5: "exersize_five", 6: "exersize_six",
                7: "exersize_seven", 8: "exersize_eight", 9: "exersize_nine"
            }.items():
                val = getattr(solution, col)
                status_dict[num] = val if val else 0
        else:
            for i in range(1, 10):
                status_dict[i] = 0
    else:
        for i in range(1, 10):
            status_dict[i] = 0

    ses.close()
    return status_dict


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


@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    email = session['email']

    db_session.global_init('db/blogs.db')
    ses = db_session.create_session()

    lesson_models = [Third_lesson, Fourth_lesson, Fifth_lesson, Sixth_lesson]
    total_tasks = 36
    solved = 0

    for model in lesson_models:
        row = ses.query(model).filter(model.user_email == email).first()
        if row:
            for i in range(1, 10):
                col = getattr(row,
                              f'exersize_{["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"][i - 1]}')
                if col == 2:
                    solved += 1

    total_score = user.scores if user.scores else 0

    all_users = ses.query(User).order_by(User.scores.desc()).all()
    rank = 1
    for u in all_users:
        if u.email == email:
            break
        rank += 1

    progress = round(solved / total_tasks * 100) if total_tasks > 0 else 0

    courses = [
        {
            "name": "Основы программирования на Python",
            "score": total_score,
            "solved": solved,
            "total": total_tasks,
            "progress": progress
        }
    ]

    ses.close()

    return render_template('profile.html', courses=courses, rank=rank)


@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return redirect(url_for('profile'))

    file = request.files['avatar']
    if file.filename == '':
        return redirect(url_for('profile'))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{get_current_user().id}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        db_session.global_init('db/blogs.db')
        ses = db_session.create_session()
        user = ses.query(User).filter(User.email == session['email']).first()
        user.avatar = filename
        ses.commit()
        ses.close()

    return redirect(url_for('profile'))


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
    email = session['email']
    db_session.global_init('db/blogs.db')
    ses = db_session.create_session()

    lesson_models = {1: First_lesson, 2: Second_lesson, 3: Third_lesson, 4: Fourth_lesson, 5: Fifth_lesson,
                     6: Sixth_lesson, 7: Seventh_lesson, 8: Eighth_lesson}
    lesson_progress = {}

    for lesson_id, model in lesson_models.items():
        row = ses.query(model).filter(model.user_email == email).first()
        solved = 0
        if row:
            for i in range(1, 10):
                col = getattr(row,
                              f'exersize_{["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"][i - 1]}')
                if col == 2:
                    solved += 1
        lesson_progress[lesson_id] = {"solved": solved, "total": 9, "percent": round(solved / 9 * 100)}

    ses.close()
    return render_template('course_python.html', lesson_progress=lesson_progress)


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
    progress = get_lesson_progress(1)
    return render_template('first_lesson.html', status_dict=get_status_dict(1),
                           solved=progress['solved'], total=progress['total'], percent=progress['percent'])


@app.route('/book_for_first_lessonn')
def book_for_first():
    return render_template('book_for_first_lessonn.html')


@app.route('/45')
def mine():
    return render_template('my_honest.html')


def get_tasks_for_lesson(lesson_id):
    if lesson_id == 1:
        return [{'id': 1, 'lesson_id': 1, 'title': 'Привет, мир!', 'points': 10, 'difficulty': 'easy',
                 'description': '<p>Напишите программу, которая выводит "Привет, мир!"</p>',
                 'starter_code': '# Напишите ваше решение здесь', 'status': None,
                 'tests': [
                     {'input': [], "expected": ['Hello, world!']}
                 ]}
                ]
    elif lesson_id == 2:
        return []
    elif lesson_id == 3:
        return [
            {'id': 1, 'lesson_id': 3, 'title': 'Секретный код', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Агент получил зашифрованное сообщение: три числа. Каждое число — это код символа. Помогите агенту прочитать послание.</p><p><strong>Формат ввода:</strong> Три целых числа, каждое с новой строки.</p><p><strong>Формат вывода:</strong> Строка из символов.</p><p><strong>Пример 1:</strong><br>Ввод:<br>72<br>105<br>33<br>Вывод:<br>Hi!</p><p><strong>Пример 2:</strong><br>Ввод:<br>80<br>121<br>116<br>Вывод:<br>Pyt</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['72', '105', '33'], "expected": ['Hi!']},
                 {"input": ['80', '121', '116'], "expected": ['Pyt']},
                 {"input": ['65', '66', '67'], "expected": ['ABC']},
             ]},

            {'id': 2, 'lesson_id': 3, 'title': 'Детский праздник', 'points': 10, 'difficulty': 'easy',
             'description': '<p>На день рождения к Пете пришли друзья. Мама купила мешок конфет и сказала разделить их поровну на всех, а остаток отдать имениннику.</p><p><strong>Формат ввода:</strong> Два целых числа, каждое с новой строки: сначала количество конфет, затем количество детей.</p><p><strong>Формат вывода:</strong> Два числа через пробел: сколько конфет получит каждый и сколько останется Пете.</p><p><strong>Пример 1:</strong><br>Ввод:<br>17<br>5<br>Вывод:<br>3 2</p><p><strong>Пример 2:</strong><br>Ввод:<br>42<br>10<br>Вывод:<br>4 2</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['17', '5'], "expected": ['3 2']},
                 {"input": ['42', '10'], "expected": ['4 2']},
                 {"input": ['10', '3'], "expected": ['3 1']},
             ]},

            {'id': 3, 'lesson_id': 3, 'title': 'Расстояние от дома', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Турист отмечал на карте свои перемещения: положительные числа — движение на север, отрицательные — на юг. В конце дня он записал одно итоговое число. Но ему нужно узнать, на каком расстоянии от дома (по модулю) он оказался.</p><p><strong>Формат ввода:</strong> Одно число (может быть целым или дробным).</p><p><strong>Формат вывода:</strong> Неотрицательное число — расстояние от нуля.</p><p><strong>Пример 1:</strong><br>Ввод:<br>-42<br>Вывод:<br>42.0</p><p><strong>Пример 2:</strong><br>Ввод:<br>-3.14<br>Вывод:<br>3.14</p><p><strong>Пример 3:</strong><br>Ввод:<br>15.7<br>Вывод:<br>15.7</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['-42'], "expected": ['42.0']},
                 {"input": ['-3.14'], "expected": ['3.14']},
                 {"input": ['15.7'], "expected": ['15.7']},
                 {"input": ['0'], "expected": ['0.0']},
             ]},

            {'id': 4, 'lesson_id': 3, 'title': 'Инженерный калькулятор', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Инженеру нужна программа, которая выполняет одну арифметическую операцию над двумя числами.</p><p><strong>Формат ввода:</strong> Три строки: первое число, знак операции (+, -, *, /, **, //, %), второе число. Числа могут быть целыми или дробными.</p><p><strong>Формат вывода:</strong> Результат вычисления.</p><p><strong>Пример 1:</strong><br>Ввод:<br>17<br>%<br>5<br>Вывод:<br>2.0</p><p><strong>Пример 2:</strong><br>Ввод:<br>2<br>**<br>10<br>Вывод:<br>1024.0</p><p><strong>Пример 3:</strong><br>Ввод:<br>15<br>/<br>4<br>Вывод:<br>3.75</p><p><strong>Пример 4:</strong><br>Ввод:<br>20<br>//<br>6<br>Вывод:<br>3.0</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['17', '%', '5'], "expected": ['2.0']},
                 {"input": ['2', '**', '10'], "expected": ['1024.0']},
                 {"input": ['15', '/', '4'], "expected": ['3.75']},
                 {"input": ['20', '//', '6'], "expected": ['3.0']},
             ]},

            {'id': 5, 'lesson_id': 3, 'title': 'Метеостанция', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Метеоролог записал показания термометра за неделю. Ему нужно определить самую высокую и самую низкую температуру, а также среднюю, округлённую до одного знака.</p><p><strong>Формат ввода:</strong> Шесть чисел, каждое с новой строки. Числа могут быть целыми или дробными.</p><p><strong>Формат вывода:</strong> Три строки: максимум и минимум через пробел, средняя (округлить до 1 знака), тип данных средней.</p><p><strong>Пример 1:</strong><br>Ввод:<br>-5.2<br>-3<br>0<br>2.5<br>-1<br>-7.3<br>Вывод:<br>2.5 -7.3<br>-2.3<br>&lt;class \'float\'&gt;</p><p><strong>Пример 2:</strong><br>Ввод:<br>12<br>15<br>10<br>14<br>13<br>16<br>Вывод:<br>16.0 10.0<br>13.3<br>&lt;class \'float\'&gt;</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['-5.2', '-3', '0', '2.5', '-1', '-7.3'],
                  "expected": ['2.5 -7.3', '-2.3', "<class 'float'>"]},
                 {"input": ['12', '15', '10', '14', '13', '16'], "expected": ['16.0 10.0', '13.3', "<class 'float'>"]},
                 {"input": ['1', '2', '3', '4', '5', '6'], "expected": ['6.0 1.0', '3.5', "<class 'float'>"]},
             ]},

            {'id': 6, 'lesson_id': 3, 'title': 'Анализ пароля', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Пользователь придумал пароль. Система проверяет его длину и выводит тип данных этой длины.</p><p><strong>Формат ввода:</strong> Строка — пароль.</p><p><strong>Формат вывода:</strong> Две строки: длина пароля, тип данных длины.</p><p><strong>Пример 1:</strong><br>Ввод:<br>qwerty123<br>Вывод:<br>9<br>&lt;class \'int\'&gt;</p><p><strong>Пример 2:</strong><br>Ввод:<br>abc<br>Вывод:<br>3<br>&lt;class \'int\'&gt;</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['qwerty123'], "expected": ['9', "<class 'int'>"]},
                 {"input": ['abc'], "expected": ['3', "<class 'int'>"]},
                 {"input": [''], "expected": ['0', "<class 'int'>"]},
             ]},

            {'id': 7, 'lesson_id': 3, 'title': 'Программист-археолог', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Археолог нашёл древний диск с данными. Чтобы прочитать символ, нужно знать его код в трёх системах счисления.</p><p><strong>Формат ввода:</strong> Один символ.</p><p><strong>Формат вывода:</strong> Три строки: код в десятичной, двоичной и шестнадцатеричной системе.</p><p><strong>Пример 1:</strong><br>Ввод:<br>Z<br>Вывод:<br>90<br>0b1011010<br>0x5a</p><p><strong>Пример 2:</strong><br>Ввод:<br>@<br>Вывод:<br>64<br>0b1000000<br>0x40</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['Z'], "expected": ['90', '0b1011010', '0x5a']},
                 {"input": ['@'], "expected": ['64', '0b1000000', '0x40']},
                 {"input": ['!'], "expected": ['33', '0b100001', '0x21']},
             ]},

            {'id': 8, 'lesson_id': 3, 'title': 'Олимпиадный приз', 'points': 12, 'difficulty': 'hard',
             'description': '<p>На олимпиаде три победителя набрали разное количество баллов. Главный приз получает участник с максимальным баллом. Утешительные призы получают двое оставшихся. Найдите сумму баллов утешительных призов и сколько процентов от максимума она составляет.</p><p><strong>Формат ввода:</strong> Три целых числа, каждое с новой строки.</p><p><strong>Формат вывода:</strong> Две строки: сумма двух меньших, процент от максимума (округлить до целого).</p><p><strong>Пример 1:</strong><br>Ввод:<br>5<br>12<br>9<br>Вывод:<br>14<br>117</p><p><strong>Пример 2:</strong><br>Ввод:<br>100<br>50<br>75<br>Вывод:<br>125<br>125</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['5', '12', '9'], "expected": ['14', '117']},
                 {"input": ['100', '50', '75'], "expected": ['125', '125']},
                 {"input": ['10', '20', '30'], "expected": ['30', '100']},
             ]},

            {'id': 9, 'lesson_id': 3, 'title': 'Вадим Маликович и ручные проверки', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Вадим Маликович получил от студента три числа: количество задач, количество строк кода и количество отступов. Он вычисляет индекс лени: (задачи * строки) // (отступы * 2). Если > 100 — "Я тебе не нейросеть...", 50-100 — "Ладно, проверю...", < 50 — "Идеально...".</p><p><strong>Формат ввода:</strong> Три целых числа, каждое с новой строки.</p><p><strong>Формат вывода:</strong> Индекс лени в восьмеричной системе, максимальное из трёх чисел, тип данных индекса, вердикт.</p><p><strong>Пример:</strong><br>Ввод:<br>10<br>200<br>2<br>Вывод:<br>0o764<br>200<br>&lt;class \'int\'&gt;<br>Я тебе не нейросеть, чтобы за тебя код писать.</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['10', '200', '2'],
                  "expected": ['0o764', '200', "<class 'int'>", 'Я тебе не нейросеть, чтобы за тебя код писать.']},
                 {"input": ['2', '5', '5'], "expected": ['0o1', '5', "<class 'int'>", 'Идеально, ставлю пятёрку.']},
                 {"input": ['8', '25', '2'],
                  "expected": ['0o62', '25', "<class 'int'>", 'Ладно, проверю, но в следующий раз — нейросеть.']},
             ]},
        ]
    elif lesson_id == 4:
        return [
            {'id': 1, 'lesson_id': 4, 'title': 'Робот-пылесос', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Робот-пылесос движется по комнате и сообщает, сколько метров он проехал. Выведите пройденное расстояние от 1 до N метров.</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> N строк вида "Проехал X метр(ов)".</p><p><strong>Пример:</strong><br>Ввод:<br>4<br>Вывод:<br>Проехал 1 метр(ов)<br>Проехал 2 метр(ов)<br>Проехал 3 метр(ов)<br>Проехал 4 метр(ов)</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['4'],
                  "expected": ['Проехал 1 метр(ов)', 'Проехал 2 метр(ов)', 'Проехал 3 метр(ов)', 'Проехал 4 метр(ов)']},
                 {"input": ['2'], "expected": ['Проехал 1 метр(ов)', 'Проехал 2 метр(ов)']},
                 {"input": ['1'], "expected": ['Проехал 1 метр(ов)']},
             ]},

            {'id': 2, 'lesson_id': 4, 'title': 'Космический запуск', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Центр управления полётами ведёт обратный отсчёт перед запуском ракеты. Выведите числа от N до 1, а затем слово "Поехали!".</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> N строк с числами, затем строка "Поехали!".</p><p><strong>Пример:</strong><br>Ввод:<br>3<br>Вывод:<br>3<br>2<br>1<br>Поехали!</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['3'], "expected": ['3', '2', '1', 'Поехали!']},
                 {"input": ['1'], "expected": ['1', 'Поехали!']},
                 {"input": ['5'], "expected": ['5', '4', '3', '2', '1', 'Поехали!']},
             ]},

            {'id': 3, 'lesson_id': 4, 'title': 'Зарядка', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Тренер просит сделать N отжиманий. После каждого десятого — "Есть!". Выведите номера отжиманий, помечая каждое десятое.</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> N строк с номерами. После каждого числа, кратного 10, через пробел слово "Есть!".</p><p><strong>Пример:</strong><br>Ввод:<br>25<br>Вывод:<br>1<br>2<br>...<br>10 Есть!<br>11<br>...<br>20 Есть!<br>21<br>22<br>23<br>24<br>25</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['10'], "expected": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10 Есть!']},
                 {"input": ['5'], "expected": ['1', '2', '3', '4', '5']},
                 {"input": ['20'],
                  "expected": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10 Есть!', '11', '12', '13', '14', '15',
                               '16', '17', '18', '19', '20 Есть!']},
             ]},

            {'id': 4, 'lesson_id': 4, 'title': 'Непослушный робот', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Робот принимает команды: "вперёд", "назад", "стоп". Команда "вперёд" увеличивает расстояние на 10, "назад" уменьшает на 10. Робот не может уйти в минус. Команда "стоп" завершает работу.</p><p><strong>Формат ввода:</strong> Несколько строк с командами, каждая с новой строки. Последняя команда — "стоп".</p><p><strong>Формат вывода:</strong> После каждой команды (кроме "стоп") — текущее положение робота. Если "назад" привела бы к минусу — "Робот упёрся в стену".</p><p><strong>Пример:</strong><br>Ввод:<br>вперёд<br>вперёд<br>назад<br>назад<br>назад<br>вперёд<br>стоп<br>Вывод:<br>10<br>20<br>10<br>0<br>Робот упёрся в стену<br>10</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['вперёд', 'вперёд', 'назад', 'назад', 'назад', 'вперёд', 'стоп'],
                  "expected": ['10', '20', '10', '0', 'Робот упёрся в стену', '10']},
                 {"input": ['вперёд', 'вперёд', 'стоп'], "expected": ['10', '20']},
                 {"input": ['назад', 'стоп'], "expected": ['Робот упёрся в стену']},
             ]},

            {'id': 5, 'lesson_id': 4, 'title': 'Капризный покупатель', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Кассир сканирует цены. Если товар дороже 1000 рублей — "Дорогой товар, проверьте цену!" и не прибавлять к сумме. Ввод 0 — конец покупок.</p><p><strong>Формат ввода:</strong> Целые числа (цены), каждое с новой строки. Последнее число — 0.</p><p><strong>Формат вывода:</strong> Для каждого пропущенного товара — "Дорогой товар, проверьте цену!". В конце — итоговая сумма.</p><p><strong>Пример:</strong><br>Ввод:<br>150<br>1200<br>300<br>2500<br>50<br>0<br>Вывод:<br>Дорогой товар, проверьте цену!<br>Дорогой товар, проверьте цену!<br>500</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['150', '1200', '300', '2500', '50', '0'],
                  "expected": ['Дорогой товар, проверьте цену!', 'Дорогой товар, проверьте цену!', '500']},
                 {"input": ['100', '200', '0'], "expected": ['300']},
                 {"input": ['2000', '0'], "expected": ['Дорогой товар, проверьте цену!', '0']},
             ]},

            {'id': 6, 'lesson_id': 4, 'title': 'Детектор лжи', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Следователь допрашивает подозреваемого. Ответы: "да", "нет", "стоп". Если три "нет" подряд — "Ложь!". Если "стоп" раньше — "Допрос окончен".</p><p><strong>Формат ввода:</strong> Несколько строк с ответами. Последний ответ — "стоп" или три "нет" подряд.</p><p><strong>Формат вывода:</strong> Если три "нет" подряд — "Ложь!". Если "стоп" раньше — "Допрос окончен".</p><p><strong>Пример 1:</strong><br>Ввод:<br>да<br>нет<br>нет<br>нет<br>Вывод:<br>Ложь!</p><p><strong>Пример 2:</strong><br>Ввод:<br>да<br>нет<br>да<br>нет<br>стоп<br>Вывод:<br>Допрос окончен</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['да', 'нет', 'нет', 'нет'], "expected": ['Ложь!']},
                 {"input": ['да', 'нет', 'да', 'нет', 'стоп'], "expected": ['Допрос окончен']},
                 {"input": ['нет', 'нет', 'нет'], "expected": ['Ложь!']},
             ]},

            {'id': 7, 'lesson_id': 4, 'title': 'Шифровальщик-2', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Агент передаёт сообщения, состоящие из отдельных символов. Каждый символ вводится с новой строки. Пустая строка — конец сообщения. Найдите символ с наибольшим кодом и количество символов.</p><p><strong>Формат ввода:</strong> Несколько строк с одиночными символами. Пустая строка — конец.</p><p><strong>Формат вывода:</strong> Две строки: символ с наибольшим кодом, общее количество символов.</p><p><strong>Пример:</strong><br>Ввод:<br>A<br>z<br>5<br>m<br><br>Вывод:<br>z<br>4</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['A', 'z', '5', 'm', ''], "expected": ['z', '4']},
                 {"input": ['a', 'b', 'c', ''], "expected": ['c', '3']},
                 {"input": ['X', ''], "expected": ['X', '1']},
             ]},

            {'id': 8, 'lesson_id': 4, 'title': 'Гадалка', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Гадалка записывает возраст посетителей. Ввод 0 — конец. Найдите самого молодого, самого старого и есть ли ровесники.</p><p><strong>Формат ввода:</strong> Целые положительные числа (возраст), каждое с новой строки. Последнее — 0.</p><p><strong>Формат вывода:</strong> Три строки: "Самый молодой: X", "Самый старый: Y", "Есть ровесники" или "Нет ровесников".</p><p><strong>Пример 1:</strong><br>Ввод:<br>25<br>42<br>25<br>18<br>0<br>Вывод:<br>Самый молодой: 18<br>Самый старый: 42<br>Есть ровесники</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['25', '42', '25', '18', '0'],
                  "expected": ['Самый молодой: 18', 'Самый старый: 42', 'Есть ровесники']},
                 {"input": ['30', '15', '22', '0'],
                  "expected": ['Самый молодой: 15', 'Самый старый: 30', 'Нет ровесников']},
                 {"input": ['5', '5', '0'], "expected": ['Самый молодой: 5', 'Самый старый: 5', 'Есть ровесники']},
             ]},

            {'id': 9, 'lesson_id': 4, 'title': 'Вадим Маликович и бесконечный цикл', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Вадим Маликович проверяет, сколько раз студенты готовы нажимать Enter. Секретный код выхода: 120. Программа считает попытки, максимум, минимум и был ли введён 0.</p><p><strong>Формат ввода:</strong> Целые числа, каждое с новой строки. Число 120 — сигнал остановки.</p><p><strong>Формат вывода:</strong> Четыре строки: количество попыток (не считая 120), максимум, минимум, "Обнаружена капитуляция" или "Без капитуляции". Затем "Вадим Маликович жмёт 120. Легко. Break — ваш друг."</p><p><strong>Пример:</strong><br>Ввод:<br>15<br>42<br>8<br>120<br>Вывод:<br>Всего попыток: 3<br>Максимум: 42<br>Минимум: 8<br>Без капитуляции.<br>Вадим Маликович жмёт 120. Легко. Break — ваш друг.</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['15', '42', '8', '120'],
                  "expected": ['Всего попыток: 3', 'Максимум: 42', 'Минимум: 8', 'Без капитуляции.',
                               'Вадим Маликович жмёт 120. Легко. Break — ваш друг.']},
                 {"input": ['0', '120'],
                  "expected": ['Всего попыток: 1', 'Максимум: 0', 'Минимум: 0', 'Обнаружена капитуляция.',
                               'Вадим Маликович жмёт 120. Легко. Break — ваш друг.']},
                 {"input": ['100', '120'],
                  "expected": ['Всего попыток: 1', 'Максимум: 100', 'Минимум: 100', 'Без капитуляции.',
                               'Вадим Маликович жмёт 120. Легко. Break — ваш друг.']},
             ]},
        ]
    elif lesson_id == 5:
        return [
            {'id': 1, 'lesson_id': 5, 'title': 'Гласные и согласные', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Робот проверяет текст и считает, сколько в слове гласных букв. Гласные: а, е, ё, и, о, у, ы, э, ю, я.</p><p><strong>Формат ввода:</strong> Одна строка — слово.</p><p><strong>Формат вывода:</strong> Одно число — количество гласных.</p><p><strong>Пример:</strong><br>Ввод:<br>привет<br>Вывод:<br>2</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['привет'], "expected": ['2']},
                 {"input": ['ааа'], "expected": ['3']},
                 {"input": ['ббб'], "expected": ['0']},
             ]},

            {'id': 2, 'lesson_id': 5, 'title': 'Эхо', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Робот повторяет каждую букву слова дважды.</p><p><strong>Формат ввода:</strong> Одна строка — слово.</p><p><strong>Формат вывода:</strong> Строка, где каждая буква повторена дважды.</p><p><strong>Пример:</strong><br>Ввод:<br>привет<br>Вывод:<br>ппррииввеетт</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['привет'], "expected": ['ппррииввеетт']},
                 {"input": ['да'], "expected": ['ддаа']},
                 {"input": ['a'], "expected": ['aa']},
             ]},

            {'id': 3, 'lesson_id': 5, 'title': 'Скрытое послание', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Шпион зашифровал сообщение: каждую вторую букву нужно пропустить, а остальные вывести подряд (берём 0-ю, 2-ю, 4-ю...).</p><p><strong>Формат ввода:</strong> Одна строка.</p><p><strong>Формат вывода:</strong> Строка из символов через один.</p><p><strong>Пример:</strong><br>Ввод:<br>привет<br>Вывод:<br>пие</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['привет'], "expected": ['пие']},
                 {"input": ['abcdef'], "expected": ['ace']},
                 {"input": ['a'], "expected": ['a']},
             ]},

            {'id': 4, 'lesson_id': 5, 'title': 'Пирамида из чисел', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Выведите пирамиду из чисел высотой N. Каждая строка состоит из чисел от 1 до номера строки и обратно.</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> N строк, образующих числовую пирамиду.</p><p><strong>Пример:</strong><br>Ввод:<br>4<br>Вывод:<br>   1<br>  1 2 1<br> 1 2 3 2 1<br>1 2 3 4 3 2 1</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['4'], "expected": ['   1', '  1 2 1', ' 1 2 3 2 1', '1 2 3 4 3 2 1']},
                 {"input": ['2'], "expected": [' 1', '1 2 1']},
                 {"input": ['1'], "expected": ['1']},
             ]},

            {'id': 5, 'lesson_id': 5, 'title': 'Сумма нечётных', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Посчитайте сумму всех нечётных чисел от 1 до N.</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> Одно число — сумма нечётных.</p><p><strong>Пример:</strong><br>Ввод:<br>5<br>Вывод:<br>9</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['5'], "expected": ['9']},
                 {"input": ['1'], "expected": ['1']},
                 {"input": ['10'], "expected": ['25']},
             ]},

            {'id': 6, 'lesson_id': 5, 'title': 'Таблица умножения', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Выведите таблицу умножения от 1 до N. Числа в строке разделяйте пробелом.</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> Таблица N×N.</p><p><strong>Пример:</strong><br>Ввод:<br>4<br>Вывод:<br>1 2 3 4<br>2 4 6 8<br>3 6 9 12<br>4 8 12 16</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['4'], "expected": ['1 2 3 4', '2 4 6 8', '3 6 9 12', '4 8 12 16']},
                 {"input": ['2'], "expected": ['1 2', '2 4']},
                 {"input": ['1'], "expected": ['1']},
             ]},

            {'id': 7, 'lesson_id': 5, 'title': 'Диагонали квадрата', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Нарисуйте квадрат N×N, где на главной и побочной диагоналях — #, а в остальных местах — . (точка). Символы разделены пробелом.</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> Квадрат N×N с диагоналями.</p><p><strong>Пример:</strong><br>Ввод:<br>5<br>Вывод:<br># . . . #<br>. # . # .<br>. . # . .<br>. # . # .<br># . . . #</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['5'], "expected": ['# . . . #', '. # . # .', '. . # . .', '. # . # .', '# . . . #']},
                 {"input": ['3'], "expected": ['# . #', '. # .', '# . #']},
                 {"input": ['1'], "expected": ['#']},
             ]},

            {'id': 8, 'lesson_id': 5, 'title': 'Простые числа', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Выведите все простые числа от 2 до N через пробел. Простое число — это число, которое делится только на 1 и на само себя.</p><p><strong>Формат ввода:</strong> Одно целое число N.</p><p><strong>Формат вывода:</strong> Простые числа через пробел.</p><p><strong>Пример 1:</strong><br>Ввод:<br>20<br>Вывод:<br>2 3 5 7 11 13 17 19</p><p><strong>Пример 2:</strong><br>Ввод:<br>10<br>Вывод:<br>2 3 5 7</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['20'], "expected": ['2 3 5 7 11 13 17 19']},
                 {"input": ['10'], "expected": ['2 3 5 7']},
                 {"input": ['2'], "expected": ['2']},
             ]},

            {'id': 9, 'lesson_id': 5, 'title': 'Вадим Маликович и восстание принтеров', 'points': 12,
             'difficulty': 'hard',
             'description': '<p>Вадим Маликович обнаружил, что все 5 принтеров взбесились. Он проверяет по 4 отчёта от каждого. Если встречает "принтер" — выключает этот принтер. Если "бесконечный" — пропускает отчёт. Блоки разделяются строкой NEXT_PRINTER.</p><p><strong>Формат ввода:</strong> 5 блоков, каждый блок — отчёты одного принтера. Блоки разделяются строкой NEXT_PRINTER.</p><p><strong>Формат вывода:</strong> Для каждого выключенного принтера — "Принтер №X выключен.". Затем итоги: всего прочитано, выключено принтеров, лучший принтер, и фраза "И да, я жму 120. Легко."</p><p><strong>Пример:</strong><br>Ввод:<br>Отчёт 1.1<br>бесконечный<br>Отчёт 1.2<br>Отчёт 1.3<br>NEXT_PRINTER<br>Отчёт 2.1<br>принтер<br>Отчёт 2.2<br>Отчёт 2.3<br>NEXT_PRINTER<br>Отчёт 3.1<br>Отчёт 3.2<br>Отчёт 3.3<br>Отчёт 3.4<br>NEXT_PRINTER<br>Отчёт 4.1<br>бесконечный<br>отчёт 4.2<br>бесконечный<br>NEXT_PRINTER<br>Отчёт 5.1<br>Отчёт 5.2<br>принтер<br>Отчёт 5.3<br>Вывод:<br>Принтер №2 выключен.<br>Принтер №5 выключен.<br>Всего прочитано отчётов: 12<br>Выключено принтеров: 2<br>Лучший принтер: №3<br>И да, я жму 120. Легко.</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": [
                     'Отчёт 1.1', 'бесконечный', 'Отчёт 1.2', 'Отчёт 1.3',
                     'NEXT_PRINTER',
                     'Отчёт 2.1', 'принтер', 'Отчёт 2.2', 'Отчёт 2.3',
                     'NEXT_PRINTER',
                     'Отчёт 3.1', 'Отчёт 3.2', 'Отчёт 3.3', 'Отчёт 3.4',
                     'NEXT_PRINTER',
                     'Отчёт 4.1', 'бесконечный', 'отчёт 4.2', 'бесконечный',
                     'NEXT_PRINTER',
                     'Отчёт 5.1', 'Отчёт 5.2', 'принтер', 'Отчёт 5.3'
                 ],
                     "expected": [
                         'Принтер №2 выключен.',
                         'Принтер №5 выключен.',
                         'Всего прочитано отчётов: 12',
                         'Выключено принтеров: 2',
                         'Лучший принтер: №3',
                         'И да, я жму 120. Легко.'
                     ]},
                 {"input": [
                     'Отчёт 1.1', 'Отчёт 1.2', 'Отчёт 1.3', 'Отчёт 1.4',
                     'NEXT_PRINTER',
                     'Отчёт 2.1', 'Отчёт 2.2', 'Отчёт 2.3', 'Отчёт 2.4',
                     'NEXT_PRINTER',
                     'Отчёт 3.1', 'Отчёт 3.2', 'Отчёт 3.3', 'Отчёт 3.4',
                     'NEXT_PRINTER',
                     'Отчёт 4.1', 'Отчёт 4.2', 'Отчёт 4.3', 'Отчёт 4.4',
                     'NEXT_PRINTER',
                     'Отчёт 5.1', 'Отчёт 5.2', 'Отчёт 5.3', 'Отчёт 5.4'
                 ],
                     "expected": [
                         'Всего прочитано отчётов: 20',
                         'Выключено принтеров: 0',
                         'Лучший принтер: №1',
                         'И да, я жму 120. Легко.'
                     ]},
                 {"input": [
                     'принтер', 'бесконечный', 'Отчёт 1.2', 'Отчёт 1.3',
                     'NEXT_PRINTER',
                     'принтер', 'Отчёт 2.2', 'бесконечный', 'Отчёт 2.3',
                     'NEXT_PRINTER',
                     'принтер', 'Отчёт 3.2', 'Отчёт 3.3', 'бесконечный',
                     'NEXT_PRINTER',
                     'принтер', 'бесконечный', 'Отчёт 4.2', 'Отчёт 4.3',
                     'NEXT_PRINTER',
                     'принтер', 'Отчёт 5.2', 'бесконечный', 'Отчёт 5.3'
                 ],
                     "expected": [
                         'Принтер №1 выключен.',
                         'Принтер №2 выключен.',
                         'Принтер №3 выключен.',
                         'Принтер №4 выключен.',
                         'Принтер №5 выключен.',
                         'Всего прочитано отчётов: 0',
                         'Выключено принтеров: 5',
                         'Лучший принтер: нет',
                         'И да, я жму 120. Легко.'
                     ]},
             ]},
        ]
    elif lesson_id == 6:
        return [
            {'id': 1, 'lesson_id': 6, 'title': 'Шпионский пароль', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Шпион передаёт пароль, который состоит из первого и последнего символа кодовой фразы.</p><p><strong>Формат ввода:</strong> Одна строка — кодовая фраза.</p><p><strong>Формат вывода:</strong> Два символа подряд — пароль.</p><p><strong>Пример:</strong><br>Ввод:<br>пингвин<br>Вывод:<br>пн</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['пингвин'], "expected": ['пн']},
                 {"input": ['привет'], "expected": ['пт']},
                 {"input": ['а'], "expected": ['аа']},
             ]},

            {'id': 2, 'lesson_id': 6, 'title': 'Ленивый попугай', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Попугай Кеша ленится учить новые слова и просто повторяет то, что сказал хозяин, но 4 раза подряд.</p><p><strong>Формат ввода:</strong> Одна строка — слово.</p><p><strong>Формат вывода:</strong> Строка, повторённая 4 раза.</p><p><strong>Пример:</strong><br>Ввод:<br>Кеша<br>Вывод:<br>КешаКешаКешаКеша</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['Кеша'], "expected": ['КешаКешаКешаКеша']},
                 {"input": ['да'], "expected": ['дададада']},
                 {"input": ['a'], "expected": ['aaaa']},
             ]},

            {'id': 3, 'lesson_id': 6, 'title': 'Разделитель тысяч', 'points': 10, 'difficulty': 'easy',
             'description': '<p>Напишите программу, которая принимает строку из цифр и вставляет пробелы каждые 3 цифры справа налево.</p><p><strong>Формат ввода:</strong> Одна строка из цифр.</p><p><strong>Формат вывода:</strong> Строка с пробелами между тройками цифр.</p><p><strong>Пример 1:</strong><br>Ввод:<br>1234567890<br>Вывод:<br>1 234 567 890</p><p><strong>Пример 2:</strong><br>Ввод:<br>12345<br>Вывод:<br>12 345</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['1234567890'], "expected": ['1 234 567 890']},
                 {"input": ['12345'], "expected": ['12 345']},
                 {"input": ['123'], "expected": ['123']},
             ]},

            {'id': 4, 'lesson_id': 6, 'title': 'Символы в обратном порядке через два', 'points': 11,
             'difficulty': 'medium',
             'description': '<p>Выведите символы строки в обратном порядке, пропуская каждые два символа (берёте каждый третий с конца).</p><p><strong>Формат ввода:</strong> Одна строка.</p><p><strong>Формат вывода:</strong> Строка из символов.</p><p><strong>Пример:</strong><br>Ввод:<br>abcdefghijk<br>Вывод:<br>kheb</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['abcdefghijk'], "expected": ['kheb']},
                 {"input": ['abcdef'], "expected": ['fc']},
                 {"input": ['abc'], "expected": ['c']},
             ]},

            {'id': 5, 'lesson_id': 6, 'title': 'Сравнение половин', 'points': 11, 'difficulty': 'medium',
             'description': '<p>Разделите строку пополам (если нечётная длина — середина не учитывается) и сравните левую половину с перевёрнутой правой. Если равны — "Симметричные", иначе — "Несимметричные".</p><p><strong>Формат ввода:</strong> Одна строка.</p><p><strong>Формат вывода:</strong> "Симметричные" или "Несимметричные".</p><p><strong>Пример 1:</strong><br>Ввод:<br>абвгвба<br>Вывод:<br>Симметричные</p><p><strong>Пример 2:</strong><br>Ввод:<br>привет<br>Вывод:<br>Несимметричные</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['абвгвба'], "expected": ['Симметричные']},
                 {"input": ['привет'], "expected": ['Несимметричные']},
                 {"input": ['abcba'], "expected": ['Симметричные']},
             ]},

            {'id': 6, 'lesson_id': 6, 'title': 'Самая длинная подстрока без повторений', 'points': 11,
             'difficulty': 'medium',
             'description': '<p>Найдите длину самой длинной подстроки, в которой все символы уникальны.</p><p><strong>Формат ввода:</strong> Одна строка.</p><p><strong>Формат вывода:</strong> Одно число — длина подстроки.</p><p><strong>Пример 1:</strong><br>Ввод:<br>abcabcbb<br>Вывод:<br>3</p><p><strong>Пример 2:</strong><br>Ввод:<br>bbbbb<br>Вывод:<br>1</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['abcabcbb'], "expected": ['3']},
                 {"input": ['bbbbb'], "expected": ['1']},
                 {"input": ['pwwkew'], "expected": ['3']},
             ]},

            {'id': 7, 'lesson_id': 6, 'title': 'Римские цифры в арабские', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Переведите римское число (до 3999) в арабское.</p><p><strong>Формат ввода:</strong> Одна строка — римское число.</p><p><strong>Формат вывода:</strong> Одно целое число.</p><p><strong>Пример 1:</strong><br>Ввод:<br>XIV<br>Вывод:<br>14</p><p><strong>Пример 2:</strong><br>Ввод:<br>MCMXCIV<br>Вывод:<br>1994</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['XIV'], "expected": ['14']},
                 {"input": ['MCMXCIV'], "expected": ['1994']},
                 {"input": ['III'], "expected": ['3']},
             ]},

            {'id': 8, 'lesson_id': 6, 'title': 'Самое длинное слово', 'points': 12, 'difficulty': 'hard',
             'description': '<p>Найдите самое длинное слово в строке. Слова разделены пробелами. Если слов несколько — выведите первое по порядку.</p><p><strong>Формат ввода:</strong> Одна строка.</p><p><strong>Формат вывода:</strong> Самое длинное слово.</p><p><strong>Пример 1:</strong><br>Ввод:<br>привет мир программирование<br>Вывод:<br>программирование</p><p><strong>Пример 2:</strong><br>Ввод:<br>a bb ccc dddd<br>Вывод:<br>dddd</p><p><strong>Пример 3:</strong><br>Ввод:<br>один два три<br>Вывод:<br>один</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['привет мир программирование'], "expected": ['программирование']},
                 {"input": ['a bb ccc dddd'], "expected": ['dddd']},
                 {"input": ['один два три'], "expected": ['один']},
             ]},

            {'id': 9, 'lesson_id': 6, 'title': 'Вадим Маликович и шифр подмазавшегося студента', 'points': 12,
             'difficulty': 'hard',
             'description': '<p>Студент зашифровал комплимент. Каждую цифру на чётном индексе заменил на текст (0→ноль, 1→один, ... 9→девять). Если есть "120" — "Вадим Маликович жмёт 120! Легко!". Если "принтер" — "Принтер? Опять?!". Иначе расшифрованная строка.</p><p><strong>Формат ввода:</strong> Одна строка.</p><p><strong>Формат вывода:</strong> Расшифрованная строка или сообщение.</p><p><strong>Пример 1:</strong><br>Ввод:<br>Я поднял 1два0 кг<br>Вывод:<br>Вадим Маликович жмёт 120! Легко! Подмазаться не вышло.</p><p><strong>Пример 2:</strong><br>Ввод:<br>У меня 2 яблока и 3 груши<br>Вывод:<br>У меня 2 яблока и три груши</p><p><strong>Пример 3:</strong><br>Ввод:<br>Код с принтер и 2 три<br>Вывод:<br>Принтер? Опять?! Всё, хватит.</p>',
             'starter_code': '', 'status': None,
             'tests': [
                 {"input": ['Я поднял 1два0 кг'],
                  "expected": ['Вадим Маликович жмёт 120! Легко! Подмазаться не вышло.']},
                 {"input": ['У меня 2 яблока и 3 груши'], "expected": ['У меня 2 яблока и три груши']},
                 {"input": ['Код с принтер и 2 три'], "expected": ['Принтер? Опять?! Всё, хватит.']},
             ]},
        ]
    elif lesson_id == 7:
        return []
    elif lesson_id == 8:
        return []
    return []


@app.route('/course/python/lesson/<int:lesson_id>/task/<int:task_order>')
@login_required
def task(lesson_id, task_order):
    db_session.global_init('db/blogs.db')
    ses = db_session.create_session()
    email = session['email']
    tasks = get_tasks_for_lesson(lesson_id)
    if not tasks:
        return f"<h2>Урок {lesson_id}</h2><p>Задания ещё не добавлены</p>"
    task = tasks[task_order - 1]

    if lesson_id == 1:
        less = First_lesson
    elif lesson_id == 2:
        less = Second_lesson
    elif lesson_id == 3:
        less = Third_lesson
    elif lesson_id == 4:
        less = Fourth_lesson
    elif lesson_id == 5:
        less = Fifth_lesson
    elif lesson_id == 6:
        less = Sixth_lesson
    elif lesson_id == 7:
        less = Seventh_lesson
    elif lesson_id == 8:
        less = Eighth_lesson

    solution = ses.query(less).filter(less.user_email == email).first()

    task_columns = {
        1: "exersize_one_solution", 2: "exersize_two_solution", 3: "exersize_three_solution",
        4: "exersize_four_solution", 5: "exersize_five_solution", 6: "exersize_six_solution",
        7: "exersize_seven_solution", 8: "exersize_eight_solution", 9: "exersize_nine_solution"
    }
    if solution:
        column_name = task_columns.get(task_order)
        solution_in_db = getattr(solution, column_name)
        if solution_in_db:
            task['starter_code'] = solution_in_db

    if solution:
        status_col = {
            1: "exersize_one", 2: "exersize_two", 3: "exersize_three",
            4: "exersize_four", 5: "exersize_five", 6: "exersize_six",
            7: "exersize_seven", 8: "exersize_eight", 9: "exersize_nine"
        }.get(task_order)
        val = getattr(solution, status_col)
        if val == 2:
            task['status'] = 'solved'
        elif val == 1:
            task['status'] = 'failed'

    status_dict = {}
    if solution:
        for num, col in {
            1: "exersize_one", 2: "exersize_two", 3: "exersize_three",
            4: "exersize_four", 5: "exersize_five", 6: "exersize_six",
            7: "exersize_seven", 8: "exersize_eight", 9: "exersize_nine"
        }.items():
            val = getattr(solution, col)
            status_dict[num] = val if val else 0
    else:
        for i in range(1, 10):
            status_dict[i] = 0

    lesson_urls = {
        1: 'hello_world',
        3: 'lesson_operators',
        4: 'lesson_while',
        5: 'lesson_for',
        6: 'lesson_strings',
    }
    back_url = url_for(lesson_urls.get(lesson_id, 'hello_world'))

    return render_template('task.html', task=task, lesson_id=lesson_id, status_dict=status_dict, back_url=back_url)


def get_lesson_progress(lesson_id):
    status_dict = get_status_dict(lesson_id)
    solved = sum(1 for v in status_dict.values() if v == 2)
    total = 9
    percent = round(solved / total * 100) if total > 0 else 0
    return {"solved": solved, "total": total, "percent": percent}


@app.route('/course/python/operators')
@login_required
def lesson_operators():
    progress = get_lesson_progress(3)
    return render_template('lesson_operators.html', status_dict=get_status_dict(3),
                           solved=progress['solved'], total=progress['total'], percent=progress['percent'])


@app.route('/course/python/while')
@login_required
def lesson_while():
    progress = get_lesson_progress(4)
    return render_template('lesson_while.html', status_dict=get_status_dict(4),
                           solved=progress['solved'], total=progress['total'], percent=progress['percent'])


@app.route('/course/python/for')
@login_required
def lesson_for():
    progress = get_lesson_progress(5)
    return render_template('lesson_for.html', status_dict=get_status_dict(5),
                           solved=progress['solved'], total=progress['total'], percent=progress['percent'])


@app.route('/course/python/strings')
@login_required
def lesson_strings():
    progress = get_lesson_progress(6)
    return render_template('lesson_strings.html', status_dict=get_status_dict(6),
                           solved=progress['solved'], total=progress['total'], percent=progress['percent'])


@app.route('/book_for_operators')
def book_for_operators():
    return render_template('book_for_operators.html')


@app.route('/book_for_while')
def book_for_while():
    return render_template('book_for_while.html')


@app.route('/book_for_for')
def book_for_for():
    return render_template('book_for_for.html')


@app.route('/book_for_strings')
def book_for_strings():
    return render_template('book_for_strings.html')


def add_verdict(lesson_id, exersize_id, code, verdict, email, points):
    db_session.global_init('db/blogs.db')
    session = db_session.create_session()

    task_columns = {
        1: "exersize_one", 2: "exersize_two", 3: "exersize_three",
        4: "exersize_four", 5: "exersize_five", 6: "exersize_six",
        7: "exersize_seven", 8: "exersize_eight", 9: "exersize_nine"
    }

    if lesson_id == 1:
        new_verdict = First_lesson

    elif lesson_id == 2:
        new_verdict = Second_lesson

    elif lesson_id == 3:
        new_verdict = Third_lesson

    elif lesson_id == 4:
        new_verdict = Fourth_lesson

    elif lesson_id == 5:
        new_verdict = Fifth_lesson

    elif lesson_id == 6:
        new_verdict = Sixth_lesson

    elif lesson_id == 7:
        new_verdict = Seventh_lesson

    elif lesson_id == 8:
        new_verdict = Eighth_lesson

    user = session.query(new_verdict).filter(new_verdict.user_email == email).first()

    column_name = task_columns.get(exersize_id)

    if not user:
        user = new_verdict(user_email=email)
        session.add(user)
        if verdict == 2:
            user_in_main_db_scores = session.query(User).filter(User.email == email).first()
            scores = user_in_main_db_scores.scores
            new_scores = scores + points
            user_in_main_db_scores.scores = new_scores

    else:
        verdict_in_db = getattr(user, column_name)
        if verdict_in_db != 2 and verdict == 2:
            user_in_main_db_scores = session.query(User).filter(User.email == email).first()
            scores = user_in_main_db_scores.scores
            new_scores = scores + points
            user_in_main_db_scores.scores = new_scores
        else:
            verdict = 2

    if exersize_id == 1:
        user.exersize_one = verdict
        user.exersize_one_solution = code
    elif exersize_id == 2:
        user.exersize_two = verdict
        user.exersize_two_solution = code
    elif exersize_id == 3:
        user.exersize_three = verdict
        user.exersize_three_solution = code
    elif exersize_id == 4:
        user.exersize_four = verdict
        user.exersize_four_solution = code
    elif exersize_id == 5:
        user.exersize_five = verdict
        user.exersize_five_solution = code
    elif exersize_id == 6:
        user.exersize_six = verdict
        user.exersize_six_solution = code
    elif exersize_id == 7:
        user.exersize_seven = verdict
        user.exersize_seven_solution = code
    elif exersize_id == 8:
        user.exersize_eight = verdict
        user.exersize_eight_solution = code
    elif exersize_id == 9:
        user.exersize_nine = verdict
        user.exersize_nine_solution = code

    try:
        session.commit()
        return 'Задача успешно сохранена'
    except Exception:
        return 'При загрузке задачи на сервер произошла ошибка'
    finally:
        session.close()


@app.route('/api/check_solution', methods=['POST'])
@login_required
def check_solution():
    data = request.get_json()
    code = data.get('code')
    lesson_id = int(data.get('lesson_id'))
    task_order = int(data.get('task_order'))

    tasks = get_tasks_for_lesson(lesson_id)
    task = tasks[task_order - 1]

    points = task['points']

    result = first_first(code, task['tests'])

    email = session['email']

    if result['verdict'] == 'ok':
        save_decision = add_verdict(lesson_id, task_order, code, 2, email, points)
        if save_decision != 'Задача успешно сохранена':
            result[
                'verdict'] = 'ошибка при отправке задачи на сервер. Попробуйте снова или позвоните в поддержку по номеру: +7 (910) 456-94-61'
    else:
        save_decision = add_verdict(lesson_id, task_order, code, 1, email, points)
        if save_decision != 'Задача успешно сохранена':
            result[
                'verdict'] = 'ошибка при отправке задачи на сервер. Попробуйте снова или позвоните в поддержку по номеру: +7 (910) 456-94-61'

    return jsonify(result)


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
