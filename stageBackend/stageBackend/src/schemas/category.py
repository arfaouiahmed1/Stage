from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    idCategory: Optional[str] = None  # Optionnel pour l’entrée JSON
    island: str  
