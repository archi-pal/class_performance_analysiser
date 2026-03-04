from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.secret_key = "formula1_ds_secret"

# 1. DATABASE CONFIGURATION
# This creates a file named 'erp_database.db' in your folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///erp_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. DATABASE MODELS (Tables)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False) # HOD, Class Teacher, Subject Teacher
    subject = db.Column(db.String(50)) # e.g., 'Data Science'

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    attendance = db.Column(db.Integer)
    ut_marks = db.Column(db.Integer)
    sem_marks = db.Column(db.Integer)
    subject = db.Column(db.String(50))

# Create the database and dummy users
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='omkar').first():
        u1 = User(username='omkar', password='123', role='Subject Teacher', subject='Data Science')
        u2 = User(username='hod_sir', password='admin', role='HOD', subject='All')
        db.session.add_all([u1, u2])
        db.session.commit()

# 3. ROUTES
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    uname = request.form.get('username')
    pword = request.form.get('password')
    user = User.query.filter_by(username=uname, password=pword).first()
    
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['subject'] = user.subject
        return redirect(url_for('dashboard'))
    return "Invalid Credentials!"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: 
        return redirect(url_for('index'))
    
    # Define subjects based on role
    if session['role'] == 'HOD':
        subjects = ['Data Science', 'AIML', 'Networking', 'Python']
    else:
        subjects = [session['subject']]
        
    # FIX: We use 'session' here because we stored the user info there during login
    return render_template('dashboard.html', subjects=subjects)

# ADD THIS NEW ROUTE to see your saved data on screen
@app.route('/view_data')
def view_data():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    # This line queries the database for all records
    records = Performance.query.all()
    return render_template('view_data.html', records=records)

@app.route('/input/<sub_name>')
def input_page(sub_name):
    return render_template('input.html', subject=sub_name)

@app.route('/submit', methods=['POST'])
def submit():
    # 1. Capture the data from your form
    s_name = request.form.get('student_name')
    att = request.form.get('attendance')
    ut = request.form.get('ut_marks')
    sem = request.form.get('sem_marks')
    sub = request.form.get('subject')

    # 2. Save to LOCAL Dummy ERP database (so it shows in /view_data)
    try:
        new_entry = Performance(
            student_name=s_name,
            attendance=att,
            ut_marks=ut,
            sem_marks=sem,
            subject=sub
        )
        db.session.add(new_entry)
        db.session.commit()
        print(f"✔ Saved locally: {s_name}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Local DB Error: {e}")

    # 3. SEND TO MAIN APP ON PORT 5001
    sync_payload = {
        "student_name": s_name,
        "attendance": att,
        "ut_marks": ut,
        "sem_marks": sem,
        "subject_name": sub
    }

    try:
        # We send to 5001 because that's where your Main App is
        response = requests.post("http://127.0.0.1:5001/api/sync", json=sync_payload, timeout=2)
        if response.status_code == 200:
            print(f"✅ SUCCESSFULLY SYNCED TO MAIN APP (5001)")
        else:
            print(f"⚠ Main App received but rejected data: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: Main App on 5001 might be closed. ({e})")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)