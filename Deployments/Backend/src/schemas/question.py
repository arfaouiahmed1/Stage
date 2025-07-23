from pydantic import BaseModel
from typing import Optional

class Question(BaseModel):
    idQuestion: Optional[str] = None
    content: str
    idQuiz: str
    idCategory: str  # ✅ La catégorie liée à cette question


