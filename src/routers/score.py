from fastapi import APIRouter, HTTPException
from src.core.firebase import db
from src.schemas.score import Score
import uuid

router = APIRouter()

answers_collection = "answers"
scores_collection = "scores"
quizzes_collection = "quizzes"

# 🔹 Convertit un document Firestore en objet Score
def doc_to_score(doc) -> Score:
    data = doc.to_dict()
    return Score(
        idScore=doc.id,
        idUser=data["idUser"],
        idQuiz=data["idQuiz"],
        totalScore=data["totalScore"],
        scoreCategory1=data["scoreCategory1"],
        scoreCategory2=data["scoreCategory2"],
        scoreCategory3=data["scoreCategory3"],
        scoreCategory4=data["scoreCategory4"]
    )

# ✅ 1. Calculer et enregistrer le score
@router.post("/calculate_score/{quiz_id}/user/{user_id}", response_model=Score)
def calculate_score(quiz_id: str, user_id: str):
    # 1. Récupérer le quiz
    quiz_doc = db.collection(quizzes_collection).document(quiz_id).get()
    if not quiz_doc.exists:
        raise HTTPException(status_code=404, detail="Quiz non trouvé")
    
    quiz_data = quiz_doc.to_dict()
    categories = quiz_data.get("idCategory", [])

    if len(categories) != 4:
        raise HTTPException(status_code=400, detail="Le quiz doit contenir exactement 4 catégories")

    # 2. Récupérer les réponses
    docs = db.collection(answers_collection) \
             .where("idQuiz", "==", quiz_id) \
             .where("idUser", "==", user_id) \
             .stream()

    answers = [doc.to_dict() for doc in docs]
    if not answers:
        raise HTTPException(status_code=404, detail="Aucune réponse trouvée")

    # 3. Grouper les réponses par catégorie
    scores_by_cat = {cat: [] for cat in categories}
    for ans in answers:
        cat = ans.get("idCategory")
        if cat in scores_by_cat:
            scores_by_cat[cat].append(ans.get("value", 0))

    # 4. Calculer les scores par catégorie
    averages = []
    for cat in categories:
        vals = scores_by_cat[cat]
        avg = round(sum(vals) / len(vals), 2) if vals else 0.0
        averages.append(avg)

    total_score = round(sum(averages) / 4, 2)

    # 5. Enregistrer dans Firestore
    score_id = str(uuid.uuid4())
    score_data = {
        "idScore": score_id,
        "idUser": user_id,
        "idQuiz": quiz_id,
        "scoreCategory1": averages[0],
        "scoreCategory2": averages[1],
        "scoreCategory3": averages[2],
        "scoreCategory4": averages[3],
        "totalScore": total_score
    }

    db.collection(scores_collection).document(score_id).set(score_data)
    return Score(**score_data)

# ✅ 2. Obtenir un score existant
@router.get("/get_score/{quiz_id}/user/{user_id}", response_model=Score)
def get_score(quiz_id: str, user_id: str):
    query = db.collection(scores_collection) \
              .where("idQuiz", "==", quiz_id) \
              .where("idUser", "==", user_id) \
              .stream()

    for doc in query:
        return doc_to_score(doc)

    raise HTTPException(status_code=404, detail="Score non trouvé pour ce quiz et cet utilisateur")
