from os import getenv
from forms import LoginForm, RegisterForm, PasswordReset

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv("FlaskSecretKey")
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

mdc_challenge_cluster = MongoClient(getenv("MongoDbSecretKey"))
website_db = mdc_challenge_cluster["website"]


@app.route('/', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            flash("You logged in successfully", "success")

    return render_template('sign_in.html', form=form)

def send_verification_email(email, token):
    #need to set up email server, Bruno do this
    pass

def save_user_in_database(email, password):
    website_db["registered_accounts"].insert_one({"email": email, "password": password, "verified": False})

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email, password = form.email.data, form.password.data
            token = serializer.dumps(email, salt='email-confirm')

            save_user_in_database(email, password)
            send_verification_email(email, token)
            flash(f"Your token is {token}", "success")  # for testing purposes
            # flash("You registered successfully, please check your email to verify your account", "success")
            return redirect(url_for('sign_in'))

    return render_template('register.html', form=form)


def verify_user(email):
    website_db["registered_accounts"].update_one({"email": email}, {"$set": {"verified": True}})



@app.route('/verify_email/<token>', methods=['GET', 'POST'])
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        verify_user(email)
        flash("Your email has been verified", "success")
        return redirect(url_for('sign_in'))
    except SignatureExpired:
        flash("Your token is expired, please register your account again", "danger")
        return redirect(url_for('register'))
    except BadTimeSignature:
        flash("Your token is invalid, please register your account again", "danger")
        return redirect(url_for('register'))


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