from pydantic import BaseModel
from typing import Optional

class Question(BaseModel):
    idQuestion: Optional[str] = None  # Optionnel pour l’entrée JSON
    content: str
    idQuiz: str

