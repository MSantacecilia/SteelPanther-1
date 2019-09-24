from webapp import app, db
from webapp.models import User_account, Organization, Category, Assessment, Question, AssessmentDetail

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User_account,
    'Organization':Organization, 'Category': Category,
    'Assessment': Assessment, 'Question': Question,
    'AssessmentDetail': AssessmentDetail
    }