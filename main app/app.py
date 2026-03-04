from flask import Flask
from models import db, User, Class, Subject, Student, Performance
from flask import request, jsonify
import uuid
import requests

app = Flask(__name__)

# 1. Configuration - Set the database location
# This creates 'students.db' in a folder named 'instance'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# 2. Initialize the database with the app
db.init_app(app)

# 3. Create the Database Tables
# This block checks if the database exists; if not, it creates it.
with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")

# 4. Basic Route to test the setup
@app.route('/')
def home():
     # Fetch all users from the database
    users = User.query.all()
    
    # Create a simple string to display them
    user_list = "<br>".join([f"{u.name} - Role: {u.role} (Username: {u.username})" for u in users])
    
    return f"<h1>Database Content:</h1><p>{user_list}</p>"

@app.route('/dashboard')
def dashboard():
    # Performance.query.all() pulls all synced data
    records = Performance.query.all()
    return render_template('dashboard.html', records=records)

@app.route('/analytics')
def analytics():
    # Force the database to check for new data
    db.session.expire_all() 
    records = Performance.query.all()
    return render_template('analytics.html', records=records)

@app.route('/api/sync', methods=['POST'])
def receive_sync():
    data = request.get_json(force=True)
    s_name = data.get('student_name', '').strip()
    sub_name = data.get('subject_name', '').strip()

    try:
        # 1. ENSURE A TEACHER EXISTS (Required for Subject)
        teacher = User.query.filter_by(role='subject_teacher').first()
        if not teacher:
            teacher = User(username="auto_teacher", password="pbkdf2:sha256:...", role="subject_teacher")
            db.session.add(teacher)
            db.session.commit()

        # 2. ENSURE A CLASS EXISTS (Required for Student and Subject)
        cls = Class.query.first()
        if not cls:
            cls = Class(name="Auto Class", class_teacher_id=teacher.id)
            db.session.add(cls)
            db.session.commit()

        # 3. GET OR CREATE STUDENT
        student = Student.query.filter_by(name=s_name).first()
        if not student:
            student = Student(name=s_name, roll_no=str(uuid.uuid4())[:8], class_id=cls.id)
            db.session.add(student)
            db.session.commit()

        # 4. GET OR CREATE SUBJECT (Linked to Teacher and Class)
        subject = Subject.query.filter_by(name=sub_name).first()
        if not subject:
            subject = Subject(name=sub_name, class_id=cls.id, teacher_id=teacher.id)
            db.session.add(subject)
            db.session.commit()

        # 5. SAVE PERFORMANCE
        perf = Performance.query.filter_by(student_id=student.id, subject_id=subject.id).first()
        if not perf:
            perf = Performance(student_id=student.id, subject_id=subject.id)
            db.session.add(perf)

        perf.attendance = int(data.get('attendance', 0))
        perf.ut1_marks = int(data.get('ut_marks', 0))
        perf.sem_marks = int(data.get('sem_marks', 0))
        
        db.session.commit()
        print(f"✅ SYNC SUCCESS: {s_name}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ DATABASE REJECTED: {str(e)}")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    # Run in debug mode so it restarts automatically when you save changes
    app.run(debug=True)