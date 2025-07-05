from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.answer import Answer
from src.core.firebase import db

router = APIRouter()
collection_name = "answers"

# 🔁 Convertir un document Firestore en objet Answer
def doc_to_answer(doc) -> Answer:
    data = doc.to_dict()
    return Answer(
        id=doc.id,
        idUser=data["idUser"],
        idQuiz=data["idQuiz"],
        idQuestion=data["idQuestion"],
        value=data["value"]
    )

# ✅ 1. Créer une nouvelle réponse
@router.post("/", response_model=Answer)
def create_answer(answer: Answer):
    doc_ref = db.collection(collection_name).document()  # ID auto-généré
    data = answer.dict(exclude={"id"})  # on exclut id si présent
    doc_ref.set(data)
    return Answer(id=doc_ref.id, **data)

# 📖 2. Lire toutes les réponses
@router.get("/", response_model=List[Answer])
def get_all_answers():
    docs = db.collection(collection_name).stream()
    return [doc_to_answer(doc) for doc in docs]

# 📖 3. Lire les réponses d’un étudiant pour un quiz
@router.get("/by_quiz/{quiz_id}/user/{user_id}", response_model=List[Answer])
def get_answers_by_user_and_quiz(quiz_id: str, user_id: str):
    docs = db.collection(collection_name) \
             .where("idQuiz", "==", quiz_id) \
             .where("idUser", "==", user_id) \
             .stream()
    results = [doc_to_answer(doc) for doc in docs]
    if not results:
        raise HTTPException(status_code=404, detail="Aucune réponse trouvée")
    return results

# ✏️ 4. Modifier une réponse existante
@router.put("/{answer_id}", response_model=Answer)
def update_answer(answer_id: str, updated_answer: Answer):
    doc_ref = db.collection(collection_name).document(answer_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")

    data = updated_answer.dict(exclude={"id"})
    doc_ref.set(data)
    return Answer(id=answer_id, **data)

# ❌ 5. Supprimer une réponse
@router.delete("/{answer_id}")
def delete_answer(answer_id: str):
    doc_ref = db.collection(collection_name).document(answer_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")
    doc_ref.delete()
    return {"detail": "Réponse supprimée"}
