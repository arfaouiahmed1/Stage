# routers/question.py
from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.question import Question
from src.schemas.generation import GenerateRequest, GenerateResponse, DimensionsResponse, SubdimensionsResponse
from src.core.firebase import db
from src.core.generation_service import QuestionGenerationService

router = APIRouter()
collection_name = "questions"

# Initialize generation service (singleton pattern)
generation_service = None

def get_generation_service():
    global generation_service
    if generation_service is None:
        generation_service = QuestionGenerationService()
    return generation_service

def doc_to_question(doc):
    data = doc.to_dict()
    return Question(
        idQuestion=doc.id,
        content=data.get("content"),
        idQuiz=data.get("idQuiz"),
        idCategory=data.get("idCategory")  # ✅ Ajout
    )


@router.post("/", response_model=Question)
def create_question(question: Question):
    doc_ref = db.collection(collection_name).document()  # ID auto-généré
    data = question.dict(exclude={"idQuestion"})  # on retire idQuestion si présent
    doc_ref.set(data)
    return Question(idQuestion=doc_ref.id, **data)  # on renvoie l'objet avec l'ID généré


@router.get("/", response_model=List[Question])
def get_questions():
    docs = db.collection(collection_name).stream()
    return [doc_to_question(doc) for doc in docs]

# ===============================================
# GENERATION ENDPOINTS (Must be before /{question_id})
# ===============================================

@router.get("/dimensions", response_model=DimensionsResponse)
def get_available_dimensions():
    """Get all available dimensions for question generation"""
    try:
        service = get_generation_service()
        dimensions = service.get_available_dimensions()
        return DimensionsResponse(dimensions=dimensions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dimensions: {str(e)}")


@router.get("/subdimensions/{dimension}", response_model=SubdimensionsResponse)
def get_available_subdimensions(dimension: str):
    """Get all available subdimensions for a given dimension"""
    try:
        service = get_generation_service()
        subdimensions = service.get_available_subdimensions(dimension)
        if not subdimensions:
            raise HTTPException(status_code=404, detail=f"No subdimensions found for dimension: {dimension}")
        return SubdimensionsResponse(subdimensions=subdimensions, dimension=dimension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subdimensions: {str(e)}")


@router.post("/generate", response_model=GenerateResponse)
def generate_questions(request: GenerateRequest):
    """Generate a single AI question and automatically save it to Firebase"""
    try:
        service = get_generation_service()
        
        # Generate question using the AI service
        generation_result = service.generate_questions(
            dimension=request.dimension,
            subdimension=request.subdimension,
            target_year_level=request.target_year_level,
            additional_context=request.additional_context
        )
        
        # Save generated question to Firebase
        question_data = {
            "content": generation_result["question"],
            "idQuiz": request.idQuiz,
            "idCategory": request.idCategory
        }
        
        # Create question in Firebase
        doc_ref = db.collection(collection_name).document()
        doc_ref.set(question_data)
        
        return GenerateResponse(
            question=generation_result["question"],
            dimension=generation_result["dimension"],
            subdimension=generation_result["subdimension"],
            target_year_level=generation_result["target_year_level"],
            response_scale="1-5",
            saved_question_id=doc_ref.id
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

@router.get("/{question_id}", response_model=Question)
def get_question(question_id: str):
    doc = db.collection(collection_name).document(question_id).get()
    if not doc.exists:
        raise HTTPException(404, "Question non trouvée")
    return doc_to_question(doc)

@router.put("/{question_id}", response_model=Question)
def update_question(question_id: str, question: Question):
    doc_ref = db.collection(collection_name).document(question_id)
    if not doc_ref.get().exists:
        raise HTTPException(404, "Question non trouvée")
    doc_ref.set(question.dict())
    return question

@router.delete("/{question_id}")
def delete_question(question_id: str):
    doc_ref = db.collection(collection_name).document(question_id)
    if not doc_ref.get().exists:
        raise HTTPException(404, "Question non trouvée")
    doc_ref.delete()
    return {"detail": "Question supprimée"}


@router.get("/by_quiz/{quiz_id}", response_model=List[Question])
def get_questions_by_quiz(quiz_id: str):
    query = db.collection(collection_name).where("idQuiz", "==", quiz_id).stream()
    questions = [doc_to_question(doc) for doc in query]
    if not questions:
        raise HTTPException(status_code=404, detail="Aucune question trouvée pour ce quiz")
    return questions


@router.get("/search/", response_model=List[Question])
def search_questions(keyword: str):
    all_questions = db.collection(collection_name).stream()
    filtered = [
        doc_to_question(doc)
        for doc in all_questions
        if keyword.lower() in doc.to_dict().get("content", "").lower()
    ]
    if not filtered:
        raise HTTPException(404, detail="Aucune question ne correspond à ce mot-clé")
    return filtered
