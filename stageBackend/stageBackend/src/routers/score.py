from fastapi import APIRouter, HTTPException
from src.core.firebase import db
from src.schemas.score import Score
import uuid

router = APIRouter()
answers_collection = "answers"
scores_collection = "scores"

@router.post("/calculate_score/{quiz_id}/user/{user_id}", response_model=Score)
def calculate_score(quiz_id: str, user_id: str):
    docs = db.collection(answers_collection) \
             .where("idQuiz", "==", quiz_id) \
             .where("idUser", "==", user_id) \
             .stream()

    answers = [doc.to_dict() for doc in docs]
    
    if not answers:
        raise HTTPException(status_code=404, detail="Aucune réponse trouvée pour ce quiz")

    total = sum(a["value"] for a in answers)
    count = len(answers)
    average_score = round(total / count, 2)

    score_id = str(uuid.uuid4())
    score_data = {
        "idScore": score_id,
        "idUser": user_id,
        "idQuiz": quiz_id,
        "totalScore": average_score
    }

    db.collection(scores_collection).document(score_id).set(score_data)

    return Score(**score_data)
