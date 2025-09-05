from fastapi import FastAPI, HTTPException, Query
from typing import List
import json

app = FastAPI()

# Load student data from JSON file
with open("students.json", "r") as f:
    students = json.load(f)

# Get all students
@app.get("/students", status_code=200)
def get_students():
    return {"students": students}

#  Get student by ID
@app.get("/students/{student_id}", status_code=200)
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")

# Get students sorted by CGPA
@app.get("/students/sorted", status_code=200)
def get_sorted_students(order: str = Query("asc", enum=["asc", "desc"])):
    sorted_students = sorted(
        students,
        key=lambda x: x["cgpa"],
        reverse=True if order == "desc" else False
    )
    return {"students": sorted_students}
