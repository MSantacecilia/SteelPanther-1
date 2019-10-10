from flask import url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from werkzeug import security
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from datetime import datetime

from werkzeug.utils import redirect

from webapp import db, login, app
from sqlalchemy.ext.declarative import declarative_base

# Ordered ALPHABETICALLY



class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    cats = db.relationship("Category", backref='category_assessment', lazy='dynamic')
    evaluations = db.relationship("Evaluation", backref='evaluation_assessment', lazy='dynamic')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    assessmentid = db.Column(db.Integer, db.ForeignKey("assessment.id"), nullable=True)

    questions = db.relationship('Question', backref='question_category', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return '<Category {0}>'.format(self.name)

    def getQuestions(self):
        return Question.query.filter(Question.category_id == self.id).all()


class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), nullable=False)
    assmt = db.Column(db.Integer, db.ForeignKey('assessment.id', ondelete='CASCADE'), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    rating = db.relationship('Rating', backref='rating_evaluation', lazy='dynamic')
    question = db.relationship("Rating", backref='question_evaluation', lazy='dynamic')

    def __repr__(self):
        return '<Evaluation {0} {1}>'.format(Organization.query.get(self.organization_id).name, self.id)


class Guideline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guideline = db.Column(db.String(256))
    quest_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return '<Guideline {0}>'.format(self.guideline)


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    size = db.Column(db.String(64))
    domain = db.Column(db.String(64))

    evaluations = db.relationship('Evaluation', backref='evaluation_organization', lazy='dynamic')

    def __repr__(self):
        return '{0}'.format(self.name)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=False)

    guideline = db.relationship('Guideline', backref='guideline_question', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='rating_question', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return '<Question {0}>'.format(self.name)

    def getGuidelines(self):
        return Guideline.query.filter(Guideline.quest_id == self.id).all()


class Rating(db.Model):
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluation.id'), nullable=False, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    rating = db.Column(db.Integer)
    observation = db.Column(db.String(256))

    def __repr__(self):
        return '<Rating {0} {1} {2}>'.format(Question.query.get(self.question_id).name, Evaluation.query.get(self.evaluation_id), self.rating)


class UserAccount(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    privilege = db.Column(db.Integer, default=2)

    evaluations = db.relationship('Evaluation', backref='evaluation_user_account', lazy='dynamic')


    def __repr__(self):
        return '<UserAccount {0}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_manager(self):
        return self.privilege >= 1

    def is_admin(self):
        return self.privilege == 2


# ADMIN STUFF

class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

    form_excluded_columns = ['evaluations', ]


class UserModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def is_accessible(self):
        return current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

    def on_model_change(self, form, model, is_created):
        model.password_hash = security.generate_password_hash(model.password_hash)

    form_excluded_columns = ['evaluations', ]
    column_exclude_list = ['password_hash']
    column_searchable_list = ['username']


class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin()
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))



# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'darkly'

newadmin = Admin(app, name='SteelPanther', template_mode='bootstrap3', index_view=MyAdminIndexView())
# Add administrative views here


newadmin.add_link(MenuLink(name='Go Back', url='/'))
newadmin.add_view(UserModelView(UserAccount, db.session))
newadmin.add_view(MyModelView(Organization, db.session))
newadmin.add_view(MyModelView(Assessment, db.session))
newadmin.add_view(MyModelView(Evaluation, db.session))
newadmin.add_view(MyModelView(Category, db.session))




@login.user_loader
def load_user(id):
    return UserAccount.query.get(int(id))
