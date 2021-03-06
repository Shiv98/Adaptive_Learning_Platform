from flask import Flask, request, jsonify, render_template,redirect, url_for,flash,session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
app.secret_key = "shivanginavigus"
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Teacher Class/Model
class Teacher(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(128))

    def __init__(self,username,name,password):
        self.username=username
        self.name=name
        self.password=password

# Teacher Schema
class TeacherSchema(ma.Schema):
  class Meta:
    fields = ('username', 'name', 'password')

# init Schema
t_schema = TeacherSchema()
ts_schema = TeacherSchema(many=True)

#Course Class/Model
class Course(db.Model):
    courseid = db.Column(db.String(100), primary_key=True)
    coursename = db.Column(db.String(100))
    semester = db.Column(db.String(128))
    credit = db.Column(db.String(128))
    hasquiz = db.Column(db.String(128))

    def __init__(self,courseid,coursename,semester,credit,hasquiz):
        self.courseid=courseid
        self.coursename=coursename
        self.semester=semester
        self.credit = credit
        self.hasquiz= hasquiz

# Course Schema
class CourseSchema(ma.Schema):
  class Meta:
    fields = ('courseid', 'coursename', 'semester','credit','hasquiz')

# init Schema
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

#Question Class/Model
class Question(db.Model):
    cid = db.Column(db.String(100))
    qid = db.Column(db.String(100),primary_key=True)
    ques = db.Column(db.String(300))
    op1 = db.Column(db.String(100))
    op2 = db.Column(db.String(100))
    op3 = db.Column(db.String(100))
    ans = db.Column(db.String(100))
    marks = db.Column(db.String(100))

    def __init__(self,cid,qid,ques,op1,op2,op3,ans,marks):
        self.cid = cid
        self.qid = qid
        self.ques=ques
        self.op1=op1
        self.op2=op2
        self.op3=op3
        self.ans = ans
        self.marks = marks

# Teacher Schema
class QuestionSchema(ma.Schema):
  class Meta:
    fields = ('cid', 'qid', 'ques','op1','op2','op3','ans','marks')

# init Schema
q_schema = QuestionSchema()
qs_schema = QuestionSchema(many=True)


#Authtication routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def loginst():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    uname = request.form.get('uname')
    password = request.form.get('password')

    user = Teacher.query.filter_by(username=uname).first()

    # check if the user actually exists
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect('/login') # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    session['username'] = uname
    return redirect('/teacherdashboard')

@app.route('/logout')
def logout():
    session['username'] = None
    return redirect('/')

# Create a Teacher
@app.route('/teacher', methods=['POST'])
def add_teacher():

    usernamef = request.form.get('username')
    namef = request.form.get('name')
    passwordf = request.form.get('password')

    user = Teacher.query.filter_by(username=usernamef).first()  # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Username already exists, Try with a different username or login!')
        return render_template('index.html')
    
    new_teacher = Teacher(usernamef, namef,generate_password_hash(passwordf, method='sha256'))
    db.session.add(new_teacher)
    db.session.commit()

    return redirect('/login')

# Get All Teachers (For testing on Postaman)
@app.route('/teacher', methods=['GET'])
def get_teachers():
    all_teachers = Teacher.query.all()
    result = ts_schema.dump(all_teachers)
    return jsonify(result)

# Get Single Teacher (For testing on Postaman)
@app.route('/teacher/<username>', methods=['GET'])
def get_teacher(username):
    teacher = Teacher.query.get(username)
    return t_schema.jsonify(teacher)


# Delete Teacher
@app.route('/teacher/<username>', methods=['DELETE'])
def delete_teacher(username):
    teacher = Teacher.query.get(username)
    db.session.delete(teacher)
    db.session.commit()
    return t_schema.jsonify(teacher)

#Dashboard Routes For Teacher
@app.route("/teacherdashboard",methods=['GET'])
def dashboard():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("t_dashboard.html",name = uname)

@app.route("/addcourse",methods=['GET'])
def addourse():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("addcourse.html")

@app.route("/addcourse",methods=['POST'])
def addc():
    cid = request.form.get('courseid')
    cname = request.form.get('coursename')
    sem = request.form.get('semester')
    credit = request.form.get('credit')

    course = Course.query.filter_by(courseid=cid).first()  # if this returns a user, then the course already exists in database

    if course: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Course already exists, Try again')
        return render_template('addcourse.html')
    
    new_course = Course(cid, cname,sem,credit,0)
    db.session.add(new_course)
    db.session.commit()

    return redirect('/teacherdashboard')

