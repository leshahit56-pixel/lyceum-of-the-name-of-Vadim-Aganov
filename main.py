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
from werkzeug.utils import secure_filename
from tasks_data import get_tasks_for_lesson

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
            status_dict[num] = val
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
            if verdict_in_db == 2:
                verdict = 2
            else:
                verdict = verdict

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
