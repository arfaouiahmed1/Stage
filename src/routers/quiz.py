# routers/quiz.py
from fastapi import APIRouter, HTTPException, Query
from typing import List
from src.schemas.quiz import Quiz
from src.core.firebase import db

router = APIRouter()
collection_name = "quizzes"
category_collection = "categories"  # nom de ta collection categories

def doc_to_quiz(doc):
    data = doc.to_dict()
    return Quiz(
        idQuiz=doc.id,
        idTeacher=data.get("idTeacher"),
        idCategory=data.get("idCategory"),
        dateCreation=data.get("dateCreation"),
        isAccessible=data.get("isAccessible", True),
        accessCode=data.get("accessCode")
    )

# @router.post("/", response_model=Quiz)
# def create_quiz(quiz: Quiz):
#     doc_ref = db.collection(collection_name).document()  # ID auto-généré
#     data = quiz.dict(exclude={"idQuiz"})  # exclure l'idQuiz fourni (ou absent)
#     doc_ref.set(data)
#     return Quiz(idQuiz=doc_ref.id, **data)  # retourner avec ID généré

@router.post("/", response_model=Quiz)
def create_quiz(quiz: Quiz):
    # 🔒 Validation : exactement 4 catégories
    if not isinstance(quiz.idCategory, list) or len(quiz.idCategory) != 4:
        raise HTTPException(
            status_code=400,
            detail="Each quiz must be assigned exactly 4 categories."
        )

    doc_ref = db.collection(collection_name).document()  # ID auto-généré
    data = quiz.dict(exclude={"idQuiz"})  # exclure l'idQuiz fourni (ou absent)
    doc_ref.set(data)
    return Quiz(idQuiz=doc_ref.id, **data)


@router.get("/", response_model=List[Quiz])
def get_quizzes():
    docs = db.collection(collection_name).stream()
    return [doc_to_quiz(doc) for doc in docs]

@router.get("/{quiz_id}", response_model=Quiz)
def get_quiz(quiz_id: str):
    doc = db.collection(collection_name).document(quiz_id).get()
    if not doc.exists:
        raise HTTPException(404, "Quiz non trouvé")
    return doc_to_quiz(doc)

@router.put("/{quiz_id}", response_model=Quiz)
def update_quiz(quiz_id: str, quiz: Quiz):
    doc_ref = db.collection(collection_name).document(quiz_id)
    if not doc_ref.get().exists:
        raise HTTPException(404, "Quiz non trouvé")
    doc_ref.set(quiz.dict())
    return quiz

@router.delete("/{quiz_id}")
def delete_quiz(quiz_id: str):
    doc_ref = db.collection(collection_name).document(quiz_id)
    if not doc_ref.get().exists:
        raise HTTPException(404, "Quiz non trouvé")
    doc_ref.delete()
    return {"detail": "Quiz supprimé"}

# ----- Nouvelle route pour filtrer les quizzes par island -----
@router.get("/by_island/", response_model=List[Quiz])
def get_quizzes_by_island(island: str = Query(..., description="Nom de l'island")):
    # 1. Trouver les categories correspondant à l'island
    categories_query = db.collection(category_collection).where("island", "==", island).stream()
    id_categories = [doc.id for doc in categories_query]

    if not id_categories:
        raise HTTPException(404, "Aucune catégorie trouvée pour cet island")

    # 2. Chercher les quizzes dont idCategory est dans la liste
    quizzes = []
    for cat_id in id_categories:
        query = db.collection(collection_name).where("idCategory", "==", cat_id).stream()
        quizzes.extend([doc_to_quiz(doc) for doc in query])

    if not quizzes:
        raise HTTPException(404, "Aucun quiz trouvé pour cet island")

    return quizzes
