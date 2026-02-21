from app import app
from models import db, User, Class, Subject, Student

def seed_database():
    with app.app_context():
        # 1. Clear existing data to start fresh
        db.drop_all()
        db.create_all()

        # 2. Create 1 HOD
        hod = User(username="hod_admin", password="password123", role="hod", name="Dr. Sharma")
        db.session.add(hod)

        # 3. Create 3 Classes and 3 Class Teachers
        classes = []
        for i in range(1, 4):
            ct = User(
                username=f"ct_user{i}", 
                password="password123", 
                role="class_teacher", 
                name=f"Class Teacher {i}"
            )
            db.session.add(ct)
            db.session.commit() # Commit to get the ID for the foreign key
            
            new_class = Class(name=f"Class {i}_Section A", class_teacher_id=ct.id)
            db.session.add(new_class)
            classes.append(new_class)
        
        db.session.commit()

        # 4. Create 12 Subject Teachers and assign 4 subjects per class
        # (Total 12 subjects across 3 classes)
        subject_names = ["Mathematics", "Physics", "Data Structures", "Operating Systems"]
        
        teacher_count = 1
        for cls in classes:
            for sub_name in subject_names:
                st = User(
                    username=f"teacher_{teacher_count}", 
                    password="password123", 
                    role="subject_teacher", 
                    name=f"Prof. Smith {teacher_count}"
                )
                db.session.add(st)
                db.session.commit()
                
                new_subject = Subject(name=sub_name, class_id=cls.id, teacher_id=st.id)
                db.session.add(new_subject)
                teacher_count += 1

        # 5. Add 5 Dummy Students to the first class for testing
        for j in range(1, 6):
            std = Student(roll_no=f"2026_00{j}", name=f"Student Name {j}", class_id=classes[0].id)
            db.session.add(std)

        db.session.commit()
        print("Database Seeded Successfully!")

if __name__ == '__main__':
    seed_database()