from pydantic import BaseModel, Field
from typing import Optional, List

class Question(BaseModel):
    idQuestion: Optional[str] = None
    content: str
    idQuiz: str
    idCategory: str  # ✅ La catégorie liée à cette question

class QuestionGenerateRequest(BaseModel):
    """Request for AI-generated questions"""
    idQuiz: str = Field(..., description="Quiz ID to assign generated question to")
    idCategory: str = Field(..., description="Category ID to assign generated question to")
    subdimension: Optional[str] = Field(default=None, description="Specific subdimension (optional - will auto-detect from category)")
    target_year_level: int = Field(..., ge=1, le=3, description="Target year level (1, 2, or 3)")

class QuestionGenerateResponse(BaseModel):
    """Response for AI-generated questions"""
    question: Question = Field(..., description="The generated and saved question")
    generation_metadata: dict = Field(..., description="Metadata about the generation process")

class DimensionsResponse(BaseModel):
    """Available dimensions for question generation"""
    dimensions: List[str] = Field(..., description="Available dimensions")

class SubdimensionsResponse(BaseModel):
    """Available subdimensions for a specific dimension"""
    subdimensions: List[str] = Field(..., description="Available subdimensions")
    dimension: str = Field(..., description="The dimension these subdimensions belong to")


