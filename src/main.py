from fastapi import FastAPI
from src.routers import quiz, question, category, answer, score


app = FastAPI(title="Quiz API")
app.include_router(quiz.router, prefix="/quizzes", tags=["quizzes"])
app.include_router(question.router, prefix="/questions", tags=["questions"])
app.include_router(category.router, prefix="/categories", tags=["categories"])
app.include_router(answer.router, prefix="/answers", tags=["answers"])
app.include_router(score.router, prefix="/scores", tags=["scores"])

@app.get("/")
def root():
    return {"message": "Bienvenue dans l'API Quiz"}



