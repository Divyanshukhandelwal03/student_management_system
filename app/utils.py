def student_helper(student) -> dict:
    """Convert MongoDB ObjectId to string for JSON response."""
    student["id"] = str(student["_id"])
    del student["_id"]
    return student
