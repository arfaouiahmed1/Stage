from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import pandas as pd
import random
import json
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="Soft Skills Assessment API",
    description="API for serving soft skills assessment quizzes and evaluating responses",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define data folder for consistent path usage
data_folder = 'data'
os.makedirs(data_folder, exist_ok=True)  # Create folder if it doesn't exist

# Define soft skill question categories and questions
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

# Pydantic models
class QuestionItem(BaseModel):
    id: int
    question: str
    category: str
    subcategory: Optional[str] = None

class AssessmentQuestion(BaseModel):
    id: int
    question: str

class AnswerItem(BaseModel):
    question_id: int
    answer_value: int  # 1-5 scale

class SubmitAnswersRequest(BaseModel):
    student_id: str
    student_name: str
    answers: List[AnswerItem]

class AssessmentResult(BaseModel):
    student_id: str
    student_name: str
    scores: Dict[str, float]
    overall_score: float
    feedback: Dict[str, str]

class QuizRequest(BaseModel):
    category: Optional[str] = None
    count: int = 5

# Helper function to compile all questions
def compile_questions():
    all_questions = []
    question_id = 0
    
    for category, subcategories in soft_skills_questions.items():
        for subcategory, questions in subcategories.items():
            for question in questions:
                all_questions.append({
                    'id': question_id,
                    'question': question,
                    'category': category,
                    'subcategory': subcategory
                })
                question_id += 1
    
    return all_questions

# Load questions from CSV if it exists, otherwise compile from dictionary
def load_questions():
    csv_path = os.path.join(data_folder, 'all_soft_skills_questions.csv')
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            if 'id' not in df.columns:
                df['id'] = range(len(df))
            questions = df.to_dict('records')
            return questions
        except Exception as e:
            print(f"Error loading questions from CSV: {e}")
            return compile_questions()
    else:
        return compile_questions()

# Save assessment results
def save_assessment_results(student_id, student_name, scores):
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
        print(f"Results for {student_name} appended to {results_file}")
    else:
        # Create new file
        results_df.to_csv(results_file, index=False)
        print(f"New results file created at {results_file} with data for {student_name}")
    
    return results_file

# Generate feedback based on scores
def generate_feedback(scores):
    feedback = {}
    
    for category, score in scores.items():
        if score >= 4.5:
            feedback[category] = f"Outstanding! You demonstrate excellent {category.lower()} skills."
        elif score >= 3.5:
            feedback[category] = f"Good job! You have solid {category.lower()} skills with some room for improvement."
        elif score >= 2.5:
            feedback[category] = f"You have moderate {category.lower()} skills. Consider focusing on development in this area."
        else:
            feedback[category] = f"This appears to be an area for growth. Consider seeking resources to develop your {category.lower()} skills."
    
    return feedback

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Soft Skills Assessment API. Use /docs to see available endpoints."}

@app.get("/questions", response_model=List[QuestionItem])
async def get_all_questions():
    """Get all available soft skills questions"""
    questions = load_questions()
    return questions

@app.post("/quiz", response_model=List[AssessmentQuestion])
async def create_quiz(request: QuizRequest):
    """Create a quiz with questions from a specific category or mixed categories"""
    questions = load_questions()
    
    if request.category:
        # Filter questions by category
        category_questions = [q for q in questions if q['category'].lower() == request.category.lower()]
        if not category_questions:
            raise HTTPException(status_code=404, detail=f"Category '{request.category}' not found")
        
        # Select random questions from this category
        selected_questions = random.sample(
            category_questions, 
            min(request.count, len(category_questions))
        )
    else:
        # Get questions from all categories, ensuring a balanced mix
        categories = list(set(q['category'] for q in questions))
        questions_per_category = max(1, request.count // len(categories))
        
        selected_questions = []
        for category in categories:
            cat_questions = [q for q in questions if q['category'] == category]
            category_selection = random.sample(
                cat_questions,
                min(questions_per_category, len(cat_questions))
            )
            selected_questions.extend(category_selection)
        
        # If we need more questions to meet the count, add random questions
        if len(selected_questions) < request.count:
            remaining_questions = [q for q in questions if q not in selected_questions]
            additional_questions = random.sample(
                remaining_questions,
                min(request.count - len(selected_questions), len(remaining_questions))
            )
            selected_questions.extend(additional_questions)
        
        # If we have too many, trim to the requested count
        if len(selected_questions) > request.count:
            selected_questions = selected_questions[:request.count]
    
    # Convert to simpler format for the quiz
    quiz_questions = [{"id": q["id"], "question": q["question"]} for q in selected_questions]
    return quiz_questions

@app.post("/submit", response_model=AssessmentResult)
async def submit_answers(submission: SubmitAnswersRequest):
    """Submit answers and get assessment results"""
    # Load all questions to map IDs back to categories
    all_questions = load_questions()
    question_map = {q['id']: q for q in all_questions}
    
    # Organize answers by category
    category_scores = {}
    category_counts = {}
    
    for answer in submission.answers:
        if answer.question_id not in question_map:
            raise HTTPException(
                status_code=400, 
                detail=f"Question with ID {answer.question_id} not found"
            )
        
        question = question_map[answer.question_id]
        category = question['category']
        
        # Initialize if this is the first answer for this category
        if category not in category_scores:
            category_scores[category] = 0
            category_counts[category] = 0
        
        # Add the score
        category_scores[category] += answer.answer_value
        category_counts[category] += 1
    
    # Calculate average score for each category
    final_scores = {}
    for category in category_scores:
        if category_counts[category] > 0:  # Avoid division by zero
            final_scores[category] = round(category_scores[category] / category_counts[category], 2)
    
    # Calculate overall score
    overall_score = sum(final_scores.values()) / len(final_scores) if final_scores else 0
    
    # Generate feedback
    feedback = generate_feedback(final_scores)
    
    # Save results
    save_assessment_results(submission.student_id, submission.student_name, final_scores)
    
    # Return the result
    return AssessmentResult(
        student_id=submission.student_id,
        student_name=submission.student_name,
        scores=final_scores,
        overall_score=round(overall_score, 2),
        feedback=feedback
    )

@app.get("/categories")
async def get_categories():
    """Get all available skill categories"""
    return list(soft_skills_questions.keys())

@app.get("/results/{student_id}")
async def get_student_results(student_id: str):
    """Get assessment results for a specific student"""
    results_file = os.path.join(data_folder, 'assessment_results.csv')
    
    if not os.path.exists(results_file):
        raise HTTPException(status_code=404, detail="No assessment results found")
    
    try:
        results_df = pd.read_csv(results_file)
        student_results = results_df[results_df['student_id'] == student_id]
        
        if student_results.empty:
            raise HTTPException(status_code=404, detail=f"No results found for student ID: {student_id}")
        
        # Get the latest result for this student
        latest_result = student_results.iloc[-1].to_dict()
        
        # Extract scores
        scores = {}
        for key in latest_result:
            if key.endswith('_score') and key != 'overall_score':
                category = key.replace('_score', '')
                scores[category] = latest_result[key]
        
        # Generate feedback
        feedback = generate_feedback(scores)
        
        return {
            "student_id": student_id,
            "student_name": latest_result['student_name'],
            "scores": scores,
            "overall_score": latest_result['overall_score'],
            "feedback": feedback
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
