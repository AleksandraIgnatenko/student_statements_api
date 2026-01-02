from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, CHAR, Date
from sqlalchemy.orm import relationship
from database import Base

SCHEMA = "statement"

class Student(Base):
    __tablename__ = "students"
    __table_args__ = {"schema": SCHEMA}
    student_id = Column(Integer, primary_key=True)

class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = {"schema": SCHEMA}

    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), unique=True, nullable=False)

    grades = relationship("Grade", back_populates="subject")


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = {"schema": SCHEMA}

    grade_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey(f"{SCHEMA}.students.student_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey(f"{SCHEMA}.subjects.subject_id", ondelete="CASCADE"), nullable=False)
    grade_numeric = Column(SmallInteger, nullable=False)
    grade_ects = Column(CHAR(1), nullable=False)
    date_recorded = Column(Date, nullable=False, default="CURRENT_DATE")

    subject = relationship("Subject", back_populates="grades")