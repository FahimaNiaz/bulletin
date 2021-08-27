from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://fniaz:pjoforever@cluster0.j1zlv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = client.get_database('userdata')
records = db.userids
record2= db.posts

@app.route("/", methods=['post','get'])
def home():
    log='/'
    if "username" in session:
        log="/home"
        return render_template('base.html', log=log)
    return render_template('base.html', log=log)


@app.route("/home", methods=['post','get'])
def loghome():
    return render_template('home.html')


@app.route("/register", methods=['post', 'get'])
def index():
    message = 'Please register'
    if "username" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_found = records.find_one({"username": user})
        email_found = records.find_one({"email": email})
        if email=='':
            message = 'enter an email'
            return render_template('index.html', message=message)
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'username': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            user_data = records.find_one({"username": user})
            new_user= user_data['username']
            message='account created successfully! Please go to the login page to access your account'
            return render_template('index.html', message=message)
    return render_template('index.html', message=message)



@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "username" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        user_found = records.find_one({"username": user})
        if user_found:
            user_val = user_found['username']
            passwordcheck = user_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["username"] = user_val
                return redirect(url_for('logged_in'))
            else:
                if "username" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'User not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "username" in session:
        user = session["username"]
        num=db.posts.find({"name" : user}).count();
        return render_template('logged_in.html', username=user, num=num)
    else:
        return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "username" in session:
        session.pop("username", None)
        return render_template("base.html",log='/')
    else:
        return render_template('login.html')

@app.route ( '/post', methods=['POST', 'GET']) 
def  add_entry():
    if "username" in session:
        message = 'Write a post'
        if request.method == "POST":
            name=session["username"]
            title=request.form.get("title")
            content=request.form.get("body")
            posted_on=datetime.utcnow()
            user_input = {'name':name, 'title': title, 'content': content, 'posted_on': posted_on}
            record2.insert_one(user_input)
            return redirect(url_for('user_view'))
    else:
        message = ''
    return render_template('post.html', message=message)

@app.route('/allposts')
def all_post():
    allp=db.posts.find()
    return render_template('allposts.html', posts=allp)

@app.route('/apuser')
def user_view():
    allp=db.posts.find()
    return render_template('apuser.html', posts=allp)



@app.route('/<title>')
def post(title):
    log='/'
    a='/allposts'
    post = db.posts.find_one({'title':title})
    if "username" in session:
        log='/home'
        a='/apuser'
        return render_template('a.html', post=post, log=log,a=a)
    return render_template('a.html', post=post, log=log,a=a)


if __name__ == "__main__":
  app.run(debug=True)
