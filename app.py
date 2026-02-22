from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI(title="Student Risk Analysis API")


# ==========================
# Models
# ==========================
class StudentData(BaseModel):
    Student_ID: str
    Attendance_percent: float
    Math: float
    English: float
    Science: float
    Teacher_Load_Index: float


class BatchStudents(BaseModel):
    students: List[StudentData]


# ==========================
# Risk Formula
# ==========================
def calculate_risk(student: StudentData):

    attendance_risk = 100 - student.Attendance_percent

    academic_avg = (
        student.Math +
        student.English +
        student.Science
    ) / 3

    academic_risk = 100 - academic_avg

    teacher_risk = min(student.Teacher_Load_Index * 100, 100)

    total_risk = (
        attendance_risk * 0.4 +
        academic_risk * 0.4 +
        teacher_risk * 0.2
    )

    if total_risk >= 70:
        level = "High"
    elif total_risk >= 40:
        level = "Moderate"
    else:
        level = "Low"

    return round(total_risk, 2), level


# ==========================
# Rule-based Summary
# ==========================
def generate_summary(student, score, level):

    issues = []

    if student.Attendance_percent < 75:
        issues.append("low attendance")

    if (student.Math + student.English + student.Science) / 3 < 60:
        issues.append("weak academic performance")

    if student.Teacher_Load_Index > 1.2:
        issues.append("teacher overload")

    if not issues:
        issues.append("stable performance")

    return (
        f"Student {student.Student_ID} shows {level} risk "
        f"due to {', '.join(issues)}. "
        f"Recommended monitoring and academic support."
    )


# ==========================
# Health Check
# ==========================
@app.get("/")
def root():
    return {"status": "Student Risk API Running"}


# ==========================
# Single Student Endpoint
# ==========================
@app.post("/analyze")
def analyze_student(student: StudentData):

    score, level = calculate_risk(student)
    summary = generate_summary(student, score, level)

    return {
        "Student_ID": student.Student_ID,
        "Risk_Score": score,
        "Risk_Level": level,
        "Summary": summary,
        "Generated_Date": str(datetime.date.today())
    }


# ==========================
# ⭐ Batch Endpoint
# ==========================
@app.post("/analyze_batch")
def analyze_batch(batch: BatchStudents):

    try:
        results = []

        for student in batch.students:
            score, level = calculate_risk(student)
            summary = generate_summary(student, score, level)

            results.append({
                "Student_ID": student.Student_ID,
                "Risk_Score": score,
                "Risk_Level": level,
                "Summary": summary,
                "Generated_Date": str(datetime.date.today())
            })

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
