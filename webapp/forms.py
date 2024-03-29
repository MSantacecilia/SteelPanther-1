from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, DateTimeField, SelectField, validators
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from webapp.models import UserAccount


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'autofocus': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = UserAccount.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = UserAccount.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'autofocus': True})
    newpassword1 = PasswordField('New Password', validators=[DataRequired()])
    newpassword2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('newpassword1')])
    submit = SubmitField('Confirm')

class CategoryForm(FlaskForm):
    name = StringField('', [validators.DataRequired()], render_kw={'autofocus': True})
    submit = SubmitField('Submit')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={'autofocus': True})
    loc = StringField('Location', validators=[DataRequired()])
    myChoices = [('0-500', '0-500'), ('501-2000', '501-2000'), ('2001-5000', '2001-5000'),('5000+', '5000+')]
    size = SelectField('Number of employees',choices=myChoices, validators=[DataRequired()])
    domain = StringField('Domain', validators=[DataRequired()])
    submit = SubmitField('Add Organization')

class QuestionForm(FlaskForm):
    name = StringField('Question', validators=[DataRequired()], render_kw={'autofocus': True})
    submit = SubmitField('Add Question')
""" 
class GuidelineForm(FlaskForm):
    name = StringField('Guideline', validators=[DataRequired()], render_kw={'autofocus': True})
    submit = SubmitField('Add Guidelines')
 """
class AssessmentForm(FlaskForm):
    submit = SubmitField('Add Assessment')

class RatingForm(FlaskForm):
    submit = SubmitField('Submit')
	
class DeleteQuestionsForm(FlaskForm):
    categories = SelectField('category', choices=[])
    submit = SubmitField('Submit')

class SelectTimestampForm(FlaskForm):
    submit = SubmitField('Submit')

class ViewSingleAssessmentForm(FlaskForm):
    submit = SubmitField('Submit')