@app.route("/editcourse",methods=['GET'])
def editc():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("editcourse.html")

@app.route("/editcourse",methods=['POST'])
def editcp():
    cid = request.form.get('courseid')
    ucname = request.form.get('coursename')
    usem = request.form.get('semester')
    ucredit = request.form.get('credit')

    course = Course.query.filter_by(courseid=cid).first()

    # check if the user actually exists
    if not course:
        flash('Course not found! Try Again!')
        return render_template('editcourse.html') # if the user doesn't exist or password is wrong, reload the page
    else:
        course = Course.query.get(cid)
        course.coursename=ucname
        course.semester=usem
        course.credit = ucredit
        db.session.commit()
        return redirect('/teacherdashboard')


@app.route("/delcourse",methods=['GET'])
def delc():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("delcourse.html")

@app.route("/delcourse",methods=['POST'])
def delcp():
    cid = request.form.get('courseid')
    cidr =  request.form.get('courseidr')

    if cid != cidr:
        flash('Please confirm the Course Id correctly!')
        return render_template('delcourse.html') 

    course = Course.query.filter_by(courseid=cid).first()
    if not course:
        flash('Course not found! Try Again!')
        return render_template('delcourse.html') # if the user doesn't exist or password is wrong, reload the page
    else:
        db.session.delete(course)
        db.session.commit()
        return redirect('/teacherdashboard')


@app.route("/viewcourse", methods=['GET'])
def viewc():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        all_cs = Course.query.all()
        result = courses_schema.dump(all_cs)
        return render_template("viewcourse.html",value = result)


#Quiz Portal Routes for Teacher

@app.route("/quizdashboard",methods=['GET'])
def quiz_dashboard():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("quizdashboard.html")

@app.route("/addques",methods=['GET'])
def addques():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("addques.html")

@app.route("/addques",methods= ['POST'])
def addquesp():
    cid = request.form.get('courseid')
    qid = request.form.get('quesid')
    ques = request.form.get('ques')
    op1 = request.form.get('op1')
    op2 = request.form.get('op2')
    op3 = request.form.get('op3')
    ans = request.form.get('ans')
    marks = request.form.get('marks')

    course = Course.query.filter_by(courseid=cid).first()  # if this returns a user, then the course already exists in database
    ques = Question.query.filter_by(cid=cid, qid = qid).first() # ques for specicif course

    if not course: # if course is not found
        flash('Course does not exist, Try again')
        return render_template('addques.html')

    if ques:
        flash('Quesid for this Course already exist, Try again')
        return render_template('addques.html')
        
    else:
        new_ques = Question(cid, qid,ques,op1,op2,op3,ans,marks)
        db.session.add(new_ques)
        db.session.commit()
        return redirect('/quizdashboard')

@app.route("/editques",methods=['GET'])
def editques():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("editques.html")

@app.route("/editques",methods=['POST'])
def editquesp():
    cid = request.form.get('courseid')
    qid = request.form.get('quesid')
    uques = request.form.get('ques')
    uop1 = request.form.get('op1')
    uop2 = request.form.get('op2')
    uop3 = request.form.get('op3')
    uans = request.form.get('ans')
    umarks = request.form.get('marks')

    ques = Question.query.filter_by(cid=cid, qid = qid).first()

    if not ques:
        flash('Quesid for this Course does not exist, Try again')
        return render_template('editques.html')

    else:
        question = Question.query.get(cid,qid)
        question.ques=uques
        question.op1=uop1
        question.op2 = uop2
        question.op3 = uop3
        question.ans = uans
        question.marks = umarks
        db.session.commit()
        return redirect('/quizdashboard')

@app.route("/delques",methods=['GET'])
def delques():
    uname = session['username']
    if uname == None:
        return redirect('/')
    else:
        return render_template("delques.html")

@app.route("/delques",methods=['POST'])
def delquesp():
    cid = request.form.get('courseid')
    qid = request.form.get('quesid')

    ques = Question.query.filter_by(cid=cid, qid = qid).first() # ques for specicif course

    if not ques:
        flash('Quesid for this Course does not exist, Try again')
        return render_template('delques.html')

    else:
        db.session.delete(ques)
        db.session.commit()
        return redirect('/quizdashboard')



if __name__ == '__main__':
    app.run(debug= True)