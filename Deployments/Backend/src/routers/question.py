# routers/question.py
from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.question import (
    Question, 
    QuestionGenerateRequest, 
    QuestionGenerateResponse, 
    DimensionsResponse, 
    SubdimensionsResponse
)
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
    """Get all available dimensions for question generation (from dataset + categories)"""
    try:
        service = get_generation_service()
        dataset_dimensions = service.get_available_dimensions()
        
        # Also get dimensions from categories (islands)
        try:
            categories_docs = db.collection("categories").stream()
            category_dimensions = [doc.to_dict().get("island", "") for doc in categories_docs]
            category_dimensions = [d for d in category_dimensions if d]  # Remove empty strings
        except Exception as e:
            print(f"⚠️ Could not fetch categories: {e}")
            category_dimensions = []
        
        # Combine and deduplicate
        all_dimensions = list(set(dataset_dimensions + category_dimensions))
        all_dimensions.sort()
        
        return DimensionsResponse(dimensions=all_dimensions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dimensions: {str(e)}")


@router.get("/subdimensions/{dimension}", response_model=SubdimensionsResponse)
def get_available_subdimensions(dimension: str):
    """Get all available subdimensions for a given dimension (from dataset + categories)"""
    try:
        service = get_generation_service()
        
        # Get subdimensions from dataset
        dataset_subdimensions = service.get_available_subdimensions(dimension)
        
        # Get subdimensions from categories
        try:
            categories_docs = db.collection("categories").where("island", "==", dimension).stream()
            category_subdimensions = []
            for doc in categories_docs:
                subcats = doc.to_dict().get("subcategories", [])
                category_subdimensions.extend(subcats)
        except Exception as e:
            print(f"⚠️ Could not fetch category subdimensions: {e}")
            category_subdimensions = []
        
        # Combine and deduplicate
        all_subdimensions = list(set(dataset_subdimensions + category_subdimensions))
        all_subdimensions.sort()
        
        if not all_subdimensions:
            raise HTTPException(status_code=404, detail=f"No subdimensions found for dimension: {dimension}")
            
        return SubdimensionsResponse(subdimensions=all_subdimensions, dimension=dimension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subdimensions: {str(e)}")


@router.post("/generate", response_model=QuestionGenerateResponse)
def generate_questions(request: QuestionGenerateRequest):
    """Generate AI question with auto-detection of dimension and subdimension from category"""
    try:
        # Get category to extract dimension
        category_ref = db.collection("categories").document(request.idCategory)
        category_doc = category_ref.get()
        
        if not category_doc.exists:
            raise HTTPException(status_code=404, detail=f"Category {request.idCategory} not found")
        
        category_data = category_doc.to_dict()
        dimension = category_data.get("island")
        
        if not dimension:
            raise HTTPException(status_code=400, detail="Category has no dimension (island) specified")
        
        # Determine subdimension
        subdimension = None
        if request.subdimension:
            # Teacher provided a specific subdimension
            subdimension = request.subdimension
        else:
            # Auto-select subdimension from category or dataset
            category_subdimensions = category_data.get("subcategories", [])
            
            if category_subdimensions:
                # Use first subdimension from category
                subdimension = category_subdimensions[0]
            else:
                # Fallback to first subdimension from dataset for this dimension
                service = get_generation_service()
                dataset_subdimensions = service.get_available_subdimensions(dimension)
                if dataset_subdimensions:
                    subdimension = dataset_subdimensions[0]
                else:
                    raise HTTPException(status_code=400, detail=f"No subdimensions available for dimension '{dimension}'")
        
        # Verify quiz exists
        quiz_ref = db.collection("quizzes").document(request.idQuiz)
        quiz_doc = quiz_ref.get()
        
        if not quiz_doc.exists:
            raise HTTPException(status_code=404, detail=f"Quiz {request.idQuiz} not found")
        
        print(f"🎯 Generating question: {dimension} -> {subdimension} (Year {request.target_year_level})")
        
        # Generate question using the AI service
        service = get_generation_service()
        generation_result = service.generate_questions(
            dimension=dimension,
            subdimension=subdimension,
            target_year_level=request.target_year_level,
            additional_context=None  # Removed additional_context
        )
        
        # Create a Question model instance with the generated content
        new_question = Question(
            content=generation_result["question"],
            idQuiz=request.idQuiz,
            idCategory=request.idCategory
        )
        
        # Use the existing create_question function to save to Firebase
        saved_question = create_question(new_question)
        
        # Update category to include the subdimension if it's not already there
        try:
            _update_category_with_subdimension(request.idCategory, subdimension)
        except Exception as e:
            print(f"⚠️ Warning: Could not update category with subdimension: {e}")
        
        return QuestionGenerateResponse(
            question=saved_question,
            generation_metadata={
                "dimension": generation_result["dimension"],
                "subdimension": generation_result["subdimension"],
                "target_year_level": generation_result["target_year_level"],
                "context_used": generation_result.get("context_used", []),
                "response_scale": "1-5"
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")


def _update_category_with_subdimension(category_id: str, subdimension: str):
    """Update category to include the subdimension if it's not already present"""
    try:
        # Get the category document
        category_ref = db.collection("categories").document(category_id)
        category_doc = category_ref.get()
        
        if category_doc.exists:
            category_data = category_doc.to_dict()
            subcategories = category_data.get("subcategories", [])
            
            # Add the subdimension if it's not already in the list
            if subdimension not in subcategories:
                subcategories.append(subdimension)
                category_ref.update({"subcategories": subcategories})
                print(f"✅ Added '{subdimension}' to category {category_id}")
        else:
            print(f"⚠️ Category {category_id} not found")
            
    except Exception as e:
        print(f"❌ Error updating category: {e}")
        # Don't raise the error as this is not critical for question generation

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
