from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_window():
    return render_template('hello_window.html')


@app.route('/register')
def register():
    return "<h1>Страница регистрации </h1>"


@app.route('/login')
def login():
    return "<h1>Страница входа </h1>"


@app.route('/menu')
def hello_window():
    return render_template('menu.html')

def main():
    app.run(port='8080', host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
