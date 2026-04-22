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


@app.route('/45')
def mine():
    return render_template('my_honest.html')


def get_tasks_for_lesson(lesson_id):
    if lesson_id == 1:
        return [{'id': 1, 'lesson_id': 1, 'title': 'Привет, мир!', 'points': 10, 'difficulty': 'easy',
                 'description': '<p>Напишите программу, которая выводит "Привет, мир!"</p>',
                 'starter_code': '# Напишите ваше решение здесь', 'status': None}]
    elif lesson_id == 2:
        return []
    elif lesson_id == 3:
        return [
            {'id': 1, 'lesson_id': 3, 'title': 'Секретный код', 'points': 10, 'difficulty': 'easy',
             'description': '''
                    <p>Агент получил зашифрованное сообщение: три числа. Каждое число — это код символа. Помогите агенту прочитать послание.</p>
                    <p><strong>Формат ввода:</strong> Три целых числа, каждое с новой строки.</p>
                    <p><strong>Формат вывода:</strong> Строка из символов.</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод:
        72
        105
        33
        Вывод:
        Hi!</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод:
        80
        121
        116
        Вывод:
        Pyt</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте функцию <code>chr()</code> для преобразования кода в символ.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 2, 'lesson_id': 3, 'title': 'Детский праздник', 'points': 10, 'difficulty': 'easy',
             'description': '''
                    <p>На день рождения к Пете пришли друзья. Мама купила мешок конфет и сказала разделить их поровну на всех, а остаток отдать имениннику.</p>
                    <p><strong>Формат ввода:</strong> Два целых числа через пробел: количество конфет и количество детей (включая Петю).</p>
                    <p><strong>Формат вывода:</strong> Два числа через пробел: сколько конфет получит каждый и сколько останется Пете.</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод: 17 5
        Вывод: 3 2</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод: 42 10
        Вывод: 4 2</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте функцию <code>divmod()</code>.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 3, 'lesson_id': 3, 'title': 'Расстояние от дома', 'points': 10, 'difficulty': 'easy',
             'description': '''
                    <p>Турист отмечал на карте свои перемещения: положительные числа — движение на север, отрицательные — на юг. В конце дня он записал одно итоговое число. Узнайте, на каком расстоянии от дома (по модулю) он оказался.</p>
                    <p><strong>Формат ввода:</strong> Одно число (может быть отрицательным или дробным).</p>
                    <p><strong>Формат вывода:</strong> Неотрицательное число — расстояние от нуля.</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод: -42
        Вывод: 42</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод: -3.14
        Вывод: 3.14</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте функцию <code>abs()</code>.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 4, 'lesson_id': 3, 'title': 'Инженерный калькулятор', 'points': 11, 'difficulty': 'medium',
             'description': '''
                    <p>Инженеру нужна программа, которая выполняет одну арифметическую операцию над двумя числами.</p>
                    <p><strong>Формат ввода:</strong> Три строки: первое число, знак операции (+, -, *, /, **, //, %), второе число.</p>
                    <p><strong>Формат вывода:</strong> Результат вычисления.</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод:
        17
        %
        5
        Вывод: 2</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод:
        2
        **
        10
        Вывод: 1024</code></pre>
                    <p><strong>Пример 3:</strong></p>
                    <pre><code>Ввод:
        15
        /
        4
        Вывод: 3.75</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте <code>if/elif</code> для проверки знака операции.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 5, 'lesson_id': 3, 'title': 'Метеостанция', 'points': 11, 'difficulty': 'medium',
             'description': '''
                    <p>Метеоролог записал показания термометра за неделю. Определите самую высокую и самую низкую температуру, а также среднюю, округлённую до одного знака.</p>
                    <p><strong>Формат ввода:</strong> Шесть чисел через пробел.</p>
                    <p><strong>Формат вывода:</strong></p>
                    <p>1. Максимальная и минимальная температура через пробел.</p>
                    <p>2. Средняя температура (округлить до 1 знака).</p>
                    <p>3. Тип данных средней температуры.</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод: -5.2 -3 0 2.5 -1 -7.3
        Вывод:
        2.5 -7.3
        -2.3
        &lt;class 'float'&gt;</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод: 12 15 10 14 13 16
        Вывод:
        16 10
        13.3
        &lt;class 'float'&gt;</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте <code>max()</code>, <code>min()</code>, <code>sum()</code>, <code>len()</code>, <code>round()</code>, <code>type()</code>.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 6, 'lesson_id': 3, 'title': 'Анализ пароля', 'points': 11, 'difficulty': 'medium',
             'description': '''
                    <p>Пользователь придумал пароль. Система проверяет его длину и выводит тип данных этой длины.</p>
                    <p><strong>Формат ввода:</strong> Строка — пароль.</p>
                    <p><strong>Формат вывода:</strong> Две строки: длина пароля, тип данных длины.</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод: qwerty123
        Вывод:
        9
        &lt;class 'int'&gt;</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод: abc
        Вывод:
        3
        &lt;class 'int'&gt;</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте <code>len()</code> и <code>type()</code>.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 7, 'lesson_id': 3, 'title': 'Программист-археолог', 'points': 12, 'difficulty': 'hard',
             'description': '''
                    <p>Археолог нашёл древний диск с данными. Чтобы прочитать символ, нужно знать его код в десятичной, двоичной и шестнадцатеричной системах.</p>
                    <p><strong>Формат ввода:</strong> Один символ.</p>
                    <p><strong>Формат вывода:</strong> Три строки: код в десятичной, двоичной и шестнадцатеричной системе (заглавными).</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод: Z
        Вывод:
        90
        0b1011010
        0x5A</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод: @
        Вывод:
        64
        0b1000000
        0x40</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте <code>ord()</code>, <code>bin()</code>, <code>hex()</code> и <code>.upper()</code>.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 8, 'lesson_id': 3, 'title': 'Олимпиадный приз', 'points': 12, 'difficulty': 'hard',
             'description': '''
                    <p>На олимпиаде три победителя набрали разное количество баллов. Главный приз получает участник с максимальным баллом. Утешительные призы получают двое оставшихся.</p>
                    <p>Найдите сумму баллов утешительных призов и сколько процентов от максимального балла она составляет (округлить до целого).</p>
                    <p><strong>Формат ввода:</strong> Три целых числа через пробел.</p>
                    <p><strong>Формат вывода:</strong> Две строки: сумма двух меньших, процент от максимума (округлить до целого).</p>
                    <p><strong>Пример 1:</strong></p>
                    <pre><code>Ввод: 5 12 9
        Вывод:
        14
        117</code></pre>
                    <p><strong>Пример 2:</strong></p>
                    <pre><code>Ввод: 100 50 75
        Вывод:
        125
        125</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Найдите максимум, затем сумму двух оставшихся.
                    </div>
                 ''', 'starter_code': '', 'status': None},

            {'id': 9, 'lesson_id': 3, 'title': 'Вадим Маликович и ручные проверки', 'points': 12, 'difficulty': 'hard',
             'description': '''
                    <p>Вадим Маликович получил от студента три числа: количество задач, количество строк кода и количество отступов.</p>
                    <p>Он вычисляет <strong>индекс лени</strong>: <code>(задачи * строки) // (отступы * 2)</code>.</p>
                    <p>Если > 100 — «Я тебе не нейросеть, чтобы за тебя код писать.»</p>
                    <p>Если 50–100 — «Ладно, проверю. Но отступы поправь.»</p>
                    <p>Если < 50 — «Идеально. Даже принтер не понадобится.»</p>
                    <p><strong>Формат ввода:</strong> Три целых числа, каждое с новой строки.</p>
                    <p><strong>Формат вывода:</strong></p>
                    <p>1. Индекс лени в восьмеричной системе (с префиксом 0o).</p>
                    <p>2. Максимальное из трёх чисел.</p>
                    <p>3. Тип данных индекса лени.</p>
                    <p>4. Вердикт.</p>
                    <p><strong>Пример:</strong></p>
                    <pre><code>Ввод:
        10
        200
        2
        Вывод:
        0o372
        200
        &lt;class 'int'&gt;
        Я тебе не нейросеть, чтобы за тебя код писать.</code></pre>
                    <div class="task-hint">
                        <i class="bi bi-lightbulb"></i> Используйте <code>oct()</code>, <code>max()</code>, <code>type()</code>.
                    </div>
                 ''', 'starter_code': '', 'status': None},
        ]
    elif lesson_id == 4:
        return []
    elif lesson_id == 5:
        return []
    elif lesson_id == 6:
        return []
    elif lesson_id == 7:
        return []
    elif lesson_id == 8:
        return []
    return []


@app.route('/course/python/lesson/<int:lesson_id>/task/<int:task_order>')
@login_required
def task(lesson_id, task_order):
    tasks = get_tasks_for_lesson(lesson_id)
    if not tasks:
        return f"<h2>Урок {lesson_id}</h2><p>Задания ещё не добавлены</p>"
    task = tasks[task_order - 1]
    return render_template('task.html', task=task, lesson_id=lesson_id)


@app.route('/course/python/operators')
@login_required
def lesson_operators():
    return render_template('lesson_operators.html')


@app.route('/course/python/while')
@login_required
def lesson_while():
    return render_template('lesson_while.html')


@app.route('/course/python/for')
@login_required
def lesson_for():
    return render_template('lesson_for.html')


@app.route('/course/python/strings')
@login_required
def lesson_strings():
    return render_template('lesson_strings.html')


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


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
