from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    students = relationship("Student", back_populates="teacher")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    teacher = relationship("User", back_populates="students")
    logs = relationship("ProgressLog", back_populates="student", cascade="all, delete-orphan")

class Surah(Base):
    __tablename__ = "surahs"
    id = Column(Integer, primary_key=True) # 1-114
    name = Column(String, nullable=False)
    total_ayahs = Column(Integer, nullable=False)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)

class ProgressLog(Base):
    __tablename__ = "progress_log"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False) # sabaq, sabqi, manzil
    surah_id = Column(Integer, ForeignKey("surahs.id"))
    ayah_from = Column(Integer, nullable=False)
    ayah_to = Column(Integer, nullable=False)
    rating = Column(Integer)
    notes = Column(Text)
    
    student = relationship("Student", back_populates="logs")
    mistakes = relationship("Mistake", back_populates="log", cascade="all, delete-orphan")

class Mistake(Base):
    __tablename__ = "mistakes"
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("progress_log.id"))
    surah_id = Column(Integer, ForeignKey("surahs.id"))
    ayah_no = Column(Integer, nullable=False)
    
    log = relationship("ProgressLog", back_populates="mistakes")