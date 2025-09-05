from fastapi import FastAPI

app = FastAPI()

student = {
    "id": 2,
    "name": "Ayesha",
    "field_of_study": "Data Science"
}

@app.get("/student")
def get_student():
    return student
