from webapp import app, db
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from webapp.forms import LoginForm, RegistrationForm, CategoryForm, OrganizationForm, QuestionForm, AssessmentForm, AssessmentDetailForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from webapp.models import User_account, Category, Organization, Question, Assessment, AssessmentDetail, category_list


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
        user = User_account(username=form.username.data, email=form.email.data, manager_status=True)
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
        user = User_account.query.filter_by(username=form.username.data).first()
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
            flash('Invalid username or password')
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
        catlist = Category.query.all()
        for c in catlist:
            org.cats.append(c)
        db.session.add(org)
        db.session.commit()
        flash('Success')
        return redirect(url_for('index'))
    return render_template('add_organization.html', title='Add Organization', form=form)


@app.route('/add_category',methods=['GET','POST'])
def add_category():
    # This functionality is only for managers
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    form = CategoryForm()
    if form.validate_on_submit():
        cat = Category(name=form.name.data)
        db.session.add(cat)
        db.session.commit()
        flash('Success')
        return redirect(url_for('add_question'))
    return render_template('add_category.html', title='Add Category', form=form)

@app.route('/test_category',methods=['GET','POST'])
# Agile, Cloud, Devop
def test_category():
    # This functionality is only for managers
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not current_user.is_admin():
        return redirect(url_for('index'))

    # ==trial======================================================= 
    if request.method == "POST":
        category_name = request.form["category_name"]
        
    # ==endtrial====================================================

    # form = QuestionForm()
    # cats = Category.query.all()
    # if form.validate_on_submit():
    #     q = Question(name=form.name.data, category_id=request.form['cat'])
    #     db.session.add(q)
    #     db.session.commit()
    #     flash('Success')
    #     return redirect(url_for('index'))
    return render_template('test_category.html', title='Test Category')

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
        return redirect(url_for('index'))
    return render_template('add_question.html', title='Add Question', form=form, cats=cats)

#TODO change cat query to pull relevant questions based on category list
@app.route('/select_assessment_category',methods=['GET','POST'])
def select_assessment_category():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    org = Organization.query.all()
    cat = Category.query.all()
    return render_template('select_assessment_category.html', title='Select Template', org=org, cat=cat)


@app.route('/assess',methods=['GET','POST'])
def assess():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    org = int(request.args['org'])
    cat = int(request.args['category'])
    form = AssessmentDetailForm(request.form)
    ql = Category.query.get(cat)
    queslist = ql.getQuestions()
    if form.validate_on_submit():
        a = Assessment(user_id=current_user.id, organization_id=org)
        db.session.add(a)
        db.session.commit()
        for q in queslist:
            obj = AssessmentDetail(assessment_id=a.id, question_id=q.id,rating=request.form[str(q.id)])
            db.session.add(obj)
        db.session.commit()
        flash('Success')
        return redirect(url_for('index'))
    return render_template('assess.html', title='Assessment', form=form, ql=queslist)

@app.route('/select_visual', methods=['GET'])
def select_vis():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    orgs = Organization.query.all()
    assessments = Assessment.query.all()
    return render_template('select_vis.html', title='Select Visual', assessments=assessments, orgs=orgs)


@app.route('/vis', methods=['GET'])
def indv_vis():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    assess_id = int(request.args['assessment'])
    assess_info = Assessment.query.get(assess_id).getAssessmentInfo()
    for obj in assess_info[0]:
        for ch in obj.question.name:
            if ch == '&':
                obj.question.name = obj.question.name.replace("&", "and")
                db.session.add(obj)
                db.session.commit()
    return render_template('single_assess_vis.html', title='Visual', questions_list_object=assess_info[0], category_list=assess_info[1])


@app.route('/multi_vis',methods=['GET'])
def multi_vis():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    organization_id = int(request.args['org'])
    # assessmentList = Assessment.query.all()
    AssessmentDetail = AssessmentDetail.query.all()
    assessDict = {}
    ratingdict = {}
    for q in AssessmentDetail:
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

#TODO
# def export_csv():