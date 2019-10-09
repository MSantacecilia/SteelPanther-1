from webapp import app, db
from webapp.models import UserAccount, Organization, Category, Evaluation, Question, Rating, Assessment

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': UserAccount,
    'Organization':Organization, 'Category': Category,
    'Evaluation': Evaluation, 'Question': Question,
    'Rating': Rating, 'Assessment': Assessment
    }