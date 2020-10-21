from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

# Create a Teacher
@app.route('/teacher', methods=['POST'])
def add_teacher():

    usernamef = request.form.get('username')
    namef = request.form.get('name')
    passwordf = request.form.get('password')
    
    new_teacher = Teacher(usernamef, namef, passwordf)

    db.session.add(new_teacher)
    db.session.commit()

    return render_template('login.html')

# Get All Teachers
@app.route('/teacher', methods=['GET'])
def get_teachers():
    all_teachers = Teacher.query.all()
    result = ts_schema.dump(all_teachers)
    return jsonify(result)

# Get Single Teacher
@app.route('/teacher/<username>', methods=['GET'])
def get_teacher(username):
    teacher = Teacher.query.get(username)
    return t_schema.jsonify(teacher)

if __name__ == '__main__':
    app.run(debug= True)