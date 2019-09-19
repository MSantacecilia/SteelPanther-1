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
    manager_status = db.Column(db.Integer, default=False)
    assessments = db.relationship('Assessment', backref='user_account', lazy='dynamic')
    assessment_templates = db.relationship('AssessmentTemplate', backref='user_account', lazy='dynamic')

    def __repr__(self):
        return '<User_account {0}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.manager_status == 1


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    size = db.Column(db.String(64))
    domain = db.Column(db.String(64))
    assessments = db.relationship('Assessment', backref='organization', lazy='dynamic')

    def __repr__(self):
        return '{0}'.format(self.name)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    questions = db.relationship('Question', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category {0}>'.format(self.name)

    def getQuestions(self):
        return Question.query.filter(Question.category_id == self.id).all()


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    questionlist = db.relationship('QuestionList', backref='question', lazy='dynamic')

    def __repr__(self):
        return '<Question {0}>'.format(self.name)
    


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), nullable=False)
    questionlist = db.relationship('QuestionList', backref='assessment', lazy='dynamic')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Assessment {0} {1}>'.format(Organization.query.get(self.organization_id).name,self.id)

    def getAssessmentInfo(self):
        qlo = QuestionList.query.all()
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


class QuestionList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    rating = db.Column(db.Integer)

    def __repr__(self):
        return '<QuestionList {0} {1}>'.format(Question.query.get(self.question_id).name,self.id)


class AssessmentTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id'), nullable=False)
    questions = db.Column(db.Text)

    def __repr__(self):
        return '<AssessmentTemplate {0} {1}>'.format(self.name)
    
    def getQuestions(self):
        ql = [int(x) for x in self.questions.split(',')]
        queslist = []
        for q in ql:
            query = Question.query.get(q)
            if query != None:
                queslist.append(query)
        return queslist
    
    def getIdList(self):
        ql = []
        if len(self.questions) > 0:
            ql = [int(x) for x in self.questions.split(',')]
        return ql


@login.user_loader
def load_user(id):
    return User_account.query.get(int(id))
