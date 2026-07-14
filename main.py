import os
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"
import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd

# 1. Database Configuration (Update credentials if needed)
DATABASE_URL = "mysql+pymysql://root:guru5527@localhost:3306/internship_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. SQLAlchemy Models
class Mentor(Base):
    __tablename__ = "mentors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))

class Batch(Base):
    __tablename__ = "batches"
    id = Column(String(50), primary_key=True) # e.g., 'Batch A'
    mentor_id = Column(Integer, ForeignKey("mentors.id"))

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    batch_id = Column(String(50), ForeignKey("batches.id"))
    attendance_percentage = Column(Float, default=100.0)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(Date, default=datetime.date.today)
    status = Column(String(10), default="Present") # 'Present' or 'Absent'

# Create tables in the MySQL database
Base.metadata.create_all(bind=engine)

# 3. Dependency to get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. FastAPI Application Setup
app = FastAPI(title="AI Internship Management System Backend")

# Enable CORS so your frontend dashboard can fetch the data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Data Seeding Script (Populates DB to match the dashboard image numbers)
# 5. Data Seeding Script (Populates DB to match the dashboard image numbers)
def seed_data_if_empty(db):
    # 1. Check if data already exists
    if db.query(Mentor).count() > 0:
        return  # Database already has data, skip seeding

    print("Seeding database...")

    # 2. SEED MENTORS FIRST (This fixes the foreign key crash!)
    # Adjust names/fields if your Mentor model has different columns
    mentor1 = Mentor(id=1, name="Dr. Smith")
    db.add(mentor1)
    db.commit() # This saves the mentor to the database immediately

    # 3. SEED BATCHES SECOND (Now mentor_id=1 exists!)
    batch_a = Batch(id="Batch A", mentor_id=1)
    batch_b = Batch(id="Batch B", mentor_id=1)
    batch_c = Batch(id="Batch C", mentor_id=1)
    batch_d = Batch(id="Batch D", mentor_id=1)
    
    db.add_all([batch_a, batch_b, batch_c, batch_d])
    db.commit()

    # 4. SEED YOUR STUDENTS AND ATTENDANCE NEXT
    # (Paste your existing Student and Attendance seeding logic right here)
# 4. SEED YOUR STUDENTS AND ATTENDANCE NEXT
    # Creating sample students connected to the batches
    student1 = Student(name="Rahul Sharma", batch_id="Batch A", attendance_percentage=100.0)
    student2 = Student(name="Priya Patel", batch_id="Batch A", attendance_percentage=85.5)
    student3 = Student(name="Amit Kumar", batch_id="Batch B", attendance_percentage=78.0)
    student4 = Student(name="Sneha Reddy", batch_id="Batch C", attendance_percentage=92.0)
    
    db.add_all([student1, student2, student3, student4])
    db.commit() # Saves the student records with their auto-generated IDs

    # Creating matching attendance history records to compute averages
    att1 = Attendance(student_id=student1.id, status="Present")
    att2 = Attendance(student_id=student2.id, status="Present")
    att3 = Attendance(student_id=student3.id, status="Absent")
    att4 = Attendance(student_id=student4.id, status="Present")
    
    db.add_all([att1, att2, att3, att4])
    db.commit()

    print("Database seeding completed successfully!")
    
# Run seeding routine
db_session = SessionLocal()
seed_data_if_empty(db_session)
db_session.close()

# 6. Dashboard Core API Endpoint
@app.get("/api/dashboard")
def get_dashboard_data():
    db = SessionLocal()
    try:
        # 1. Total Counts
        total_students = db.query(Student).count()
        total_mentors = db.query(Mentor).count()
        total_batches = db.query(Batch).count()
        
        # 2. Attendance Stats
        total_attendance_records = db.query(Attendance).count()
        present_count = db.query(Attendance).filter(Attendance.status == "Present").count()
        
        if total_attendance_records > 0:
            avg_attendance = round((present_count / total_attendance_records) * 100, 1)
        else:
            avg_attendance = 0.0

        # 3. Batch Wise Attendance Breakdown
        batches = db.query(Batch).all()
        batch_wise_data = []
        for b in batches:
            # Count students in this batch
            b_students = db.query(Student).filter(Student.batch_id == b.id).all()
            b_student_ids = [s.id for s in b_students]
            
            # Calculate average for this batch
            if b_student_ids:
                b_att_records = db.query(Attendance).filter(Attendance.student_id.in_(b_student_ids)).count()
                b_present = db.query(Attendance).filter(Attendance.student_id.in_(b_student_ids), Attendance.status == "Present").count()
                b_avg = round((b_present / b_att_records) * 100, 1) if b_att_records > 0 else 0.0
            else:
                b_avg = 0.0
                
            batch_wise_data.append({
                "batch_id": b.id,
                "average_attendance": b_avg
            })

        # 4. Top 5 Students
        top_students_query = db.query(Student).order_by(Student.attendance_percentage.desc()).limit(5).all()
        top_students_list = [
            {"name": s.name, "batch_id": s.batch_id, "attendance_percentage": s.attendance_percentage}
            for s in top_students_query
        ]

        return {
            "total_students": total_students,
            "total_mentors": total_mentors,
            "total_batches": total_batches,
            "average_attendance": f"{avg_attendance}%",
            "batch_wise_attendance": batch_wise_data,
            "top_students": top_students_list
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close() # This stops the page from loading forever!
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)