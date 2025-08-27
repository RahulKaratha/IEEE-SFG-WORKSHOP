from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Annotated

import models
from database import engine, SessionLocal

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML templates
templates = Jinja2Templates(directory="templates")

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# -------------------- Pydantic Schemas --------------------

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

    class Config:
        orm_mode = True

# -------------------- Database Dependency --------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# -------------------- HTML Endpoints --------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/add-question", response_class=HTMLResponse)
async def add_question_page(request: Request):
    return templates.TemplateResponse("add_question.html", {"request": request})

@app.get("/view-question", response_class=HTMLResponse)
async def view_question_page(request: Request):
    return templates.TemplateResponse("view_question.html", {"request": request})

@app.get("/update-question", response_class=HTMLResponse)
async def update_question_page(request: Request):
    return templates.TemplateResponse("update_question.html", {"request": request})

@app.get("/delete-question", response_class=HTMLResponse)
async def delete_question_page(request: Request):
    return templates.TemplateResponse("delete_question.html", {"request": request})


# -------------------- API Endpoints --------------------

# CREATE
@app.post("/questions/")
async def create_question(question: QuestionBase, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)

    db.commit()

    return {"message": "Question and choices added successfully", "question_id": db_question.id}

# READ (single question)
@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: db_dependency):
    question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    choices = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()

    return {
        "id": question.id,
        "question_text": question.question_text,
        "choices": [
            {"id": c.id, "choice_text": c.choice_text, "is_correct": c.is_correct}
            for c in choices
        ]
    }

# READ ALL
@app.get("/questions/")
async def read_all_questions(db: db_dependency):
    questions = db.query(models.Questions).all()
    result = []
    for q in questions:
        choices = db.query(models.Choices).filter(models.Choices.question_id == q.id).all()
        result.append({
            "id": q.id,
            "question_text": q.question_text,
            "choices": [
                {"id": c.id, "choice_text": c.choice_text, "is_correct": c.is_correct}
                for c in choices
            ]
        })
    return result

# UPDATE
@app.put("/questions/{question_id}")
async def update_question(question_id: int, updated: QuestionBase, db: db_dependency):
    question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Update question text
    question.question_text = updated.question_text
    db.commit()

    # Delete old choices
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()
    db.commit()

    # Add updated choices
    for choice in updated.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=question_id
        )
        db.add(db_choice)

    db.commit()

    return {"message": "Question updated successfully"}

# DELETE
@app.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: db_dependency):
    question = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Delete choices first (due to foreign key constraint)
    db.query(models.Choices).filter(models.Choices.question_id == question_id).delete()
    db.commit()

    db.delete(question)
    db.commit()

    return {"message": "Question deleted successfully"}
