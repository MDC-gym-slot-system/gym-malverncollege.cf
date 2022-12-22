from os import getenv
from forms import LoginForm, RegisterForm, PasswordReset
from pandas import read_excel
from datetime import timedelta

from flask_bcrypt import generate_password_hash
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv("FlaskSecretKey")
app.config['SESSION_COOKIE_NAME'] = "User details"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(weeks=2)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

mdc_challenge_cluster = MongoClient(getenv("MongoDbSecretKey"))
website_db = mdc_challenge_cluster["website"]


@app.route('/', methods=['GET', 'POST'])
def login():
    if "email" in session:
        return render_template('dashboard.html', email=session['email'])
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            session.clear()
            session['email'] = form.email.data
            flash("You logged in successfully", "success")
            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)


def send_verification_email(email, token):
    #need to set up email server, wait for email from IT
    pass


def save_user_in_database(email, password):
    website_db["registered_accounts"].insert_one({"email": email, "password": password, "verified": False})


def handle_log_in(is_protected, redirect):
    is_logged_in = True
    if "email" not in session:
        is_logged_in = False

    if is_protected and is_logged_in is False:
        flash("You need to be logged in to access this page", "danger")
        if redirect:
            return redirect(url_for('login'))

    if not is_protected and is_logged_in:
        if redirect:
            flash("You are already logged in", "danger")
            return redirect(url_for('dashboard', email=session['email']))


@app.route('/register', methods=['GET', 'POST'])
def register():
    handle_log_in(is_protected=False, redirect=True)
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email, password = form.email.data, form.password.data
            token = serializer.dumps(email, salt='email-confirm')

            save_user_in_database(email, generate_password_hash(password).decode('utf-8'))
            send_verification_email(email, token)
            flash(f"Your token is {token}", "success")  # for testing purposes
            # flash("You registered successfully, please check your email to verify your account", "success")
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


def verify_user(email):
    emails_allowed_to_register_account = read_excel(r'./static/excel_sheets/emails.xlsx')
    group = emails_allowed_to_register_account.loc[emails_allowed_to_register_account['email'] == email, 'group'].values[0]
    house = emails_allowed_to_register_account.loc[emails_allowed_to_register_account['email'] == email, 'house'].values[0]
    is_admin = emails_allowed_to_register_account.loc[emails_allowed_to_register_account['email'] == email, 'is_admin'].values[0]
    website_db["registered_accounts"].update_one(
        {"email": email},
        {"$set": {"verified": True, "group": int(group), "house": int(house), "is_admin": bool(is_admin)}}
    )


@app.route('/verify_email/<token>', methods=['GET', 'POST'])
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        verify_user(email)
        flash("Your email has been verified", "success")
        return redirect(url_for('login'))
    except SignatureExpired:
        flash("Your token is expired, please register your account again", "danger")
        return redirect(url_for('register'))
    except BadTimeSignature:
        flash("Your token is invalid, please register your account again", "danger")
        return redirect(url_for('register'))


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    handle_log_in(is_protected=False, redirect=False)
    form = PasswordReset()
    if request.method == "POST":
        if form.validate_on_submit():
            flash("You reset your password successfully", "success")
            return redirect(url_for('login'))
    return render_template('password_reset.html', form=PasswordReset())


@app.route('/dashboard')
def dashboard():
    handle_log_in(is_protected=True, redirect=False)
    return render_template('dashboard.html', email=session['email'])

@app.route('/logout')
def logout():
    handle_log_in(is_protected=True, redirect=True)
    session.clear()
    flash("You logged out successfully", "success")
    return redirect(url_for('login'))

@app.route('/booking')
def booking():
    handle_log_in(is_protected=True, redirect=True)
    return render_template('booking.html', email=session['email'])

@app.route('/edit_booking')
def edit_booking():
    handle_log_in(is_protected=True, redirect=True)
    return render_template('edit_booking.html', email=session['email'])

@app.route('/admin')
def admin():
    handle_log_in(is_protected=True, redirect=True)
    # check if email is admin
    return render_template('admin.html', email=session['email'])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)