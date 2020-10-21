from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
#from flask_mail import Mail
import math

with open("config.json",'r') as c:
    params=json.load(c)['params']

local_server=True

app=Flask(__name__)  #object initialization

app.secret_key = "super-secret-key"

"""app.config.update(

    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD= params['gmail_pass']
)
mail=Mail(app)"""



if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']   #'mysql://root:@localhost/flask'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db=SQLAlchemy(app)

class Contacts(db.Model):

    '''contact database attributes..
        name,email,phone_num,msg,date
    '''

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num= db.Column(db.String(12), unique=False, nullable=False)
    msg= db.Column(db.String(120), unique=False, nullable=False)
    date= db.Column(db.String(12), unique=False, nullable=True)

class Posts(db.Model):

    '''Posts database attributes..
        sno,title,tagline,slug,content,date
    '''

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=False, nullable=False)
    tagline = db.Column(db.String(20), unique=False, nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(200), unique=False, nullable=False)
    date= db.Column(db.String(12), unique=False, nullable=True)
    img_file= db.Column(db.String(12), unique=False, nullable=True)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()       #[0:params['no_of_posts']]
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    '''pagination logic will be divided into 3'''
    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page=int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    ''' 1- Either on the first page
         a- prev=#
         b- next=page+1 '''
    if page==1:
        prev="#"
        next="/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)

    ''' 2- Middle page
             a- prev=page-1
             b- next=page+1'''

    ''' 3- last page
            a- prev=page-1
            b- next=# '''


    return (render_template("index.html", params = params,posts=posts,prev=prev,next=next))

@app.route("/dashboard",methods=['GET','POST'])
def login():
    #if user is already there code.
    if ('user' in session and session['user'] == params['Admin_user']):
        posts=Posts.query.all()
        return (render_template("dashboard.html", params=params,posts=posts))

    if request.method=='POST':
        #redirect to admin panel
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username==params['Admin_user'] and userpass==params['Admin_pass']):
            #set the session variable
            session['user'] = username
            posts=Posts.query.all()
            return (render_template("dashboard.html", params=params,posts=posts))

    return (render_template("login.html", params=params))

@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user']==params['Admin_user']):
        if request.method=="POST":
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')

            if sno==0:
                post=Posts(title=box_title,tagline=tline,slug=slug,content=content,
                           date=datetime.now(),img_file=img_file)
                db.session.add(post)
                db.session.commit()
                #return render_template("")

            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.tagline=tline
                post.slug=slug
                post.img_file=img_file
                post.date=datetime.now()
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template("edit.html",params=params,post=post,sno=sno)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/dashboard")

@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user']==params['Admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/about")
def about():
    return (render_template("about.html",params=params))

@app.route("/Internship")
def internships():
    return(render_template("internship.html",params=params))

@app.route("/project")
def project():
    return (render_template("youtube.html",params=params))

@app.route("/Doodles")
def doodle():
    return (render_template("doodle.html",params=params))

@app.route('/contact', methods=["GET","POST"])
def contact():
    if request.method=='POST':
        '''add entry to database (fetching from the html page)'''
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        msg=request.form.get('message')

        ''' now entry to database
        name, email, phone_num, msg, date
        '''
        entry=Contacts(name=name,email=email,phone_num=phone,
                       msg=msg,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        """mail.send_message("New Message from blog", sender=email,
                          recipients=params["gmail_user"],
                          body=msg + "\n")"""

    return(render_template('contact.html', params = params))


@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()

    return (render_template('post.html', params = params,post=post))


if __name__=="__main__":
    app.run(debug=True,port=8080)
    