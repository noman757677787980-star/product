import json
from typing import Annotated, Optional
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel

app = FastAPI()

FILE_PATH = "students.json"

# Pydantic Model for Student Creation/Validation
class Student(BaseModel):
    id: int
    name: str
    roll_number: int
    marks: int
    contact: str
    city: str

# Pydantic Model for Student Update
class StudentUpdate(BaseModel):
    name: str
    roll_number: int
    marks: int
    contact: str
    city: str

# Helper Function to Read JSON File
def read_students():
    try:
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    except Exception:
        return []

# Helper Function to Save to JSON File
def save_students(students):
    with open(FILE_PATH, "w") as file:
        json.dump(students, file, indent=4)


# 1. GET API - Read all students with optional city query using Annotated
@app.get("/students")
def get_students(
    city: Annotated[Optional[str], Query(description="Filter students by city")] = None
):
    students = read_students()
    if city:
        filtered_students = [s for s in students if s["city"].lower() == city.lower()]
        return filtered_students
    return students


# 2. GET API - Read one student by ID using Annotated and Path with validation (gt=0)
@app.get("/students/{student_id}")
def get_student_by_id(
    student_id: Annotated[int, Path(gt=0, description="The ID of the student to fetch")]
):
    students = read_students()
    for student in students:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")


# 3. POST API - Create a new student
@app.post("/students")
def create_student(student: Student):
    students = read_students()
    
    # Check if student ID already exists
    for s in students:
        if s["id"] == student.id:
            raise HTTPException(status_code=400, detail="Student with this ID already exists")
    
    # Convert Pydantic object to dictionary and save
    student_dict = student.model_dump()
    students.append(student_dict)
    save_students(students)
    
    return {"message": "Student created successfully", "data": student_dict}


# 4. PUT API - Update an existing student using Annotated and Path
@app.put("/students/{student_id}")
def update_student(
    student_id: Annotated[int, Path(gt=0, description="The ID of the student to update")],
    updated_student: StudentUpdate = None
):
    students = read_students()
    
    for index, student in enumerate(students):
        if student["id"] == student_id:
            student_dict = updated_student.model_dump()
            student_dict["id"] = student_id  # Keep the original ID intact
            students[index] = student_dict
            save_students(students)
            return {"message": "Student updated successfully", "data": student_dict}
            
    raise HTTPException(status_code=404, detail="Student not found")


# 5. DELETE API - Delete a student using Annotated and Path
@app.delete("/students/{student_id}")
def delete_student(
    student_id: Annotated[int, Path(gt=0, description="The ID of the student to delete")]
):
    students = read_students()
    
    for index, student in enumerate(students):
        if student["id"] == student_id:
            deleted_student = students.pop(index)
            save_students(students)
            return {"message": "Student deleted successfully", "data": deleted_student}
            
    raise HTTPException(status_code=404, detail="Student not found")