from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from webapp import db, login
from sqlalchemy.ext.declarative import declarative_base

# Ordered ALPHABETICALLY

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    cats = db.relationship("Category", backref='category_assessment', lazy='dynamic')
    evalulations = db.relationship("Evaluation", backref='evaluation_assessment', lazy='dynamic')


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
        return '<Evaluation {0} {1}>'.format(Organization.query.get(self.organization_id).name,self.id)


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

    evalulations = db.relationship('Evaluation', backref='evaluation_organization', lazy='dynamic')
    
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
    privilege = db.Column(db.Integer, default=1)

    evalulations = db.relationship('Evaluation', backref='evaluation_user_account', lazy='dynamic')


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


@login.user_loader
def load_user(id):
    return UserAccount.query.get(int(id))
