from pydantic import BaseModel
from typing import List

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionCreate(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

class QuestionRead(BaseModel):
    id: int
    question_text: str

class ChoicesRead(BaseModel):
    question_id: int
    choices: List[ChoiceBase]

  