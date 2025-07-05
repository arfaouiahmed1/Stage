from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Quiz(BaseModel):
    idQuiz: Optional[str] = None  # Optionnel pour l’entrée JSON
    idTeacher: str
    idCategory: str
    dateCreation: datetime
    isAccessible: bool = True
    accessCode: str
    
