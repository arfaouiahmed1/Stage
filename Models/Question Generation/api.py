import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
# import genai client for Google Gemini API (may need installation)
import google.generativeai as genai  # type: ignore

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Load questions for context retrieval
CSV_PATH = "/workspaces/Stage/Datasets/Quiz Generation/questions.csv"
df = pd.read_csv(CSV_PATH, comment="#")
texts = df["question_text"].tolist()
metadatas = df[["dimension","subdimension","target_year_level","question_id"]].to_dict(orient="records")

# Embedding model and FAISS index
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed_model.encode(texts, convert_to_numpy=True)
index = faiss.IndexFlatIP(embeddings.shape[1])
faiss.normalize_L2(embeddings)
index.add(embeddings)

class GenerateRequest(BaseModel):
    dimension: str
    subdimension: str
    target_year_level: int
    num_questions: int = 5
    additional_context: str | None = None

class SubmitResponse(BaseModel):
    responses: dict

app = FastAPI(title="Question Generation RAG API", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api": "running"}

@app.get("/dimensions")
def list_dimensions():
    return sorted(df["dimension"].unique().tolist())

@app.get("/subdimensions/{dimension}")
def list_subdimensions(dimension: str):
    return sorted(df[df["dimension"]==dimension]["subdimension"].unique().tolist())

@app.post("/generate")
def generate(req: GenerateRequest):
    # Filter by metadata
    mask = (df.dimension==req.dimension) & (df.subdimension==req.subdimension) & (df.target_year_level==req.target_year_level)
    candidates = df[mask]
    if candidates.empty:
        raise HTTPException(status_code=404, detail="No base questions for given filters")
    # Retrieve context via FAISS if additional context provided
    if req.additional_context:
        query_emb = embed_model.encode([req.additional_context], convert_to_numpy=True)
        faiss.normalize_L2(query_emb)
        D, I = index.search(query_emb, k=5)
        context_snippets = [texts[i] for i in I[0]]
    else:
        context_snippets = candidates.question_text.sample(min(5, len(candidates))).tolist()
    # Build prompt
    prompt = (
        f"Generate {req.num_questions} self-assessment questions for \"{req.dimension} - {req.subdimension}\" at year level {req.target_year_level}. "
        + "Each question should be a clear self-assessment statement using 'How confident are you...' or similar phrasing. "
        + "Use these examples as context:\n" + "\n".join(f"- {txt}" for txt in context_snippets)
        + "\n\nGenerate exactly " + str(req.num_questions) + " questions, one per line. Do not include numbering or bullet points."
    )
    # Call LLM
    response = model.generate_content(prompt)
    # Extract generated questions
    generated_text = response.text
    # Split by lines and clean up
    items = [line.strip() for line in generated_text.split('\n') if line.strip() and not line.strip().startswith(('*', '-', '1.', '2.', '3.', '4.', '5.'))]
    # Take only the requested number of questions
    items = items[:req.num_questions]
    return {"questions": items}

@app.post("/submit")
def submit_answer(resp: SubmitResponse):
    # Placeholder: simply acknowledge
    return {"status": "received", "count": len(resp.responses)}
