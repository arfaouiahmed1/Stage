from pydantic import BaseModel
from typing import List
from typing import Optional

class Group(BaseModel):
    idGroup: Optional[str] = None  # Optionnel pour l’entrée JSON
    groupName: str
    members: List[str]  # Liste d'IDs d'étudiants
