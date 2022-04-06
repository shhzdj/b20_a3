from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '"\x88\x80\xc1\xact\x07\xa7d\xc8\xa5G\x0e\xf0{y'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 1)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable = False)
    firstName = db.Column(db.String(20), nullable = False)
    lastName = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)
    type = db.Column(db.String(20), nullable = False)
    #feedback = db.relationship('feedback', backref='author', lazy = True)

    def __repr__(self):
        return f"Person('{self.username}', '{self.email}')"

class feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key = True)
    feedback = db.Column(db.String(1000), primary_key = True, nullable = False)

    def __repr__(self):
        return f"feedback('{self.id}', '{self.feedback}')"

@app.route('/')
@app.route('/home')
def home():
    pagename = 'home'
    return render_template('home.html', pagename = pagename)

@app.route('/index')
def index():
    pagename = 'index'
    return render_template('index.html',pagename = pagename)

@app.route('/account')
def account():
    pagename = 'account'
    return render_template('account.html',pagename = pagename)

app.route('/logout')
def logout():
    session.pop('name', default=None)
    session.clear('name', default=None)
    return redirect(url_for('home'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['Username']
        email = request.form['Email']
        firstName = request.form['Firstname']
        lastName = request.form['Lastname']
        hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        type = request.form['Option']
        reg_details = [
            username,
            email,
            firstName,
            lastName,
            hashed_password,
            type
        ]
        add_users(reg_details)
        return redirect(url_for('login'))
        
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'name' in session:
            flash("already logged in")
            return redirect(url_for('account'))
        else:
            return render_template('login.html')
    else:
        username = request.form['Username']
        password= request.form['Password']
        user = users.query.filter_by(username = username).first()
        
        if not user or not bcrypt.check_password_hash(user.password,password):
            
            flash('Please check your login details!', 'error')
            return render_template('login.html')
        else:
            role = user.type
            session['name']=username
            session['role']=role
            session.permanent = True
            return redirect(url_for('account'))




@app.route('/feedback', methods = ['GET', 'POST'])
def enter_feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
    else:
        

        #username = request.form['Username']
        #feedback = request.form['Feedback']
        #user = users.query.filter_by(username = username)
        #if not user or user.usertype != 'instructor':
           # flash('Please enter a vald instructor username')
           ## return render_template('feedback.html')
       # else:
        #feedback_details = [
        #    username,
        #    feedback
       # ]
       username = request.form['Username']
      
       person = users.query.filter_by(username = username).first()
       if person:
           person_id = person.id
       
       feedback = request.form['Feedback']
       feedback_details =[ 
           
           person_id,
           feedback]
            
       
       add_feedback(feedback_details)
       return redirect(url_for('enter_feedback'))



def add_feedback(feedback_details):
    anon_feedback = feedback(id = feedback_details[0], feedback = feedback_details[1])
    db.session.add(anon_feedback)
    db.session.commit()


def add_users(reg_details):
    user = users(username = reg_details[0], email = reg_details[1], firstName = reg_details[2], lastName=reg_details[3],  password = reg_details[4], type = reg_details[5])
    db.session.add(user)
    db.session.commit()
if __name__ == '__main__':
    app.run(debug=True)

