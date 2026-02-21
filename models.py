from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Teachers, Class Teachers, and HODs"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'subject_teacher', 'class_teacher', 'hod'
    name = db.Column(db.String(100))

    # Relationship to find which subjects this user teaches
    subjects_taught = db.relationship('Subject', backref='teacher', lazy=True)
    # Relationship to find which class this user leads (if any)
    class_led = db.relationship('Class', backref='class_teacher', uselist=False)

class Class(db.Model):
    """The Classroom (e.g., SE-DS, AIML-A)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Links the Class to its Class Teacher (HOD can see all)
    class_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    students = db.relationship('Student', backref='classroom', lazy=True)
    subjects = db.relationship('Subject', backref='classroom', lazy=True)

class Subject(db.Model):
    """Specific subjects within a class"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Student(db.Model):
    """Student basic info"""
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    
    performance_records = db.relationship('Performance', backref='student', lazy=True)

class Performance(db.Model):
    """The actual data points for analysis"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    attendance = db.Column(db.Integer, default=0) # Numerical count
    ut1_marks = db.Column(db.Float, default=0.0)
    ut2_marks = db.Column(db.Float, default=0.0)
    sem_marks = db.Column(db.Float, default=0.0)