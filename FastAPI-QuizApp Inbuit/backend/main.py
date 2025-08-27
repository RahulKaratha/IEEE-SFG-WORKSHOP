from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from models import QuestionCreate, QuestionRead, ChoicesRead

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

# -------------------- In-memory storage --------------------
questions_db = {}  # {id: {"question_text": str, "choices": [{"choice_text": str, "is_correct": bool}]}}
question_counter = 1

# -------------------- HTML Endpoints --------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    new_string = "Welcome to the Quiz App!"
    return templates.TemplateResponse("index.html", {"request": request, "new_string": new_string})

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

# -------------------- API Endpoints (CRUD) --------------------

# CREATE
@app.post("/questions/")
async def create_question(question: QuestionCreate):
    global question_counter
    q_id = question_counter
    question_counter += 1

    questions_db[q_id] = {
        "question_text": question.question_text,
        "choices": [{"choice_text": c.choice_text, "is_correct": c.is_correct} for c in question.choices]
    }

    return {"message": "Question created successfully", "question_id": q_id}

# READ (single)
@app.get("/questions/{question_id}")
async def read_question(question_id: int):
    question = questions_db.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {
        "id": question_id,
        "question_text": question["question_text"],
        "choices": question["choices"]
    }

# READ (all)
@app.get("/questions/")
async def list_questions():
    return [
        {"id": q_id, "question_text": q["question_text"]}
        for q_id, q in questions_db.items()
    ]

# UPDATE
@app.put("/questions/{question_id}")
async def update_question(question_id: int, updated_data: QuestionCreate):
    if question_id not in questions_db:
        raise HTTPException(status_code=404, detail="Question not found")

    questions_db[question_id] = {
        "question_text": updated_data.question_text,
        "choices": [{"choice_text": c.choice_text, "is_correct": c.is_correct} for c in updated_data.choices]
    }

    return {"message": "Question updated successfully"}

# DELETE
@app.delete("/questions/{question_id}")
async def delete_question(question_id: int):
    if question_id not in questions_db:
        raise HTTPException(status_code=404, detail="Question not found")

    del questions_db[question_id]
    return {"message": "Question deleted successfully"}
