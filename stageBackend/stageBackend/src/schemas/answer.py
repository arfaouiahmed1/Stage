from pydantic import BaseModel
from typing import Optional

class Answer(BaseModel):
    idAnswer: Optional[str] = None        # Firestore peut générer l’ID
    idUser: str                     # l’étudiant qui répond
    idQuiz: str                     # le quiz concerné
    idQuestion: str                 # la question concernée
    value: int                      # la réponse (de 1 à 5)
