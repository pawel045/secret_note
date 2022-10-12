from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length


class NoteForm(FlaskForm):
    addressee = StringField(label='Addressee', validators=[DataRequired()])
    title = StringField(label='Title')
    content = TextAreaField(label='Content', validators=[Length(max=300)])
    submit = SubmitField(label='SEND')


class CopyForm(FlaskForm):
    copy = SubmitField(label='COPY')


class LoginForm(FlaskForm):
    login = StringField(label='Login', validators=[DataRequired(), Length(5)])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(5)])
    submit = SubmitField(label='Log in')


class RegisterForm(FlaskForm):
    login = StringField(label='Login', validators=[DataRequired(), Length(5)])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(5)])
    submit = SubmitField(label='Register')

