from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, Form
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import db

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    def __init__(self,role_):
        self.role=role_
        FlaskForm.__init__(self)

    def validate_username(self, username):
        if db.is_user_by_name(username.data):
            ValidationError('Please use a different username.')
        return True

    def validate_email(self, email):
        if db.is_user_by_email(email.data):
            ValidationError('Please use a different email.')
        return True
