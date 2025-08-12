from pydantic import BaseModel
from typing import List, Optional

class Group(BaseModel):
    idGroup: Optional[str] = None  # Optionnel pour l'entrée JSON
    groupName: str
    members: List[str]  # Liste d'IDs d'étudiants

class StudentMember(BaseModel):
    first_name: str
    last_name: str
    hard_skills: float
    soft_skills: float
    creativity: float
    teamwork: float
    class_name: str
    gender: str
    nationality: str
    age: int

class GeneratedGroup(BaseModel):
    group: int
    size: int
    members: List[StudentMember]

class ClusteringResponse(BaseModel):
    best_algorithm: str
    groups: List[GeneratedGroup]

class ClusteringConfig(BaseModel):
    group_size_min: int = 5
    group_size_max: int = 7
    population_size: int = 30
    generations: int = 50
    distance_metric: str = "euclidean"

class ClusteringRequest(BaseModel):
    # This appears to be for future use, keeping it simple for now
    config: Optional[ClusteringConfig] = None
