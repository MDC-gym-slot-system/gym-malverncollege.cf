from os import getenv
from re import search

from flask_bcrypt import check_password_hash
from pandas import read_excel
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from markupsafe import Markup
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

mdc_challenge_cluster = MongoClient(getenv("MongoDbSecretKey"))
website_db = mdc_challenge_cluster["website"]


def is_email_verified(form, email):
    found_account = website_db["registered_accounts"].find_one({"email": email.data})
    if found_account:
        if not found_account["verified"]:
            raise ValidationError(
                'Email not verified, check your email to verify your account<br>'
                'Reregister if you did not receive an email'
            )
    elif not found_account:
        raise ValidationError('Email not registered, register an account')


def is_password_valid(form, password):
    found_account = website_db["registered_accounts"].find_one({"email": form.email.data})
    if found_account:
        if not check_password_hash(found_account["password"], password.data):
            raise ValidationError('Incorrect password')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email(), is_email_verified])
    password = PasswordField('Password', validators=[DataRequired(), is_password_valid])
    submit = SubmitField('Sign In')


def is_email_allowed_to_register_account(form, email):
    emails_allowed_to_register_account = read_excel(r'./static/excel_sheets/emails.xlsx')
    if email.data not in emails_allowed_to_register_account['email'].values:
        raise ValidationError('Email not allowed to register an account')


def is_email_already_registered(form, email):
    found_account = website_db["registered_accounts"].find_one({"email": email.data})
    if found_account:
        if not found_account["verified"]:
            website_db["registered_accounts"].delete_many({"email": email.data})
        else:
            raise ValidationError('Email already registered, reset password if forgotten')


def is_password_strong_enough(form, password):
    password = password.data
    length_error = len(password) < 8

    digit_error = search(r"\d", password) is None

    alphabet_error = search(r"[a-zA-Z]", password) is None

    symbol_error = search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None

    password_ok = not (length_error or digit_error or alphabet_error or symbol_error)
    if not password_ok:
        raise ValidationError(
            Markup('Password must be at least 8 characters long.<br>Contain at least one digit, letter and symbol')
        )


class RegisterForm(FlaskForm):
    email = StringField(
        'email',
        validators=[
            DataRequired(),
            Email(),
            is_email_allowed_to_register_account,
            is_email_already_registered
        ]
    )
    password = PasswordField('password', validators=[DataRequired(), is_password_strong_enough])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('register')


def is_email_registered_and_verified(form, email):
    found_account = website_db["registered_accounts"].find_one({"email": email.data})
    if found_account:
        if not found_account["verified"]:
            raise ValidationError('Email not verified, check your email to verify your account')
    elif not found_account:
        raise ValidationError('Email not registered')


class PasswordReset(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), is_email_registered_and_verified])
    new_password = PasswordField('new_password', validators=[DataRequired(), is_password_strong_enough])
    confirm_new_password = PasswordField('confirm_new_password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('reset password')