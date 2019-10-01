from webapp import app, db
from flask import render_template, flash, redirect, url_for, request, jsonify, make_response
from werkzeug.urls import url_parse
from webapp.forms import LoginForm, RegistrationForm, CategoryForm, OrganizationForm, QuestionForm, AssessmentForm, RatingForm, ResetPasswordForm, DeleteQuestionsForm, SelectTimestampForm, ViewSingleAssessmentForm
from flask_login import current_user, login_user, logout_user, login_required
from webapp.models import UserAccount, Category, Organization, Question, Assessment, Rating, Template, Guideline
import io,csv
from sqlalchemy import and_


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title="Home")


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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAccount.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
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
            flash('Invalid current password')
            return redirect(url_for('reset_password'))
        current_user.set_password(form.newpassword1.data)
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('reset_password.html', title='Reset Password', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#TODO: add functionality to select relevant categories
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
        flash('Success')
        return redirect(url_for('add_organization'))
    return render_template('add_organization.html', title='Add Organization', form=form)


@app.route('/add_category',methods=['GET','POST'])
def add_category():
    # This functionality is only for managers
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))
    form = CategoryForm()
    temp = Template.query.all()
    if form.validate_on_submit():
        cat = Category(name=form.name.data, templateid=request.form['temp'])
        db.session.add(cat)
        db.session.commit()
        flash('Success')
        return redirect(url_for('add_question'))
    return render_template('add_category.html', title='Add Category', form=form, temp=temp)

@app.route('/test_category',methods=['GET','POST'])
# Agile, Cloud, Devop
def test_category():
    # This functionality is only for managers
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))
    categories = Category.query.all()

    # ==trial======================================================= 
    # if request.method == "POST":
    #     category_name = request.form["category_name"]
        
    # ==endtrial====================================================

    # form = QuestionForm()
    # cats = Category.query.all()
    # if form.validate_on_submit():
    #     q = Question(name=form.name.data, category_id=request.form['cat'])
    #     db.session.add(q)
    #     db.session.commit()
    #     flash('Success')
    #     return redirect(url_for('index'))
    return render_template('test_category.html', title='Test Category', categories=categories)

@app.route('/add_question',methods=['GET','POST'])
def add_question():
    # This functionality is only for managers
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    form = QuestionForm()
    cats = Category.query.all()
    if form.validate_on_submit():
        q = Question(name=form.name.data, category_id=request.form['cat'])
        db.session.add(q)
        db.session.commit()
        flash('Success')
        return redirect(url_for('add_question'))
    return render_template('add_question.html', title='Add Question', form=form, cats=cats)

#TODO change cat query to pull relevant questions based on category list
@app.route('/select_assessment_category',methods=['GET','POST'])
def select_assessment_category():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    org = Organization.query.all()
    temp = Template.query.all()
    return render_template('select_assessment_category.html', title='Select Template', org=org, temp=temp)


@app.route('/assess',methods=['GET','POST'])
def assess():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    org = int(request.args['org'])
    temp = int(request.args['template'])
    form = RatingForm(request.form)
#   cat = Template.query.get(temp)
    categorylist = []
    cl = Category.query.filter(Category.templateid == temp).all()
    categorylist.append(cl)
#    queslist = ql.getQuestions()
    queslist = []
    for cat in categorylist:
        for question in cat:
            queslist.extend(question.getQuestions())
    if form.validate_on_submit():
        a = Assessment(user_id=current_user.id, organization_id=org, temp=temp)
        db.session.add(a)
        db.session.commit()
        for q in queslist:
            obj = Rating(assessment_id=a.id, question_id=q.id,rating=request.form[str(q.id)])
            db.session.add(obj)
        db.session.commit()
        flash('Success')
        return redirect(url_for('select_assessment_category'))
    return render_template('assess.html', title='Assessment', form=form, ql=queslist)

@app.route('/select_vis', methods=['GET'])
def select_vis():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    orgs = Organization.query.all()
    temp = Template.query.all()
    return render_template('select_vis.html', title='Select Visual', temp=temp, orgs=orgs)


@app.route('/select_timestamp', methods=['GET'])
def select_timestamp():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    orgs = int(request.args['orgs'])
    temp = int(request.args['temp'])
    cats = Category.query.filter(Category.templateid == temp)
    form = SelectTimestampForm()
    assess_deets = Assessment.query.filter((Assessment.temp == temp) & (Assessment.organization_id == orgs)).all()
   
#   assess_cat = Assessment.query.filter(Assessment.cat == Category.query.get(cats)).all()
#   assess_org = Assessment.query.filter(Assessment.organization_id == Organization.query.get(orgs)).all()
    return render_template('select_timestamp.html', title='Relevant Assessments',  form=form, assess_deets=assess_deets, cats=cats)
    
