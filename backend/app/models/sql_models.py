# app/models/sql_models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class AttendanceRecord(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    delivered = Column(Integer)
    attended = Column(Integer)
    percentage = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)