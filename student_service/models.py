from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

SCHEMA = "statement"

class Group(Base):
    __tablename__ = "groups"
    __table_args__ = {"schema": SCHEMA}

    group_id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(50), unique=True, nullable=False)

    students = relationship("Student", back_populates="group")


class Student(Base):
    __tablename__ = "students"
    __table_args__ = {"schema": SCHEMA}

    student_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    second_name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    group_id = Column(Integer, ForeignKey(f"{SCHEMA}.groups.group_id", ondelete="SET NULL"), nullable=True)

    group = relationship("Group", back_populates="students")