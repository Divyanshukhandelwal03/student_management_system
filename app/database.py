from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from app.utils import get_db_uri

client = AsyncIOMotorClient(get_db_uri())
db = client.student_management
students_collection = db.students
