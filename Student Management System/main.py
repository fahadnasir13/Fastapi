import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, validator
from pathlib import Path

DATA_FILE = Path("students.json")


if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps([]))


class Student(BaseModel):
    id: str
    name: str = Field(..., min_length=2)
    email: EmailStr
    age: int = Field(..., ge=10, le=100)
    department: Optional[str] = None
    created_at: datetime
    CGPA: int = Field(..., ge=0, le=4)  # CGPA between 0 and 4

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    age: int = Field(..., ge=10, le=100)
    department: Optional[str] = None
    CGPA: int = Field(..., ge=0, le=4)


def load_students() -> List[Dict]:
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_students(students: List[Dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4, default=str)


app = FastAPI(title="Student Management System")

# Create Student
@app.post("/students", response_model=Student)
def create_student(student: StudentCreate):
    students = load_students()

    # Prevent duplicate email
    if any(s["email"] == student.email for s in students):
        raise HTTPException(status_code=400, detail="Email already exists")

    new_student = Student(
        id=str(uuid.uuid4()),
        name=student.name,
        email=student.email,
        age=student.age,
        department=student.department,
        created_at=datetime.now(),
        CGPA=student.CGPA,
    )

    students.append(new_student.dict())
    save_students(students)
    return new_student

# Get Student by ID
@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: str):
    students = load_students()
    for s in students:
        if s["id"] == student_id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")

# Update Student
@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: str, updated: StudentCreate):
    students = load_students()
    for i, s in enumerate(students):
        if s["id"] == student_id:
            # Prevent duplicate email (except current student)
            if any(stu["email"] == updated.email and stu["id"] != student_id for stu in students):
                raise HTTPException(status_code=400, detail="Email already exists")

            students[i].update(
                name=updated.name,
                email=updated.email,
                age=updated.age,
                department=updated.department,
                CGPA=updated.CGPA,
            )
            save_students(students)
            return students[i]
    raise HTTPException(status_code=404, detail="Student not found")

# Delete Student
@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    students = load_students()
    for i, s in enumerate(students):
        if s["id"] == student_id:
            deleted = students.pop(i)
            save_students(students)
            return {"message": "Student deleted", "student": deleted}
    raise HTTPException(status_code=404, detail="Student not found")

# List + Search + Filter + Sort
@app.get("/students", response_model=List[Student])
def list_students(
    search: Optional[str] = Query(None, description="Search by name or email"),
    department: Optional[str] = Query(None, description="Filter by department"),
    sort_by: Optional[str] = Query(None, regex="^(age|name)$", description="Sort by age or name"),
):
    students = load_students()

    # Search
    if search:
        students = [s for s in students if search.lower() in s["name"].lower() or search.lower() in s["email"].lower()]

    # Filter
    if department:
        students = [s for s in students if s.get("department") and s["department"].lower() == department.lower()]

    # Sort
    if sort_by:
        students = sorted(students, key=lambda x: x[sort_by])

    return students

# Stats Endpoint
@app.get("/students/stats")
def student_stats():
    students = load_students()
    total = len(students)
    avg_age = sum(s["age"] for s in students) / total if total > 0 else 0
    dept_counts = {}
    for s in students:
        dept = s.get("department", "Unknown")
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    return {
        "total_students": total,
        "average_age": avg_age,
        "count_per_department": dept_counts,
    }
