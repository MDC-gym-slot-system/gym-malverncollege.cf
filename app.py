from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def sign_in():
    if request.method == "POST":
        return (
            f"you logged in as {request.form['email_address']}<br>"
            f"your password is {request.form['password']}"
        )

    return render_template('sign_in.html')



@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/password_reset')
def reset_password():
    return render_template('password_reset.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)