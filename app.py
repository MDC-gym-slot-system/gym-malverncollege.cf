from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def sign_in():
    return render_template('sign_in.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/password_reset')
def reset_password():
    return render_template('password_reset.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)