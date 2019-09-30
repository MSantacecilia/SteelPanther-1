from webapp import app, db
from webapp.models import UserAccount, Organization, Category, Assessment, Question, Rating

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': UserAccount,
    'Organization':Organization, 'Category': Category,
    'Assessment': Assessment, 'Question': Question,
    'Rating': Rating
    }