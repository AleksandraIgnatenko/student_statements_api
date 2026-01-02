# grade_service/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class GradeCreate(BaseModel):
    student_id: int
    subject_name: str 
    grade_numeric: int
    grade_ects: str

class GradeUpdate(BaseModel):
    grade_numeric: Optional[int] = None
    grade_ects: Optional[str] = None

class GradeResponse(BaseModel):
    grade_id: int
    student_id: int
    subject_name: str
    grade_numeric: int
    grade_ects: str
    date_recorded: date

    class Config:
        from_attributes = True