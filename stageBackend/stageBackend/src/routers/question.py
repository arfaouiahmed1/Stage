# routers/question.py
from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.question import Question
from src.core.firebase import db

router = APIRouter()
collection_name = "questions"

def doc_to_question(doc):
    data = doc.to_dict()
    return Question(
        idQuestion=doc.id,
        content=data.get("content"),
        idQuiz=data.get("idQuiz"),
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
