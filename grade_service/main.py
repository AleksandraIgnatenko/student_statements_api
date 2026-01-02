import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
import database, models, schemas

app = FastAPI(
    title="Grade Service",
    description="API для управления оценками студентов",
    version="1.0.0"
)

STUDENT_SERVICE_URL = "http://student_service:8001"

async def verify_student_exists(student_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{STUDENT_SERVICE_URL}/students/{student_id}")
            if resp.status_code == 404:
                raise HTTPException(status_code=400, detail="Студент не найден")
            resp.raise_for_status()
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Student service недоступен")


def get_subject_id_by_name(db: Session, subject_name: str):
    subject = db.query(models.Subject).filter(models.Subject.subject_name == subject_name).first()
    if not subject:
        raise HTTPException(status_code=400, detail=f"Предмет '{subject_name}' не найден")
    return subject.subject_id


@app.get("/grades/student/{student_id}", response_model=dict)
async def get_grades_by_student(student_id: int, db: Session = Depends(database.get_db)):
    grades = db.query(models.Grade)\
        .options(joinedload(models.Grade.subject))\
        .filter(models.Grade.student_id == student_id)\
        .all()
    
    student = {}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{STUDENT_SERVICE_URL}/students/{student_id}")
            student = resp.json()
        except Exception:
            student = {"error": "Student service not available"}

    return {
        "student": student,
        "grades": [
            {
                "grade_id": g.grade_id,
                "subject_name": g.subject.subject_name,
                "grade_numeric": g.grade_numeric,
                "grade_ects": g.grade_ects,
                "date_recorded": g.date_recorded
            }
            for g in grades
        ]
    }

@app.get("/grades/subjects", response_model=List[str])
def get_subjects(db: Session = Depends(database.get_db)):
    subjects = db.query(models.Subject.subject_name).all()
    return [s[0] for s in subjects]

@app.post("/grades", response_model=schemas.GradeResponse)
async def create_or_update_grade(grade: schemas.GradeCreate, db: Session = Depends(database.get_db)):
    await verify_student_exists(grade.student_id)
    
    subject_id = get_subject_id_by_name(db, grade.subject_name)
    
    existing_grade = db.query(models.Grade).filter(
        models.Grade.student_id == grade.student_id,
        models.Grade.subject_id == subject_id
    ).first()
    
    if existing_grade:
        existing_grade.grade_numeric = grade.grade_numeric
        existing_grade.grade_ects = grade.grade_ects
        existing_grade.date_recorded = date.today()
        db.commit()
        db.refresh(existing_grade)
        
        return schemas.GradeResponse(
            grade_id=existing_grade.grade_id,
            student_id=existing_grade.student_id,
            subject_name=grade.subject_name,
            grade_numeric=existing_grade.grade_numeric,
            grade_ects=existing_grade.grade_ects,
            date_recorded=existing_grade.date_recorded
        )
    else:
        db_grade = models.Grade(
            student_id=grade.student_id,
            subject_id=subject_id,
            grade_numeric=grade.grade_numeric,
            grade_ects=grade.grade_ects,
            date_recorded=date.today()
        )
        db.add(db_grade)
        db.commit()
        db.refresh(db_grade)
        
        return schemas.GradeResponse(
            grade_id=db_grade.grade_id,
            student_id=db_grade.student_id,
            subject_name=grade.subject_name,
            grade_numeric=db_grade.grade_numeric,
            grade_ects=db_grade.grade_ects,
            date_recorded=db_grade.date_recorded
        )


@app.put("/grades/{grade_id}", response_model=schemas.GradeResponse)
def update_grade(grade_id: int, grade_update: schemas.GradeUpdate, db: Session = Depends(database.get_db)):
    db_grade = db.query(models.Grade).filter(models.Grade.grade_id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Оценка не найдена")
    
    if grade_update.grade_numeric is not None:
        db_grade.grade_numeric = grade_update.grade_numeric
    if grade_update.grade_ects is not None:
        db_grade.grade_ects = grade_update.grade_ects
    
    db.commit()
    db.refresh(db_grade)
    
    subject_name = db.query(models.Subject).filter(models.Subject.subject_id == db_grade.subject_id).first().subject_name
    
    return schemas.GradeResponse(
        grade_id=db_grade.grade_id,
        student_id=db_grade.student_id,
        subject_name=subject_name,
        grade_numeric=db_grade.grade_numeric,
        grade_ects=db_grade.grade_ects,
        date_recorded=db_grade.date_recorded
    )


@app.delete("/grades/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(grade_id: int, db: Session = Depends(database.get_db)):
    db_grade = db.query(models.Grade).filter(models.Grade.grade_id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Оценка не найдена")
    
    db.delete(db_grade)
    db.commit()
    return