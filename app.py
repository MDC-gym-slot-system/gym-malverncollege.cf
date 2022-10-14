from flask import Flask
app = Flask(__name__)


@app.route('/')
def sign_in():
    return "This is the future sign in page"


@app.route('/register')
def register():
    return "This is the future register page"


@app.route('/password_reset')
def reset_password():
    return "This is the future reset password page"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)