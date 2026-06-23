from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import json
import os

app = FastAPI()

# Allows your frontend to talk to your backend safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect("hifz.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def setup_database():
    conn = get_db_connection()
    # Raw SQL table creation per requirements
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            juz INTEGER NOT NULL,
            pin TEXT,
            sabaq TEXT,
            sabqi TEXT,
            manzil TEXT,
            streak INTEGER,
            logs TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- NEW: SERVE FRONTEND ON PORT 8000 ---
@app.get("/")
def serve_frontend():
    # This tells FastAPI to load your HTML file when you go to localhost:8000
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html not found in the current directory."}

# Pydantic Validation Model
class Student(BaseModel):
    id: str
    name: str
    juz: int
    pin: str = "1234"
    sabaq: str = "Not set"
    sabqi: str = "Not set"
    manzil: str = "Not set"
    streak: int = 0
    logs: list = []

# Route 1: Get all students
@app.get("/students")
def get_all_students():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM students").fetchall() # Raw SQL
    conn.close()
    
    students = []
    for row in rows:
        s_dict = dict(row)
        # Convert JSON strings back to lists for the frontend
        s_dict['logs'] = json.loads(s_dict['logs']) if s_dict['logs'] else []
        s_dict['currentJuz'] = s_dict.pop('juz') # Format for frontend
        students.append(s_dict)
    return students

# Route 2: Add a student
@app.post("/students")
def add_student(student: Student):
    # Strict Backend Validation: Must not crash the server
    if not student.name or not student.name.strip():
        raise HTTPException(status_code=400, detail="Student name cannot be empty.")
    if student.juz < 1 or student.juz > 30:
        raise HTTPException(status_code=400, detail="Juz must be between 1 and 30.")

    conn = get_db_connection()
    try:
        # Raw SQL INSERT
        conn.execute(
            "INSERT INTO students (id, name, juz, pin, sabaq, sabqi, manzil, streak, logs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (student.id, student.name.strip(), student.juz, student.pin, student.sabaq, student.sabqi, student.manzil, student.streak, json.dumps(student.logs))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Student ID already exists.")
    finally:
        conn.close()
        
    return {"message": "Student added successfully"}

# Route 3: Delete a student
@app.delete("/students/{student_id}")
def remove_student(student_id: str):
    conn = get_db_connection()
    # Raw SQL DELETE
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return {"message": "Student removed successfully"}