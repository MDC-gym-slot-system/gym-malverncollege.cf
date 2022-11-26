from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from forms import LoginForm, RegisterForm, OneTimePasscodeForm
from os import getenv
from dotenv import load_dotenv
load_dotenv()
mongo_client = MongoClient(getenv("MongoDbSecretKey"))

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv("FlaskSecretKey")

@app.route('/', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            return (
                f"you logged in as {request.form['email']}<br>"
                f"your password is {request.form['password']}"
            )

    return render_template('sign_in.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            #create one time passcode linked to email and password
            #send email to user with one time passcode

            return redirect(url_for('one_time_passcode'))


    return render_template('register.html', form=form)


@app.route('/password_reset')
def reset_password():
    return render_template('password_reset.html')

@app.route('/one_time_passcode', methods=['GET', 'POST'])
def one_time_passcode():
    form = OneTimePasscodeForm()
    return render_template('one_time_passcode.html', form=form)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)