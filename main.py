from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')

def hello_window():
    return render_template('hello_window.html')

def main():
    app.run(port='8080', host='127.0.0.1')

if __name__ == '__main__':
    main()