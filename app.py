from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '"\x88\x80\xc1\xact\x07\xa7d\xc8\xa5G\x0e\xf0{y'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes= 15)
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
    
class Marks(db.Model):
    __tablename__ = 'Marks'
    id = db.Column(db.Integer,nullable = False, primary_key = True)
    A1 = db.Column(db.Integer)
    A2 = db.Column(db.Integer)
    A3 = db.Column(db.Integer)
    Midterm = db.Column(db.Integer)
    Tut = db.Column(db.Integer)
    final = db.Column(db.Integer)
    overall = db.Column(db.Integer)

    #website_data = db.relationship('users', backref = 'student', lazy = True)

    
    def __repr__(self):
        return f"Marks ('{self.id}', '{self.A1}', '{self.A2}', '{self.A3}', '{self.Midterm}', '{self.Tut}','{self.final}', '{self.overall}')"
    
class Remark(db.Model):
    __tablename__ = 'Remark'
    id = db.Column(db.Integer,nullable = False, primary_key = True)
    assessment = db.Column(db.Text, nullable = False, primary_key = True)
    remark = db.Column(db.Text)
    status = db.Column(db.Text)

    
    def __repr__(self):
        return f"Remark ('{self.id}', '{self.assessment}', '{self.remark}', '{self.status}')"

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
        flash('you have successfully registered!')
        return redirect(url_for('login'))
        
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'name' in session:
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
            firstn = user.firstName
            lastn=user.lastName
            session['name']=username
            session['role']= role
            session['first'] = firstn
            session['last'] = lastn
            session.permanent = True
            return redirect(url_for('account'))


@app.route('/logout')
def logout():
    session.pop('name', default = None)
    return redirect(url_for('home'))

@app.route('/Assignments')
def assignments():
    pagename = 'Assignments'
    return render_template('Assignments.html',pagename = pagename)

@app.route('/calendar')
def calendar():
    pagename = 'calendar'
    return render_template('calendar.html',pagename = pagename)

@app.route('/labs')
def labs():
    pagename = 'labs'
    return render_template('labs.html',pagename = pagename)

@app.route('/lectures')
def lectures():
    pagename = 'lectures'
    return render_template('lectures.html',pagename = pagename)

@app.route('/announcements')
def announcements():
    pagename = 'announcements'
    return render_template('announcements.html',pagename = pagename)

@app.route('/resources')
def resources():
    pagename = 'resources'
    return render_template('resources.html',pagename = pagename)

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

@app.route('/student_grades', methods = ['GET', 'POST'])
def student_grades():
    if request.method == 'GET':
        query_grades_result = query_student_grades()
        return render_template('student_grades.html', query_grades_result = query_grades_result )
    else:
        assessment = request.form['Assessment']
        reason = request.form['Reason']
        if not hasattr(Marks, assessment):
            flash('Please enter a valid assessment')
            return render_template('student_grades.html')
        else:
            remark_details = [
                assessment,
                reason
            ]
            add_remark(remark_details)
            return render_template('student_grades.html')

def add_remark(remark_details):
    username = session['name']
    student = users.query.filter_by(username = username).first()
    student_id = student.id
    remark_request = Remark(id = student_id, assessment = remark_details[0], remark = remark_details[1])
    db.session.add(remark_request)
    db.session.commit()

def query_student_grades():
    username = session['name']
    student = users.query.filter_by(username = username).first()
    student_id = student.id
    query_grades = Marks.query.filter_by(id = student_id)
    #return student
    return query_grades

def add_users(reg_details):
    user = users(username = reg_details[0], email = reg_details[1], firstName = reg_details[2], lastName=reg_details[3],  password = reg_details[4], type = reg_details[5])
    db.session.add(user)
    db.session.commit()


#

@app.route('/grades', methods = ['GET', 'POST'])
def grades():
    if request.method == 'GET':
        query_grades_result = query_grades()
        return render_template('grades.html', query_grades_result = query_grades_result )

def query_grades():
    query_grades = Marks.query.all()
    return query_grades

