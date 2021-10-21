from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField
from wtforms.validators import Required


class LoginForm(FlaskForm):
    login = TextField('login', validators=[Required()], description='Enter login')
    password = PasswordField('password', validators=[Required()], description='Enter password')
    remember_me = BooleanField('remember_me', default=False)