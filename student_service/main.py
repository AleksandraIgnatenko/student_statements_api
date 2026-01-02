from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import database, models, schemas

app = FastAPI(
    title="Student Service",
    description="API для управления студентами и группами",
    version="1.0.0"
)

@app.get("/students", response_model=List[schemas.StudentResponse])
def get_students(db: Session = Depends(database.get_db)):
    students = db.query(models.Student).all()
    return [
        schemas.StudentResponse(
            student_id=s.student_id,
            first_name=s.first_name,
            second_name=s.second_name,
            surname=s.surname,
            group_id=s.group.group_id if s.group else 0,
            group_name=s.group.group_name if s.group else "Без группы"
        )
        for s in students
    ]

@app.get("/students/{student_id}", response_model=schemas.StudentResponse)
def read_student(student_id: int, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return schemas.StudentResponse(
        student_id=student.student_id,
        first_name=student.first_name,
        second_name=student.second_name,
        surname=student.surname,
        group_id=student.group.group_id if student.group else 0,
        group_name=student.group.group_name if student.group else "Без группы"
    )

@app.post("/students", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(database.get_db)):
    group = db.query(models.Group).filter(models.Group.group_name == student.group_name).first()
    if not group:
        raise HTTPException(status_code=400, detail=f"Группа '{student.group_name}' не найдена")
    
    db_student = models.Student(
        first_name=student.first_name,
        second_name=student.second_name,
        surname=student.surname,
        group_id=group.group_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return schemas.StudentResponse(
        student_id=db_student.student_id,
        first_name=db_student.first_name,
        second_name=db_student.second_name,
        surname=db_student.surname,
        group_id=db_student.group.group_id,
        group_name=db_student.group.group_name
    )

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    db.delete(student)
    db.commit()
    return

@app.get("/groups", response_model=List[schemas.GroupResponse], tags=["Группы"])
def get_groups(db: Session = Depends(database.get_db)):
    groups = db.query(models.Group).all()
    return groups