#Instructor adding student grades
@app.route('/addGrades', methods = ['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('addGrades.html')
    else:
        grade_details =(
            request.form['StudentID'],
            request.form['A1_Mark'],
            request.form['A2_Mark'],
            request.form['A3_Mark'],
            request.form['Midterm_Mark'],
            request.form['Tut_Mark'],
            request.form['Final_Mark'],
            request.form['OverallGrade']
            

        )
        Studentid = request.form['StudentID']
        student = users.query.filter_by(id = Studentid).first()
        if not student :
            flash('There is no student with this id in your class. Please try again', 'error')
            query_grades_result = query_grades()
            return render_template('grades.html', query_grades_result = query_grades_result)
        else:

            add_grades(grade_details)
            return render_template('addGradeSuccess.html')



def add_grades(grade_details):
     
    student = users.query.filter_by(id = grade_details[0]).first()
    #Studentgrades = Marks(id = grade_details[0], A1 = grade_details[1], A2 = grade_details[2], A3 = grade_details[3], Midterm = grade_details[4], Tut = grade_details[5], final = grade_details[6], overall = grade_details[7])
    studentgrade = Marks.query.filter_by(id = student.id).first()
    studentgrade.A1 =  grade_details[1]
    db.session.commit()
    studentgrade.A2 =  grade_details[2]
    db.session.commit()
    studentgrade.A3  = grade_details[3]
    db.session.commit()
    studentgrade.Midterm = grade_details[4]
    db.session.commit()
    studentgrade.Tut = grade_details[5]
    db.session.commit()
    studentgrade.overall = grade_details[6]
    db.session.commit()
    studentgrade.final = grade_details[7]
    db.session.commit()

   
    db.session.commit()


#instructor seeing student feedback
@app.route('/instructorFeedback', methods = ['GET', 'POST'])
def inst_feedback():
    if request.method == 'GET':
        query_inst_feedback_result = query_inst_feedback()
        return render_template('instructorFeedback.html', query_inst_feedback_result = query_inst_feedback_result )


def query_inst_feedback():
    username = session['name']
    instructor = users.query.filter_by(username = username).first()
    instructor_id = instructor.id
    query_inst_feedback = feedback.query.filter_by(id = instructor_id)
    return query_inst_feedback

#instructor seeing all student remark requests
@app.route('/RemarkRequest', methods = ['GET', 'POST'])
def RemarkRequest():
    if request.method == 'GET':
        query_remark_result = query_remark_requests()
        return render_template('remarkInstructor.html', query_remark_result = query_remark_result )

def query_remark_requests():
    query_remark_requests = Remark.query.all()
    return query_remark_requests

#instructor updating scores for remark
@app.route('/RemarkAction', methods = ['GET', 'POST'])
def remark():
    if request.method == 'GET':
        return render_template('RemarkAction.html')
    else:
        grade_details =(
            request.form['StudentID'],
            request.form['Assessment'],
            request.form['UpdatedMark'],
            request.form['status']
        )

        Studentid = request.form['StudentID']
        student = users.query.filter_by(id = Studentid).first()
        if not student :
            flash('There is no student with this id in your class. Please try again', 'error')
            query_remark_result = query_remark_requests()
            return render_template('remarkInstructor.html', query_remark_result = query_remark_result)
        else:
            change_grades(grade_details)
            return render_template('RegradeSuccessful.html')



def change_grades(grade_details):
    
    student = Marks.query.filter_by(id = grade_details[0]).first()
    assesment = grade_details[1]
    regradeStatus = grade_details[3]
    
    if assesment == 'A1':
        StudentRegrade = Remark.query.filter_by(id = grade_details[0] , assessment = "grade_details[1]")

        # StudentRegradeStatus = StudentRegrade.filter_by(assessment == str(grade_details[1]))
        StudentRegrade.status = regradeStatus
        student.A1 = grade_details[2]
        db.session.commit()
    elif assesment == 'A2':
        student.A2 = grade_details[2]
        db.session.commit()
    elif assesment == 'A3':
        student.A3 = grade_details[2]
        db.session.commit()
    elif assesment == 'Midterm':
        student.Midterm = grade_details[2]
        db.session.commit()
    elif assesment == 'Tut':
        student.Tut = grade_details[2]
        db.session.commit()
    elif assesment == 'final':
        student.final = grade_details[2]
        db.session.commit()
    else:
        student.overall = grade_details[2]
        db.session.commit()

   
    StudentRegrade = Remark.query.filter_by(id = grade_details[0] , assessment = "grade_details[1]")

   # StudentRegradeStatus = StudentRegrade.filter_by(assessment == str(grade_details[1]))
    StudentRegrade.status = regradeStatus
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)


