from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import pandas as pd
import os
import random
import json

# Initialize FastAPI app
app = FastAPI(
    title="Soft Skills Assessment API",
    description="API for soft skills assessment quizzes and evaluations",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data folder for consistent path usage
data_folder = 'data'
os.makedirs(data_folder, exist_ok=True)  # Create folder if it doesn't exist

# Define file paths for question data files
soft_skills_csv = os.path.join(data_folder, 'all_soft_skills_questions.csv')

# Load questions data
def load_questions():
    """Load questions from CSV file"""
    if os.path.exists(soft_skills_csv):
        return pd.read_csv(soft_skills_csv)
    else:
        raise FileNotFoundError(f"Questions file not found: {soft_skills_csv}")

# Define soft skill question sources for 1-5 agreement scale format
soft_skills_questions = {
    'communication': {
        'verbal': [
            "I can explain complex topics clearly to people with no background knowledge.",
            "I ensure my message is understood correctly by checking for comprehension.",
            "I handle interruptions during presentations without losing my train of thought.",
            "I adapt my communication style effectively to different types of audiences.",
            "I actively use strategies to improve my listening skills on a regular basis."
        ],
        'written': [
            "I ensure clarity in my written communications by using precise language.",
            "I structure important emails and documents in a logical and organized manner.",
            "I adapt my writing style appropriately for different purposes and audiences.",
            "I thoroughly proofread important written work before finalizing it.",
            "I ensure my written messages convey the intended tone and emotional context."
        ],
        'nonverbal': [
            "I am highly aware of my body language during conversations.",
            "I can accurately interpret others' nonverbal cues during interactions.",
            "My body language consistently matches the verbal message I am communicating.",
            "I effectively adjust my nonverbal communication based on different settings.",
            "I use appropriate eye contact to enhance my communication effectiveness."
        ]
    },
    'leadership': {
        'team_motivation': [
            "I effectively motivate team members who are struggling with their tasks.",
            "I successfully lead teams through challenging situations by providing clear direction.",
            "I use effective strategies to inspire and energize team members.",
            "I recognize and utilize team members' individual strengths in task assignments.",
            "I maintain high team motivation levels even during long-term projects."
        ],
        'decision_making': [
            "I follow a clear process when making important decisions.",
            "I balance input from others with my own judgment when making decisions.",
            "I make effective decisions even under significant time pressure.",
            "I handle making unpopular decisions in a thoughtful and principled manner.",
            "I systematically evaluate the effectiveness of decisions I've made."
        ],
        'responsibility': [
            "I take full responsibility for team outcomes, whether successful or not.",
            "I handle team failures or mistakes constructively and without blame.",
            "I balance delegating tasks with maintaining appropriate oversight.",
            "I effectively encourage accountability in all team members.",
            "I address situations where team members don't meet expectations in a constructive way."
        ]
    },
    'time_management': {
        'prioritization': [
            "I decide which tasks to prioritize effectively when everything seems urgent.",
            "I maintain an organized system for managing tasks and responsibilities.",
            "I balance long-term goals with immediate demands in my planning.",
            "I adapt my priorities smoothly when circumstances change unexpectedly.",
            "I use effective strategies to avoid procrastination on important tasks."
        ],
        'deadline_management': [
            "I meet deadlines consistently across all areas of responsibility.",
            "I handle multiple competing deadlines without becoming overwhelmed.",
            "I take appropriate action promptly when I realize I might miss a deadline.",
            "I set realistic timeframes for my work based on accurate estimates.",
            "I communicate clearly about timeline expectations and any potential changes."
        ],
        'efficiency': [
            "I use effective strategies to work efficiently and maximize productivity.",
            "I minimize distractions successfully during important focused work.",
            "I identify and eliminate time-wasting activities in my schedule.",
            "I strike an appropriate balance between thoroughness and efficiency in my work.",
            "I utilize appropriate tools and systems to manage my time effectively."
        ]
    },
    'analytical': {
        'problem_solving': [
            "I approach complex problems with a clear and effective methodology.",
            "I break down large problems into manageable parts before solving them.",
            "I use effective strategies when I'm stuck on a difficult problem.",
            "I evaluate potential solutions thoroughly before implementation.",
            "I balance analysis with the need for timely action when solving problems."
        ],
        'critical_thinking': [
            "I evaluate the credibility of information using consistent criteria.",
            "I identify biases in my own thinking and adjust my analysis accordingly.",
            "I approach situations with conflicting information in a systematic manner.",
            "I follow a structured process for making evidence-based decisions.",
            "I regularly challenge my own assumptions when analyzing situations."
        ],
        'data_analysis': [
            "I feel comfortable interpreting complex numerical data and statistics.",
            "I identify meaningful patterns and trends in information effectively.",
            "I determine what data is relevant to a decision using clear criteria.",
            "I communicate complex data insights to others in an understandable way.",
            "I consistently use data to support my recommendations and decisions."
        ]
    }
}

# Define Pydantic models for request/response validation
class Question(BaseModel):
    question: str
    category: str

class QuestionResponse(BaseModel):
    question_id: int
    question: str
    category: str

class QuizRequest(BaseModel):
    category: Optional[str] = None
    count: int = 5
    randomize: bool = True

class SubmitAnswerRequest(BaseModel):
    question_id: int
    answer: int  # Rating from 1-5

class AssessmentResult(BaseModel):
    student_id: str
    student_name: str
    scores: Dict[str, float]
    overall_score: float

class SaveResultRequest(BaseModel):
    student_id: str
    student_name: str
    scores: Dict[str, float]

# Helper function to get questions
def get_soft_skills_questions(category=None, count_needed=5, randomize=True):
    """
    Get soft skills questions for assessment.
    
    Args:
        category (str): Category of soft skills ('communication', 'leadership', 'time_management', 'analytical').
                        If None, returns questions from all categories.
        count_needed (int): Number of questions to return per category
        randomize (bool): Whether to randomize the selection of questions
    
    Returns:
        list: List of questions with their categories
    """
    all_questions = []
    
    # Function to get questions from a specific category
    def get_category_questions(cat, subcats_dict, count):
        cat_questions = []
        for subcat, questions in subcats_dict.items():
            for question in questions:
                cat_questions.append({
                    'question': question,
                    'category': cat
                })
        
        # Randomize and select the requested number of questions
        if randomize:
            return random.sample(cat_questions, min(count, len(cat_questions)))
        else:
            return cat_questions[:min(count, len(cat_questions))]
    
    # If a specific category is requested
    if category is not None and category in soft_skills_questions:
        all_questions = get_category_questions(category, soft_skills_questions[category], count_needed)
    else:
        # Get questions from all categories
        for cat, subcats in soft_skills_questions.items():
            cat_questions = get_category_questions(cat, subcats, count_needed)
            all_questions.extend(cat_questions)
    
    return all_questions

# Function to save assessment results
def save_assessment_results(student_id, student_name, scores):
    """
    Save a student's assessment results to CSV.
    
    Args:
        student_id (str): Unique identifier for the student
        student_name (str): Student's name
        scores (dict): Dictionary with categories as keys and scores as values
    """
    # Create a DataFrame for the student results
    results_data = {
        'student_id': [student_id],
        'student_name': [student_name]
    }
    
    # Add each score category
    for category, score in scores.items():
        results_data[f'{category.lower()}_score'] = [score]
    
    # Calculate overall score
    results_data['overall_score'] = [sum(scores.values()) / len(scores)]
    
    # Create DataFrame
    results_df = pd.DataFrame(results_data)
    
    # Define file path
    results_file = os.path.join(data_folder, 'assessment_results.csv')
    
    # Check if file exists to append or create new
    if os.path.exists(results_file):
        # Append to existing file
        existing_df = pd.read_csv(results_file)
        updated_df = pd.concat([existing_df, results_df], ignore_index=True)
        updated_df.to_csv(results_file, index=False)
    else:
        # Create new file
        results_df.to_csv(results_file, index=False)
    
    return results_file

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Soft Skills Assessment API is running. Go to /docs for API documentation."}

@app.post("/quiz/", response_model=List[QuestionResponse])
async def get_quiz(request: QuizRequest):
    """Get a quiz with questions from the specified category"""
    try:
        questions = get_soft_skills_questions(
            category=request.category, 
            count_needed=request.count,
            randomize=request.randomize
        )
        
        # Add question IDs for reference
        for i, q in enumerate(questions):
            q['question_id'] = i
        
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

@app.post("/submit-assessment/", response_model=AssessmentResult)
async def submit_assessment(request: SaveResultRequest):
    """Save assessment results for a student"""
    try:
        results_file = save_assessment_results(
            student_id=request.student_id,
            student_name=request.student_name,
            scores=request.scores
        )
        
        # Calculate overall score
        overall_score = sum(request.scores.values()) / len(request.scores)
        
        return {
            "student_id": request.student_id,
            "student_name": request.student_name,
            "scores": request.scores,
            "overall_score": overall_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving assessment results: {str(e)}")

@app.get("/categories/")
async def get_categories():
    """Get all available soft skill categories"""
    return {"categories": list(soft_skills_questions.keys())}

@app.get("/results/{student_id}")
async def get_student_results(student_id: str):
    """Get assessment results for a specific student"""
    results_file = os.path.join(data_folder, 'assessment_results.csv')
    
    if not os.path.exists(results_file):
        raise HTTPException(status_code=404, detail="No assessment results found")
    
    try:
        results_df = pd.read_csv(results_file)
        student_results = results_df[results_df['student_id'] == student_id]
        
        if len(student_results) == 0:
            raise HTTPException(status_code=404, detail=f"No results found for student ID: {student_id}")
        
        # Convert to dictionary format
        result = student_results.iloc[0].to_dict()
        
        # Extract scores
        scores = {}
        for key, value in result.items():
            if key.endswith('_score') and key != 'overall_score':
                category = key.replace('_score', '')
                scores[category] = value
        
        return {
            "student_id": result['student_id'],
            "student_name": result['student_name'],
            "scores": scores,
            "overall_score": result['overall_score']
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving student results: {str(e)}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("quiz_api:app", host="127.0.0.1", port=8000, reload=True)
