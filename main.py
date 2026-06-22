from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import engine, Base, get_db
from backend import models
from datetime import date, datetime, timedelta
import os
import re

app = FastAPI(title="Zaryah+ Hifz Engine")

# Permissive CORS Layer to avoid local network blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database automatically on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# Pydantic Schemas for incoming request data validation
from pydantic import BaseModel
from typing import List

class StudentCreate(BaseModel):
    name: str

class ProgressCreate(BaseModel):
    student_id: int
    type: str  
    surah_id: int
    ayah_from: int
    ayah_to: int
    rating: int
    notes: str = ""
    mistakes: List[int] = []

# Router paths to serve the frontend interface
@app.get("/")
@app.get("/dashboard")
def read_dashboard_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Error", "message": "index.html workspace asset file is missing."}

# --- CORE API ROUTES ---

@app.get("/api/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students

@app.get("/api/surahs")
def get_surahs(db: Session = Depends(get_db)):
    surahs = db.query(models.Surah).order_by(models.Surah.id).all()
    return surahs

@app.post("/api/students")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(name=student.name)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/api/students/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(db_student)
    db.commit()
    return {"status": "success"}

@app.post("/api/progress")
def add_progress(progress: ProgressCreate, db: Session = Depends(get_db)):
    db_log = models.ProgressLog(
        student_id=progress.student_id,
        date=date.today(),
        type=progress.type,
        surah_id=progress.surah_id,
        ayah_from=progress.ayah_from,
        ayah_to=progress.ayah_to,
        rating=progress.rating,
        notes=progress.notes
    )
    db.add(db_log)
    db.flush()  # Flush to get the generated log ID

    for ayah_no in progress.mistakes:
        db_mistake = models.Mistake(
            log_id=db_log.id,
            surah_id=progress.surah_id,
            ayah_no=ayah_no
        )
        db.add(db_mistake)
    
    db.commit()
    return {"status": "success", "log_id": db_log.id}

@app.get("/api/students/{id}/dashboard")
def get_student_dashboard(id: int, db: Session = Depends(get_db)):
    total_sabaq = db.query(models.ProgressLog).filter(
        models.ProgressLog.student_id == id,
        models.ProgressLog.type == 'sabaq'
    ).count()
    
    recent_mistakes_query = db.query(models.Mistake).join(models.ProgressLog).filter(
        models.ProgressLog.student_id == id
    ).order_by(models.ProgressLog.date.desc()).limit(10).all()

    formatted_mistakes = [{
        "surah_no": m.surah_id,
        "ayah_no": m.ayah_no,
        "date": m.log.date.isoformat() if m.log.date else None
    } for m in recent_mistakes_query]

    # Streak calculation based on distinct log dates
    logs = db.query(models.ProgressLog.date).filter(
        models.ProgressLog.student_id == id
    ).distinct().order_by(models.ProgressLog.date.desc()).all()
    
    streak = 0
    if logs:
        log_dates = {row.date for row in logs}
        current_check = date.today()
        if current_check not in log_dates:
            current_check -= timedelta(days=1)
        
        while current_check in log_dates:
            streak += 1
            current_check -= timedelta(days=1)

    return {
        "total_sabaq": total_sabaq,
        "streak": streak,
        "recent_mistakes": formatted_mistakes
    }

@app.get("/api/students/{id}/analytics")
def get_student_analytics(id: int, db: Session = Depends(get_db)):
    # --- Milestone Calculation ---
    milestones = {
        "flawless_session": False,
        "para_completed": False,
        "hifz_completed": False,
    }

    # 1. Flawless Session: Check for any log with a 5-star rating or zero associated mistakes.
    flawless_logs = db.query(models.ProgressLog).filter(models.ProgressLog.student_id == id).all()
    for log in flawless_logs:
        if log.rating == 5 or not log.mistakes:
            milestones["flawless_session"] = True
            break

    # 2. Para/Hifz Completion: Use student's current Juz from their name as a proxy.
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if student and student.name:
        match = re.search(r'\(Juz (\d+)\)', student.name)
        if match:
            current_juz = int(match.group(1))
            if current_juz > 1:
                milestones["para_completed"] = True
            
            if current_juz >= 30:
                last_surah_log = db.query(models.ProgressLog).filter(models.ProgressLog.student_id == id, models.ProgressLog.surah_id == 114).first()
                if last_surah_log:
                    milestones["hifz_completed"] = True
    
    return {
        "milestones": milestones
    }