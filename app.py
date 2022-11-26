from flask import Flask, render_template, request, url_for, redirect, flash
from pymongo import MongoClient
from forms import LoginForm, RegisterForm, PasswordReset
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
            flash("You logged in successfully", "success")

    return render_template('sign_in.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            flash("You registered successfully", "success")
            return redirect(url_for('sign_in'))


    return render_template('register.html', form=form)


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    form = PasswordReset()
    if request.method == "POST":
        if form.validate_on_submit():
            flash("You reset your password successfully", "success")
            return redirect(url_for('sign_in'))
    return render_template('password_reset.html', form=PasswordReset())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)