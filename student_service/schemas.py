from pydantic import BaseModel

class StudentCreate(BaseModel):
    first_name: str
    second_name: str
    surname: str
    group_name: str 

class StudentResponse(BaseModel):
    student_id: int
    first_name: str
    second_name: str
    surname: str
    group_id: int
    group_name: str 

    class Config:
        from_attributes = True

class GroupResponse(BaseModel):
    group_id: int
    group_name: str

    class Config:
        from_attributes = True