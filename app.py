from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
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
    #notes = db.relationship('Notes', backref='author', lazy = True)

    def __repr__(self):
        return f"Person('{self.username}', '{self.email}')"



@app.route('/')
@app.route('/home')
def home():
    pagename = 'home'
    return render_template('home.html', pagename = pagename)

@app.route('/index')
def index():
    pagename = 'index'
    return render_template('index.html',pagename = pagename)

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
        return render_template('login.html')
    else:
        username = request.form['Username']
        password= request.form['Password']
        user = users.query.filter_by(username = username).first()
        if not user or not bcrypt.check_password_hash(user.password,password):
            flash('Please check your login details', 'error')
            return render_template('login.html')
        else:
            session['name']=username
            return redirect(url_for('index'))



def add_users(reg_details):
    user = users(username = reg_details[0], email = reg_details[1], firstName = reg_details[2], lastName=reg_details[3],  password = reg_details[4], type = reg_details[5])
    db.session.add(user)
    db.session.commit()
if __name__ == '__main__':
    app.run(debug=True)

