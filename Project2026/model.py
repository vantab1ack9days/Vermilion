from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey,  DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import sessionmaker

import os
AVATAR_FOLDER = "static/avatars"
os.makedirs(AVATAR_FOLDER, exist_ok=True)

DATABASE_URL = "sqlite:///timetable.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Consultation(Base):
    __tablename__ = 'consultation'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    is_open = Column(Boolean, default=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    topic = Column(String(200), nullable=True)
    attended = Column(Boolean, default=False)

    teacher = relationship("Users", foreign_keys=[teacher_id], back_populates="taught_slots")
    student = relationship("Users", foreign_keys=[student_id], back_populates="booked_slots")


class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(255))
    photo_path = Column(String(255))
    bio = Column(Text, default="")

    taught_slots = relationship("Consultation", foreign_keys=[Consultation.teacher_id], back_populates="teacher")
    booked_slots = relationship("Consultation", foreign_keys=[Consultation.student_id], back_populates="student")
