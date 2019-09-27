from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from webapp import db, login
from sqlalchemy.ext.declarative import declarative_base

# UserMixin will implement the is_authenticated, is_active, is_anonymous, and get_id() 
# required items for flask_login
class User_account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    manager_status = db.Column(db.Integer, default=1)
    assessments = db.relationship('Assessment', backref='user_account', lazy='dynamic')

    def __repr__(self):
        return '<User_account {0}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.manager_status == 1

category_list = db.Table('category_list', db.Model.metadata, 
    db.Column('org_id', db.Integer, db.ForeignKey('organization.id')),
    db.Column('cat_id', db.Integer, db.ForeignKey('category.id'))
)

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    size = db.Column(db.String(64))
    domain = db.Column(db.String(64))
    assessments = db.relationship('Assessment', backref='organization', lazy='dynamic')
    cats = db.relationship("Category", secondary=category_list)

    def __repr__(self):
        return '{0}'.format(self.name)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    questions = db.relationship('Question', backref='category', lazy='dynamic')
    ass = db.relationship('Assessment', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category {0}>'.format(self.name)

    def getQuestions(self):
        return Question.query.filter(Question.category_id == self.id).all()

class AssessmentDetail(db.Model):
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False, primary_key=True)
    rating = db.Column(db.Integer)
    quest = db.relationship("Question")

    def __repr__(self):
        return '<AssessmentDetail {0} {1} {2}>'.format(Question.query.get(self.question_id).name, Asessment.query.get(self.assessment_id.id), self.rating)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return '<Question {0}>'.format(self.name)
    


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), nullable=False)
    cat = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ass_detail = db.relationship('AssessmentDetail', backref='assessment', lazy='dynamic')
    question = db.relationship("AssessmentDetail")

    def __repr__(self):
        return '<Assessment {0} {1}>'.format(Organization.query.get(self.organization_id).name,self.id)

    def getAssessmentInfo(self):
        qlo = AssessmentDetail.query.all()
        ql = []
        catl = []
        for q in qlo:
            if q.assessment_id == self.id:
                ql.append(q)
        for q in ql:
            catl.append(Category.query.get(Question.query.get(q.question_id).category_id).name)
        catl = list(set(catl))
        catl.sort()
        return ql, catl

@login.user_loader
def load_user(id):
    return User_account.query.get(int(id))
