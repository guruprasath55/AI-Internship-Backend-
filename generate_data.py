import random
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your database Models from main.py
from main import Student, Attendance, Batch, Base

# Connect to your local MySQL database (Using your root user password)
# TODO: Replace 'YOUR_PASSWORD' with your actual MySQL Workbench password!
DATABASE_URL = "mysql+pymysql://root:guru5527@localhost:3306/internship_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

fake = Faker()

def seed_large_dataset():
    # 1. Fetch existing batches from the DB to link students properly
    batches = db.query(Batch).all()
    if not batches:
        print("Please run your main backend once first to create batches!")
        return
    
    batch_ids = [b.id for b in batches]
    
    print("Generating 100 random student and attendance records...")
    
    for i in range(100):
        # Generate realistic names, random batches, and random attendance percentages
        random_name = fake.name()
        random_batch = random.choice(batch_ids)
        random_percentage = round(random.uniform(50.0, 100.0), 1)
        
        # Create student record
        student = Student(
            name=random_name, 
            batch_id=random_batch, 
            attendance_percentage=random_percentage
        )
        db.add(student)
        db.commit() # Save to database to generate the student.id
        
        # Create matching attendance logs (e.g., 5 random daily records per student)
        for _ in range(5):
            status = random.choice(["Present", "Present", "Present", "Absent"]) # 75% chance present
            attendance_record = Attendance(student_id=student.id, status=status)
            db.add(attendance_record)
            
    db.commit()
    print("Successfully populated database with 100 mock students!")

if __name__ == "__main__":
    seed_large_dataset()