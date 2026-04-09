from flask import Flask, render_template, session

app = Flask(__name__)
app.secret_key = 'f8874661e03139f344aa90692fd4d642b1e7a89b9b817bba'


@app.route('/')
def hello_window():
    return render_template('hello_window.html')


@app.route('/register')
def register():
    return "<h1>регистрация</h1>"


@app.route('/login')
def login():
    return "<h1>авторизация</h1>"


@app.route('/election_course')
def election_course():
    return render_template('election_course.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
