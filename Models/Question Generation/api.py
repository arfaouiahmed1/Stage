from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from question_generation_rag import QuestionGenerationRAG

app = FastAPI(
    title="Question Generation API",
    description="RAG-based question generation system for educational assessments",
    version="1.0.0"
)

# Global RAG system instance
rag_system = None

class QuestionRequest(BaseModel):
    dimension: Optional[str] = None
    subcategory: Optional[str] = None
    question_type: Optional[str] = None
    target_year_level: Optional[str] = None
    additional_context: Optional[str] = ""
    num_questions: int = 1

class QuestionResponse(BaseModel):
    questions: List[Dict[str, Any]]
    status: str
    message: str

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global rag_system
    try:
        print("Initializing Question Generation RAG system...")
        rag_system = QuestionGenerationRAG()
        print("RAG system initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize RAG system: {str(e)}")
        raise e

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Question Generation RAG API",
        "version": "1.0.0",
        "endpoints": {
            "/generate": "POST - Generate new questions",
            "/suggestions": "GET - Get parameter suggestions",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    return {
        "status": "healthy",
        "rag_system_loaded": rag_system is not None,
        "documents_loaded": len(rag_system.knowledge_base) if rag_system else 0
    }

@app.post("/generate", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    """Generate new questions based on provided parameters"""
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        questions = rag_system.generate_question(
            dimension=request.dimension,
            subcategory=request.subcategory,
            question_type=request.question_type,
            target_year_level=request.target_year_level,
            additional_context=request.additional_context,
            num_questions=request.num_questions
        )
        
        return QuestionResponse(
            questions=questions,
            status="success",
            message=f"Generated {len(questions)} question(s) successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

@app.get("/suggestions")
async def get_suggestions(partial_input: str = ""):
    """Get suggestions for question parameters"""
    
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        suggestions = rag_system.get_question_suggestions(partial_input)
        return {
            "suggestions": suggestions,
            "count": len(suggestions),
            "partial_input": partial_input
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@app.get("/dimensions")
async def get_dimensions():
    """Get available dimensions"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    dimensions = set()
    for doc in rag_system.knowledge_base:
        if doc['type'] == 'question':
            dimensions.add(doc['dimension'])
        elif doc['type'] == 'taxonomy':
            dimensions.add(doc['dimension_name'])
    
    return {"dimensions": sorted(list(dimensions))}

@app.get("/subcategories/{dimension}")
async def get_subcategories(dimension: str):
    """Get subcategories for a specific dimension"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    subcategories = set()
    for doc in rag_system.knowledge_base:
        if doc['type'] == 'question' and doc['dimension'] == dimension:
            subcategories.add(doc['subcategory'])
        elif doc['type'] == 'taxonomy' and doc['dimension_name'] == dimension:
            subcategories.add(doc['subcategory_name'])
    
    return {"subcategories": sorted(list(subcategories))}

@app.get("/question-types")
async def get_question_types():
    """Get available question types"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    question_types = set()
    for doc in rag_system.knowledge_base:
        if doc['type'] == 'question' and doc['question_type']:
            question_types.add(doc['question_type'])
    
    return {"question_types": sorted(list(question_types))}

@app.post("/search")
async def search_context(query: str, top_k: int = 5):
    """Search for relevant context from the knowledge base"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        relevant_docs = rag_system.retrieve_relevant_context(query, top_k)
        return {
            "query": query,
            "results": relevant_docs,
            "count": len(relevant_docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("Error: GOOGLE_API_KEY environment variable is not set")
        print("Please set your Google API key: export GOOGLE_API_KEY='your_api_key_here'")
        print("You can get a free API key from: https://makersuite.google.com/app/apikey")
        exit(1)
    
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)
