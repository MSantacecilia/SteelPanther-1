from webapp import app, db
from flask import render_template, flash, redirect, url_for, request, jsonify, make_response, session
from werkzeug.urls import url_parse
from webapp.forms import LoginForm, RegistrationForm, CategoryForm, OrganizationForm, QuestionForm, AssessmentForm, RatingForm, ResetPasswordForm, DeleteQuestionsForm, SelectTimestampForm, ViewSingleAssessmentForm
from flask_login import current_user, login_user, logout_user, login_required
from webapp.models import UserAccount, Category, Organization, Question, Evaluation, Rating, Assessment, Guideline
import io,csv, json
import re
from sqlalchemy import and_, subquery


""" Basic Functionalities ================================================================= """
@app.route('/')
@app.route('/index')
@login_required
def index():
    org = Organization.query.all()
    eval= db.session.query(Evaluation,Organization,Assessment).filter((Evaluation.organization_id==Organization.id) & (Evaluation.assmt==Assessment.id)).all()
    return render_template("index.html", title="Home", org=org, eval=eval)




@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # if form.manager.data is True:
        #     manager_status = 1
        user = UserAccount(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        ratinglist = [0]
        session['myratings'] = ratinglist
        session['numquestions'] = 0
        session['myobs'] = ['']
        user = UserAccount.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', "danger")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if form.validate_on_submit():
        if current_user is None or not current_user.check_password(form.password.data):
            flash('Invalid current password', "danger")
            return redirect(url_for('reset_password'))
        current_user.set_password(form.newpassword1.data)
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            flash('Your password was reset successfully!', "success")
        return redirect(next_page)
    return render_template('reset_password.html', title='Reset Password', form=form)


@app.route('/logout')
def logout():
    logout_user()
    session.pop('myratings', None)
    flash('You have been signed out!', "success")
    return redirect(url_for('index'))


""" Add Functionality ========================================================================== """
@app.route('/add_organization',methods=['GET','POST'])
def add_organization():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = OrganizationForm()

    if form.validate_on_submit():
        org = Organization(name=form.name.data, location=form.loc.data,
            size=form.size.data, domain=form.domain.data)
        db.session.add(org)
        db.session.commit()

        flash('Organization was added successfully!', "success")

        assmtList = Assessment.query.all()
        if len(assmtList) == 0:
            return redirect(url_for('add_assessment'))
        else:
            return redirect(url_for('evaluate'))

    return render_template('add_organization.html', title='Add Organization', form=form)


@app.route('/add_assessment',methods=['GET','POST'])
def add_assessment():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['data_file']
        assessment_name = request.form['assessment_name']

        if not import_CSV(file, assessment_name):
            flash('Something went wrong with the CSV upload')
            return redirect(url_for('add_assessment'))

        flash('Assessment was added successfully!', "success")

        orgList = Organization.query.all()
        if len(orgList) == 0:
            return redirect(url_for('add_organization'))
        else:
            return redirect(url_for('evaluate'))

    return render_template('add_assessment.html', title='Add Assessment')


""" Evaluation Functionality ================================================================= """
class DataWithInfo(object):
    def __init__(self, data, info):
        self.data = data
        self.info = info

    def getData(self):
        return self.data

    def getInfo(self):
        return self.info

    def __str__(self):
        return "%s has %i items associated with it" % (self.data, len(self.info))


@app.route('/evaluate',methods=['GET','POST'])
def evaluate():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    org = Organization.query.all()
    assmt = Assessment.query.all()
    gl = Guideline.query.all()

    if request.method == 'POST':
        o_id = request.form['organization']
        a_id = request.form['assessment']
        return redirect(url_for('evaluate_perform', o_id=o_id, a_id=a_id))

    return render_template('evaluate.html', title='Start an Evaluation', org=org, assmt=assmt, gl=gl)


@app.route('/assess/<o_id>&<a_id>', methods=['GET','POST'])
def evaluate_perform(o_id, a_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    page_title = f"Evaluating '{Organization.query.get(o_id).name}' with Assessment '{Assessment.query.get(a_id).name}'"
    form = RatingForm(request.form)
    print(o_id)
    print(a_id)
    if 'savedassess' not in session:
        session['savedassess'] = a_id

    if 'orgname' not in session:
        session['orgname'] = o_id
    print(session)
    session['numquestions'] = 0

    if a_id == session['savedassess']:
        savedassess = session['savedassess']
    else:
        savedassess = [0]

    if o_id == session['orgname']:
        orgname = session['orgname']
    else:
        orgname = [0]
    cL = Category.query.filter(Category.assessmentid == a_id).all()
    categoryList = []
    numberquestonslist = []
    reverseQues=[]
    j = 0
    for c in cL:
        queslist = []
        i=0
        qL = Question.query.filter_by(category_id=c.id).all()
        for q in qL:
            guidelineList = []
            j += 1
            numberquestonslist.append(j)
            gL = Guideline.query.filter_by(quest_id=q.id).order_by(Guideline.guideline).all()
            for g in gL:
                gObj = DataWithInfo(g, [])
                guidelineList.append(gObj)
            qObj = DataWithInfo(q, guidelineList)
            queslist.append(qObj)
            i+=1
        cObj = DataWithInfo(c, queslist)
        categoryList.append(cObj)
        session['numquestions'] += i

    for i in reversed(numberquestonslist):
        reverseQues.append(i)
    session['numqueslist'] = reverseQues

    if form.validate_on_submit():
        if 'save' in request.form:
            queslist = []
            ratinglist = []
            obslist = []

            for catQuestions in categoryList:
                for question in catQuestions.info:
                    queslist.append(question.data)

            for q in queslist:
                if request.method == "POST":
                    if 'obs' + str(q.id) in request.form:
                        obs = str(request.form['obs' + str(q.id)])
                        obslist.append(obs)
                    #print(request.form['rating' + str(q.id)])
                    if 'rating' + str(q.id) in request.form:
                        rate = int(request.form['rating' + str(q.id)])
                        ratinglist.append(rate)
            if savedassess == a_id and orgname == o_id:
                print('inside save')
                session['myratings']=ratinglist
                session['myobs']=obslist
            else:
                session['myratings']=[0]
                session['myobs']=['']
            return render_template('evaluate_perform.html', title=page_title, form=form, categories=categoryList, a_id=a_id, o_id=o_id)

        elif 'submit' in request.form:
            e = Evaluation(user_id=current_user.id, organization_id=o_id, assmt=a_id)
            db.session.add(e)
            db.session.commit()

            queslist = []
            ratinglist = []
            for catQuestions in categoryList:
                for question in catQuestions.info:
                    queslist.append(question.data)

            for q in queslist:
                if request.method == "POST":
                    #print(request.form['rating' + str(q.id)])
                    if 'obs' + str(q.id) in request.form:
                        obs = str(request.form['obs' + str(q.id)])
                    if 'rating' + str(q.id) in request.form:
                        rate = int(request.form['rating' + str(q.id)])
                        ratinglist.append(rate)
                        obj = Rating(evaluation_id=e.id, question_id=q.id, rating=rate, observation=obs)
                        db.session.add(obj)
            session.pop('myratings', None)
            session.pop('savedassess', None)
            session.pop('numquestions', None)
            session.pop('myobs', None)
            session.pop('orgname', None)
            session['myratings'] = [0]
            session['myobs'] = ['']
            db.session.commit()
            flash('The evaluation was successful!', "success")
            return redirect(url_for('view'))

    return render_template('evaluate_perform.html', title=page_title, form=form, categories=categoryList, a_id=a_id, o_id=o_id)


""" Visualization Functionality ================================================================= """
@app.route('/view', methods=['GET','POST'])
def view():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    orgs = Organization.query.all()
    assmt = Assessment.query.all()

    if request.method == 'POST':
        o_id = request.form['organization']
        a_id = request.form['assessment']
        e_id = int(request.form["select"])
        return redirect(url_for('view_display', o_id=o_id, a_id=a_id, e_id=e_id))

    return render_template('view.html', title='Select Criteria of Evaluations', assmt=assmt, orgs=orgs)

@app.route('/filter_assessment/<organization_id>')
def filter_assessment(organization_id):
    evaluations = Evaluation.query.filter_by(organization_id=organization_id).all()
    assessment_array = []
    for evaluation in evaluations:
        assessment = Assessment.query.filter_by(id=evaluation.assmt).first()
        assessmentObj = {}
        assessmentObj["id"] = assessment.id
        assessmentObj["name"] = assessment.name
        if assessmentObj not in assessment_array:
            assessment_array.append(assessmentObj)
    return jsonify({'assessments': assessment_array})


@app.route('/filter_assessment_table/<assessment_id>')
def filter_assessment_table(assessment_id):
    evaluations = Evaluation.query.filter_by(assmt=assessment_id).all()
    evaluations_array = []
    for evaluation in evaluations:
        evaluationObj = {}
        evaluationObj["id"] = evaluation.id
        #evaluation_timestamp = evaluation.timestamp
        evaluationObj["timestamp"] = evaluation.timestamp
        evaluations_array.append(evaluationObj)
    return jsonify({'evaluations': evaluations_array})


@app.route('/view/<o_id>&<a_id>', methods=['GET', 'POST'])
def view_select(o_id,a_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = SelectTimestampForm()
    cats = Category.query.filter_by(assessmentid=a_id)
    eval_details = Evaluation.query.filter_by(assmt=a_id, organization_id=o_id).all()

    if request.method == 'POST':
        e_id = int(request.form["select"])
        return redirect(url_for('view_display', o_id=o_id, a_id=a_id, e_id=e_id))

    return render_template('view_select.html', title='Select Evaluation',  form=form, eval_details=eval_details, cats=cats, o_id=o_id, a_id=a_id)


@app.route('/view/<o_id>&<a_id>&<e_id>', methods=['GET'])
def view_display(o_id, a_id, e_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = ViewSingleAssessmentForm()

    eval_details = db.session.query(Rating, Question, Category).filter(Rating.evaluation_id == e_id).filter(Rating.question_id == Question.id).filter(Question.category_id == Category.id).all()
    questionsArray = []
    categories = []
    guidedetail = []
    for e in eval_details:
        questionObj = {}
        questionObj["question"] = e.Question.name
        questionObj["Value"] = e.Rating.rating
        questionObj["category"] = re.sub(r"[^a-zA-Z0-9]+", ' ', e.Category.name)
        category_name = re.sub(r"[^a-zA-Z0-9]+", ' ', e.Category.name)
        if category_name not in categories:
            categories.append(category_name)
        guidedetail = Guideline.query.filter_by(quest_id=e.Question.id).all()
        questionsArray.append(questionObj)
    json_data = json.dumps(questionsArray)
    organization_name = Organization.query.filter_by(id=o_id).first()
    return render_template('view_display.html', title='View Evaluation Visualization', form=form, eval_details=eval_details, json_data=json_data, guideline=guidedetail, categories=categories, organization_name=organization_name)


""" Edit Assessment Functionalities =============================================================="""
@app.route('/assessment',methods=['GET','POST'])
def assessment():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    assmt = Assessment.query.all()

    if request.method == 'POST':
        assmt_id = request.form['assmt']
        return redirect(url_for('assessment_display',id=assmt_id))

    return render_template('assessment.html', title='Select Assessment', assmt=assmt)


@app.route('/assessment/add',methods=['GET','POST'])
def assessment_add():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    if request.method == 'POST':
        assessment_name = request.form['assessment_name']

    newAssessment = Assessment(name=assessment_name)
    db.session.add(newAssessment)
    db.session.commit()
    newAssmtId = Assessment.query.filter_by(name=assessment_name).first().id


    flash(f"Assessment '{assessment_name}' created successfully", 'success')
    return redirect(url_for('assessment_display', id=newAssmtId))


@app.route('/assessment/<id>',methods=['GET','POST'])
# Agile, Cloud, Devop
def assessment_display(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    form = CategoryForm()
    categories = Category.query.filter_by(assessmentid=id).order_by(Category.name).all()
    assmt = Assessment.query.filter_by(id=id).one()
    return render_template('assessment_display.html', title=f"Editing Assessment '{assmt.name}'", categories=categories, form=form, id=id)


def is_category_repeat(name):
    if Category.query.filter_by(name=name).count() != 0:
        return True
    else: return False


@app.route('/assessment/<id>/category/add',methods=['POST'])
# Agile, Cloud, Devop
def assessment_category_add(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_category_name = request.form['new_cat']
        if is_category_repeat(new_category_name):
            flash(f"Category '{new_category_name}' already exists. Please make sure category you create has a unique name. ", 'error')
        else:
            cat = Category(name=new_category_name, assessmentid=id)
            db.session.add(cat)
            db.session.commit()
            flash(f"Category '{new_category_name}' added successfully", 'success')
        return redirect(url_for('assessment_display', id=id))


@app.route('/assessment/<id>/category/update/<cid>',methods=['POST'])
def assessment_category_update(id, cid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_category_name = request.form[f"cat_name{cid}"]
        if is_category_repeat(new_category_name):
            flash(f"Category '{new_category_name}' already exists. Please make sure the new category name is unique. ", 'error')
        else:
            cat = Category.query.filter_by(id=cid, assessmentid=id).first()
            cat.name = new_category_name
            flash(f"Category name updated to '{new_category_name}'", 'success')
            db.session.commit()
        return redirect(url_for('assessment_display', id=id))


@app.route('/assessment/<id>/category/<cid>/delete', methods = ['GET'])
def assessment_category_delete(id, cid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    delete_category = Category.query.filter_by(id=cid, assessmentid=id).one()
    db.session.delete(delete_category)
    db.session.commit()
    flash(f"Category '{delete_category.name}' deleted successfully", 'success')

    return redirect(url_for('assessment_display', id=id))


""" Import CSV Functionality ================================================================= """
def import_CSV(file, assessment_name):
    f = file
    if not f:
        # No file error
        return False
    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)

    # Keep track of row to skip the first 10 rows
    currentRow = 1
    firstRow = 10

    # Add an assessment to the database
    # assessment_name = request.form['assessment_name']
    assessment = Assessment(name=assessment_name)
    db.session.add(assessment)
    db.session.commit()

    # Use the id to create new categories and questions
    assessment_id = assessment.id
    category_id = -1

    for row in csv_input:
        if currentRow < firstRow:
            currentRow = currentRow + 1
            continue

        # This row corresponds to a category
        if row[1] == "":
            category_name = row[0]
            category = Category.query.filter_by(name=category_name, assessmentid=assessment_id).first()

            if category is None:
                category = Category(name=category_name, assessmentid=assessment_id)
                db.session.add(category)
                db.session.commit()

            # This will be used to create questions if necessary
            category_id = category.id

        # This row corresponds to a question
        else:
            question_name = row[0]
            # question_max = int(row[2])
            question_weightage = row[4]
            question = Question.query.filter_by(name=question_name, category_id=category_id).first()

            if question is None:

                question = Question(name=question_name, category_id=category_id)
                db.session.add(question)
                db.session.commit()

                # A new question also means the guidelines must be added
                question_id = question.id
                guidelines = row[1].split('\n')

                for g in guidelines:
                    guideline = Guideline(guideline=g, quest_id=question_id)
                    db.session.add(guideline)

                db.session.commit()

    return True
