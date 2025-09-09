from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import json
import os

app = FastAPI(title="Student Management API")

DATA_FILE = "students.json"


if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)



class Student(BaseModel):
    id: int = Field(..., gt=0, description="Unique ID for each student")
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., gt=5, lt=100)
    roll_number: str = Field(..., min_length=1, description="Unique roll number")
    grade: Optional[str] = None

    @validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty or just spaces")
        return v


def load_students() -> List[dict]:
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_students(students: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)



@app.post("/students/", response_model=Student)
def add_student(student: Student):
    students = load_students()

    for s in students:
        if s["id"] == student.id:
            raise HTTPException(status_code=400, detail="Student with this ID already exists")
        if s["roll_number"] == student.roll_number:
            raise HTTPException(status_code=400, detail="Student with this roll number already exists")

    students.append(student.dict())
    save_students(students)
    return student


@app.get("/students/", response_model=List[Student])
def get_students():
    return load_students()


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    students = load_students()
    for s in students:
        if s["id"] == student_id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")
