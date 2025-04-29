from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Dict, List, Tuple, Optional
from collections import namedtuple

# Hardcoded MySQL connection string
DB_URL = "mysql+pymysql://root:your_new_password@localhost:3306/college_erp"

# Define data structures
Student = namedtuple('Student', ['id', 'name', 'year', 'department'])
Mark = namedtuple('Mark', ['subject', 'score'])
Assignment = namedtuple('Assignment', ['title', 'grade'])
Attendance = namedtuple('Attendance', ['subject', 'percentage'])

try:
    engine = create_engine(DB_URL)
except Exception as e:
    logging.error(f"Failed to create database engine: {str(e)}")
    raise

def get_student_data(student_id: int) -> Tuple[Optional[Student], List[Mark], List[Assignment], List[Attendance]]:
    try:
        with engine.connect() as conn:
            # Get student info
            result = conn.execute(
                text("SELECT id, name, year, department FROM students WHERE id = :id"),
                {"id": student_id}
            ).fetchone()
            
            if not result:
                return None, [], [], []
            
            # Convert student row to named tuple
            student = Student(
                id=result[0],
                name=result[1],
                year=result[2],
                department=result[3]
            )
            
            # Get marks
            marks_result = conn.execute(
                text("SELECT subject, score FROM marks WHERE student_id = :id"),
                {"id": student_id}
            ).fetchall()
            marks = [Mark(subject=row[0], score=row[1]) for row in marks_result]
            
            # Get assignments
            assignments_result = conn.execute(
                text("SELECT title, grade FROM assignments WHERE student_id = :id"),
                {"id": student_id}
            ).fetchall()
            assignments = [Assignment(title=row[0], grade=row[1]) for row in assignments_result]
            
            # Get attendance
            attendance_result = conn.execute(
                text("SELECT subject, percentage FROM attendance WHERE student_id = :id"),
                {"id": student_id}
            ).fetchall()
            attendance = [Attendance(subject=row[0], percentage=row[1]) for row in attendance_result]
            
            return student, marks, assignments, attendance
            
    except SQLAlchemyError as e:
        logging.error(f"Database error for student_id {student_id}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error for student_id {student_id}: {str(e)}")
        raise
