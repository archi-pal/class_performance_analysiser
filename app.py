import os
from flask import Flask, render_template
from models import db, User, Class, Subject  # Importing from your models.py

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
    

if __name__ == '__main__':
    # Run in debug mode so it restarts automatically when you save changes
    app.run(debug=True)