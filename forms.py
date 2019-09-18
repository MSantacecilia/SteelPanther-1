from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, DateTimeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from webapp.models import User_account


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User_account.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User_account.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CategoryForm(FlaskForm):
    name = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Add Category')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    loc = StringField('Location', validators=[DataRequired()])
    size = StringField('Size', validators=[DataRequired()])
    domain = StringField('Domain', validators=[DataRequired()])
    submit = SubmitField('Add Organization')

class QuestionForm(FlaskForm):
    name = StringField('Question', validators=[DataRequired()])
    submit = SubmitField('Add Question')


class AssessmentForm(FlaskForm):
    submit = SubmitField('Add Assessment')


class TemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired()])
    submit = SubmitField('Create Template')


class QuestionListForm(FlaskForm):
    submit = SubmitField('Submit')