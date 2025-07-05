from pydantic import BaseModel
from typing import Optional

class Score(BaseModel):
    idScore: Optional[str] = None  # Optionnel pour l’entrée JSON
    totalScore: float
    idUser: str
    idQuiz: str
