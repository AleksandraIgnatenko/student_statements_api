import httpx
from fastapi import FastAPI

app = FastAPI(
    title="Report Service",
    description="API для получения отчета по студентам",
    version="1.0.0"
)

STUDENT_SERVICE_URL = "http://student_service:8001"
GRADE_SERVICE_URL = "http://grade_service:8002"

@app.get("/report/student/{student_id}")
async def get_report_by_student(student_id: int):
    student = {}
    grades = {}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{STUDENT_SERVICE_URL}/students/{student_id}")
            student = resp.json()
        except Exception:
            student = {"error": "Student service not available"}
        
        try:
            resp = await client.get(f"{GRADE_SERVICE_URL}/grades/student/{student_id}")
            grades = resp.json()
        except Exception:
            grades = {"error": "Grade service not available"}

        grade_list = grades.get("grades", []) if isinstance(grades, dict) else []
        if grade_list:
            total = sum(g["grade_numeric"] for g in grade_list)
            average = round(total / len(grade_list), 2)
        else:
            average = 0.0

        return {
            "student": student,
            "grades": grade_list,
            "average_grade": average,
            "total_subjects": len(grade_list)
        }