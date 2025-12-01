# app/crud.py
from sqlalchemy.orm import Session
from app.models.sql_models import AttendanceRecord
from datetime import datetime

def get_attendance(db: Session):
    """Read all attendance records from the DB"""
    return db.query(AttendanceRecord).all()

def create_attendance(db: Session, data: list):
    """Delete old data and save new data"""
    # 1. Clear old data 
    db.query(AttendanceRecord).delete()
    
    # 2. Add new records
    for item in data:
        record = AttendanceRecord(
            subject=item['subject'],
            delivered=item['delivered'],
            attended=item['attended'],
            percentage=item['percentage'],
            last_updated=datetime.now()
        )
        db.add(record)
    
    # 3. Commit transaction
    db.commit()
    return data