from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from pandas import read_excel


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


def is_email_allowed_to_register_account(form, email):
    emails_allowed_to_register_account = read_excel(r'./static/excel_sheets/emails.xlsx')
    if email.data not in emails_allowed_to_register_account['email'].values:
        raise ValidationError('Email not allowed to register an account')

def is_email_already_registered(form, email):
    #use database to check if email is already registered
    pass


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
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('register')



class OneTimePasscodeForm(FlaskForm):
    passcode = StringField('passcode', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate_passcode(self, passcode):
        #depending on the way of generating the passcode, this will need to be changed
        pass