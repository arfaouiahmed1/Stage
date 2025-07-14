import os
import pandas as pd
import numpy as np
import random

# Define data folder for consistent path usage
data_folder = 'data'
os.makedirs(data_folder, exist_ok=True)  # Create folder if it doesn't exist

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

def get_soft_skills_questions(category=None, count_needed=5, randomize=True):
    """
    Get soft skills questions for assessment.
    
    Args:
        category (str): Category of soft skills ('communication', 'leadership', 'time_management', 'analytical').
                        If None, returns questions from all categories.
        count_needed (int): Number of questions to return per category
        randomize (bool): Whether to randomize the selection of questions
    
    Returns:
        pd.DataFrame: DataFrame containing the selected questions
    """
    all_questions = []
    
    # Function to get questions from a specific category
    def get_category_questions(cat, subcats_dict, count):
        cat_questions = []
        for subcat, questions in subcats_dict.items():
            for question in questions:
                cat_questions.append({
                    'question': question,
                    'category': cat,
                    'subcategory': subcat,
                    'type': 'agreement_scale'
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
    
    # Create DataFrame from the collected questions
    questions_df = pd.DataFrame(all_questions)
    
    return questions_df

# Example usage
if __name__ == "__main__":
    # Get 5 questions for the communication category
    comm_questions = get_soft_skills_questions('communication', 5)
    print(f"Communication questions: {len(comm_questions)}")
    print(comm_questions['question'].tolist())
    
    # Get 3 questions from each category
    all_questions = get_soft_skills_questions(None, 3)
    print(f"\nAll categories: {len(all_questions)}")
    print(all_questions.groupby('category').size())
