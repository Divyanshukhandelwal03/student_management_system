from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
# Initialize FastAPI
app = FastAPI()

# MongoDB Connection
client = AsyncIOMotorClient("mongodb+srv://student123:student123@cluster0.pvxzi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.student_management
students_collection = db.students


# Pydantic Models
class Address(BaseModel):
    city: str
    country: str


class Student(BaseModel):
    name: str
    age: int
    address: Address


class StudentUpdate(BaseModel):
    name: Optional[str]
    age: Optional[int]
    address: Optional[Address]


class StudentResponse(BaseModel):
    id: str
    name: str
    age: int
    address: Address


# Helper Functions
def student_helper(student) -> dict:
    """Convert MongoDB ObjectId to string for JSON response."""
    student["id"] = str(student["_id"])
    del student["_id"]
    return student


@app.get("/",status_code=200)
async def create_home():
    return {"message":"Welcome to Api"}
# Routes
@app.post("/students", status_code=201)
async def create_student(student: Student):
    """Create a new student record."""
    student_data = student.dict()
    result = await students_collection.insert_one(student_data)
    return {"id": str(result.inserted_id)}


@app.get("/students", response_model=List[StudentResponse])
async def list_students(
    country: Optional[str] = Query(None),
    age: Optional[int] = Query(None),
):
    """List students with optional filters."""
    query = {}
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}

    students = await students_collection.find(query).to_list(100)
    return [student_helper(student) for student in students]


@app.get("/students/{id}", response_model=StudentResponse)
async def fetch_student(id: str = Path(...)):
    """Fetch a specific student by ID."""
    student = await students_collection.find_one({"_id": ObjectId(id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_helper(student)


@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student_update: StudentUpdate):
    """Update a student's details."""
    update_data = {k: v for k, v in student_update.dict().items() if v is not None}
    if update_data:
        result = await students_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Student not found")
    return


@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    """Delete a student by ID."""
    result = await students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