@app.route('/view_single_assessment', methods=['GET','POST'])
def view_single_assessment():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ViewSingleAssessmentForm()
    if request.method == "POST":
        ad = int(request.form["select"])
    assessdetails = Rating.query.filter(ad == Rating.assessment_id).all()
    for a in assessdetails:
        print(a)
    return render_template('view_single_assessment.html', title='View Assessment', form=form, assessdetails=assessdetails)

@app.route('/multi_vis',methods=['GET'])
def multi_vis():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    organization_id = int(request.args['org'])
    # assessmentList = Assessment.query.all()
    Rating = Rating.query.all()
    assessDict = {}
    ratingdict = {}
    for q in Rating:
        if q.assessment.organization.id == organization_id:
            if q.assessment.id not in assessDict:
                q.count = 1
                assessDict[q.assessment.id] = q
                # if q.rating == "":
                #     q.rating = "0"
                #     q.save()
                ratingdict[q.assessment.id] = int(q.rating)
            else:
                # if q.rating == "":
                #     q.rating = "0"
                #     q.save()
                ratingdict[q.assessment.id] += int(q.rating)
                assessDict[q.assessment.id].count += 1

            for k in assessDict:
                if k in ratingdict:
                    assessDict[k].rating = str(int(round(ratingdict[k] / assessDict[k].count, 1)))

    return render_template('multiple_assess_vis.html', title='Multi-Visual', assessDict=assessDict, ratingDict=ratingdict)
	
@app.route('/delete_question', methods=['GET', 'POST'])
def delete_question():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = DeleteQuestionsForm()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Edit':
            pass  # do something
        elif request.form['submit_button'] == 'Delete':
            pass  # do something else
        else:
            pass  # unknown
    elif request.method == 'GET':
        form.categories.choices = [(category.id, category.name) for category in Category.query.all()]
        categories = Category.query.all()
        return render_template('delete_question.html', title='Delete Question', form=form, categories=categories)

@app.route('/guidelines', methods=['GET', 'POST'])
def filter_guidelines():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    guidelines = Guidelines.query.all()
    return render_template()('guidelines.html', title='Guidelines for Rating', guidelines=guidelines)

@app.route('/filter_questions/<categoryId>')
def filter_questions(categoryId):
    questions = Question.query.filter_by(category_id=categoryId).all()
    questionsArray = []
    for question in questions:
        questionObj = {}
        questionObj["id"] = question.id
        questionObj["name"] = question.name
        questionsArray.append(questionObj)
    return jsonify({'questions': questionsArray})
	
@app.route('/update_question/<questionId>/<updatedQuestion>')
def update_questions(questionId, updatedQuestion):
    question = Question.query.filter_by(id=questionId).first()
    question.name = updatedQuestion
    db.session.commit()
    return jsonify({'result': "success"})
	
@app.route('/delete_question/<questionId>')
def delete_selected_questions(questionId):
    try:
        Question.query.filter_by(id=questionId).delete()
        db.session.commit()
        return jsonify({'result': "success"})
    except Exception as e:
        return jsonify("result", "failure")

@app.route('/transform', methods=["POST"])
def transform_view():
    f = request.files['data_file']
    if not f:
        return "No file"
    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    currentRow = 1
    firstRow = 10
    # TODO first, create/find template id
    template_name = 'NewTemplate'
    template = Template(name=template_name)
    db.session.add(template)
    db.session.commit()
    template_id = template.id
    category_id = -1
    # TODO should we store a list of items to add first, or will this work?
    for row in csv_input:
        if currentRow < firstRow:
            currentRow = currentRow + 1
            continue
        # Look at category, create if it does not yet exist
        if row[1] == "":
            category_name = row[0]
            category = Category.query.filter_by(name=category_name).filter_by(templateid=template_id).first()
            if category is None:
                category = Category(name=category_name, templateid=template_id)
                db.session.add(category)
                db.session.commit()
            category_id = category.id
            db.session.commit()
        # Look at question, create if it does not yet exist
        else:
            question_name = row[0]
            question_max = int(row[2])
            print(question_max)
            question_weightage = row[4]
            question = Question.query.filter_by(name=question_name, category_id=category_id).first()
            if question is None:
                question = Question(name=question_name, category_id=category_id)
                db.session.add(question)
                db.session.commit()
                question_id = question.id
                guidelines = row[1].split('\n')
                for i in range(question_max+1):
                    guideline = Guideline(guideline=guidelines[i], quest_id=question_id)
                    db.session.add(guideline)
                    db.session.commit()
    
    stream.seek(0)
    result = transform(stream.read())
    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=result.csv"
    return response
	
def transform(text_file_contents):
    return text_file_contents.replace("=", ",")		

#TODO
# def export_csv():