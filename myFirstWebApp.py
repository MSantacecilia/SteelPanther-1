from webapp import app, db
from webapp.models import User, Organization, Category, Assessment, AssessmentTemplate, Question, QuestionList

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 
    'Organization':Organization, 'Category': Category,
    'Assessment': Assessment, 'Question': Question,
    'AssessmentTemplate': AssessmentTemplate,'QuestionList': QuestionList
    }