import streamlit as st
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from question_generation_rag import QuestionGenerationRAG
import os
import warnings
from typing import Dict, List, Any

# Suppress torch warnings
warnings.filterwarnings("ignore", message=".*torch.classes.*")
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

# Configure page
st.set_page_config(
    page_title="Question Generation System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Google Forms-like styling
st.markdown("""
<style>
    .main-header {
        background: #4285f4;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.2);
    }
    
    .form-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #4285f4;
    }
    
    .question-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #4285f4;
        border: 1px solid #e8eaed;
    }
    
    .question-text {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #202124;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    .question-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .meta-item {
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #dadce0;
        font-size: 0.9rem;
        color: #5f6368;
    }
    
    .question-criteria {
        background: #e8f0fe;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .criteria-list {
        list-style: none;
        padding: 0;
        margin: 0.5rem 0;
    }
    
    .criteria-item {
        padding: 0.3rem 0;
        color: #1a73e8;
        font-weight: 500;
    }
    
    .criteria-item:before {
        content: "✓ ";
        color: #34a853;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .metric-card {
        background: #4285f4;
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(66, 133, 244, 0.3);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.4);
    }
    
    .success-banner {
        background: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #2e7d32;
        border-left: 4px solid #4caf50;
    }
    
    .info-banner {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #1565c0;
        border-left: 4px solid #2196f3;
    }
    
    .stButton > button {
        background: #4285f4;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: #3367d6;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = []
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system with caching"""
    try:
        return QuestionGenerationRAG()
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {str(e)}")
        return None

def create_quiz_json(questions: List[Dict], metadata: Dict) -> Dict:
    """Create properly formatted JSON output for frontend team"""
    
    quiz_json = {
        "quiz_metadata": {
            "quiz_id": f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": metadata.get("title", "Generated Quiz"),
            "description": metadata.get("description", ""),
            "created_at": datetime.now().isoformat(),
            "created_by": metadata.get("teacher_name", "Teacher"),
            "total_questions": len(questions),
            "estimated_duration_minutes": sum(q.get('time_limit_minutes', 15) for q in questions),
            "difficulty_level": metadata.get("difficulty", "medium"),
            "subject_area": metadata.get("subject", "Programming"),
            "target_audience": {
                "year_level": metadata.get("year_level", "1-3"),
                "course": metadata.get("course", "Computer Science"),
                "prerequisites": metadata.get("prerequisites", [])
            }
        },
        "assessment_framework": {
            "primary_dimension": metadata.get("dimension", "creativity"),
            "subcategory": metadata.get("subcategory", "innovation_problem_solving"),
            "collaboration_level": metadata.get("collaboration_level", "medium"),
            "assessment_type": metadata.get("assessment_type", "formative")
        },
        "scoring_configuration": {
            "total_points": len(questions) * 5,  # 5 points per question
            "grading_scale": {
                "excellent": {"min_score": 90, "description": "Exceptional demonstration"},
                "good": {"min_score": 75, "description": "Solid demonstration"},
                "satisfactory": {"min_score": 60, "description": "Meets expectations"},
                "needs_improvement": {"min_score": 40, "description": "Below expectations"},
                "unsatisfactory": {"min_score": 0, "description": "Minimal demonstration"}
            },
            "rubric_criteria": [
                "technical_accuracy",
                "creative_thinking", 
                "problem_solving_approach",
                "communication_clarity"
            ]
        },
        "questions": []
    }
    
    # Process each question
    for i, question in enumerate(questions, 1):
        question_obj = {
            "question_id": question.get('generated_id', f"q_{i:03d}"),
            "question_number": i,
            "question_text": question.get('question_text', ''),
            "question_type": question.get('question_type', 'open_ended'),
            "difficulty_level": estimate_difficulty(question),
            "time_allocation": {
                "recommended_minutes": question.get('time_limit_minutes', 15),
                "maximum_minutes": question.get('time_limit_minutes', 15) * 1.5
            },
            "assessment_criteria": {
                "primary": question.get('assessment_criteria_1', 'problem_solving'),
                "secondary": question.get('assessment_criteria_2', 'creativity'),
                "tertiary": question.get('assessment_criteria_3', 'technical_accuracy')
            },
            "collaboration_requirements": {
                "level": question.get('collaboration_indicator', 'medium'),
                "team_size": get_team_size(question.get('collaboration_indicator', 'medium')),
                "interaction_required": question.get('collaboration_indicator', 'medium') != 'low'
            },
            "scoring": {
                "max_points": 5,
                "rubric_levels": [
                    {"level": 5, "description": "Excellent", "criteria": "Exceptional demonstration of all criteria"},
                    {"level": 4, "description": "Good", "criteria": "Strong demonstration with minor gaps"},
                    {"level": 3, "description": "Satisfactory", "criteria": "Meets basic expectations"},
                    {"level": 2, "description": "Needs Improvement", "criteria": "Below expectations"},
                    {"level": 1, "description": "Unsatisfactory", "criteria": "Minimal demonstration"}
                ]
            },
            "metadata": {
                "dimension": question.get('dimension', 'creativity'),
                "subcategory": question.get('subcategory', 'innovation_problem_solving'),
                "target_year_level": question.get('target_year_level', '1-3'),
                "context_similarity_score": question.get('generation_context', {}).get('top_similarity_score', 0.0),
                "generation_timestamp": datetime.now().isoformat()
            },
            "frontend_display": {
                "render_type": map_question_type_to_component(question.get('question_type', '')),
                "layout_hints": {
                    "full_width": True,
                    "show_timer": True,
                    "allow_drafts": True,
                    "rich_text_editor": question.get('question_type') in ['essay', 'reflection', 'analysis']
                },
                "ui_elements": {
                    "progress_indicator": True,
                    "word_count": question.get('question_type') in ['essay', 'reflection'],
                    "collaboration_tools": question.get('collaboration_indicator', 'medium') != 'low'
                }
            }
        }
        
        quiz_json["questions"].append(question_obj)
    
    return quiz_json

def estimate_difficulty(question: Dict) -> str:
    """Estimate question difficulty based on various factors"""
    year_level = question.get('target_year_level', '1')
    time_limit = question.get('time_limit_minutes', 15)
    collaboration = question.get('collaboration_indicator', 'medium')
    
    if isinstance(year_level, str) and '-' in year_level:
        max_year = int(year_level.split('-')[-1])
    else:
        max_year = int(str(year_level).split('-')[0]) if str(year_level) else 1
    
    score = 0
    if max_year >= 4: score += 2
    elif max_year >= 3: score += 1
    
    if time_limit >= 20: score += 2
    elif time_limit >= 15: score += 1
    
    if collaboration == 'high': score += 1
    
    if score >= 4: return "advanced"
    elif score >= 2: return "intermediate"
    else: return "beginner"

def get_team_size(collaboration_level: str) -> str:
    """Get recommended team size based on collaboration level"""
    if collaboration_level == 'high': return "3-4 students"
    elif collaboration_level == 'medium': return "2-3 students"
    else: return "Individual work"

def map_question_type_to_component(question_type: str) -> str:
    """Map question type to frontend component"""
    type_mapping = {
        'collaboration_scenario': 'scenario_card',
        'presentation_creativity': 'multimedia_response',
        'academic_creativity': 'essay_editor',
        'design_creativity': 'design_canvas',
        'writing_creativity': 'rich_text_editor',
        'user_centered_design': 'prototype_builder',
        'adaptive_presentation': 'video_response',
        'resourceful_design': 'resource_planner',
        'research_innovation': 'research_proposal',
        'creative_enhancement': 'project_showcase',
        'resourceful_creativity': 'solution_builder',
        'technical_presentation': 'demo_recorder'
    }
    return type_mapping.get(question_type, 'text_area')

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📝 Question Generation System</h1>
        <p>AI-Powered Educational Assessment Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        selected = option_menu(
            "Navigation",
            ["Generate Quiz", "Quiz History", "Analytics", "Export"],
            icons=['plus-circle', 'clock-history', 'graph-up', 'download'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#4285f4", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px"},
                "nav-link-selected": {"background-color": "#4285f4"},
            }
        )
    
    # Initialize RAG system
    if st.session_state.rag_system is None:
        with st.spinner("🚀 Initializing AI system..."):
            st.session_state.rag_system = initialize_rag_system()
    
    if st.session_state.rag_system is None:
        st.error("❌ Failed to initialize the system. Please check your setup.")
        st.stop()
    
    # Main content based on selection
    if selected == "Generate Quiz":
        show_quiz_generation()
    elif selected == "Quiz History":
        show_quiz_history()
    elif selected == "Analytics":
        show_analytics()
    elif selected == "Export":
        show_export_options()

def show_quiz_generation():
    """Main quiz generation interface"""
    
    st.markdown("""
    <div class="info-banner">
        <strong>📋 Quiz Generation Form</strong><br>
        Fill out the details below to generate custom assessment questions using AI.
    </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout for form
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.subheader("📝 Basic Information")
        
        quiz_title = st.text_input(
            "Quiz Title *",
            placeholder="e.g., Creative Problem Solving Assessment",
            help="Enter a descriptive title for your quiz"
        )
        
        quiz_description = st.text_area(
            "Description",
            placeholder="Brief description of the assessment objectives...",
            height=100
        )
        
        teacher_name = st.text_input(
            "Teacher Name",
            placeholder="Your name",
            value=st.session_state.get('teacher_name', '')
        )
        
        course = st.text_input(
            "Course/Subject",
            placeholder="e.g., Computer Science, Web Development",
            value="Computer Science"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.subheader("🎯 Assessment Parameters")
        
        # Get available options from RAG system
        dimensions = ["creativity", "teamwork", "soft_skills", "hard_skills"]
        dimension = st.selectbox(
            "Primary Dimension *",
            dimensions,
            help="Select the main competency dimension to assess"
        )
        
        # Get subcategories based on dimension
        if dimension:
            subcategories = get_subcategories_for_dimension(dimension)
            subcategory = st.selectbox(
                "Subcategory *",
                subcategories,
                help="Specific aspect within the dimension"
            )
        
        year_level = st.selectbox(
            "Target Year Level *",
            ["1", "2", "3", "4", "5", "1-2", "2-3", "3-4", "4-5"],
            index=2,
            help="Student year level for appropriate difficulty"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.subheader("⚙️ Generation Settings")
        
        num_questions = st.slider(
            "Number of Questions",
            min_value=1,
            max_value=10,
            value=3,
            help="How many questions to generate"
        )
        
        question_types = get_available_question_types()
        question_type = st.selectbox(
            "Question Type",
            ["Auto-select"] + question_types,
            help="Specific type of question or let AI choose"
        )
        
        collaboration_level = st.selectbox(
            "Collaboration Level",
            ["low", "medium", "high"],
            index=1,
            help="Level of teamwork required"
        )
        
        difficulty = st.selectbox(
            "Difficulty Level",
            ["beginner", "intermediate", "advanced"],
            index=1
        )
        
        assessment_type = st.selectbox(
            "Assessment Type",
            ["formative", "summative", "diagnostic", "peer_assessment"],
            help="Purpose of the assessment"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.subheader("🎨 Customization")
        
        additional_context = st.text_area(
            "Additional Context",
            placeholder="e.g., Focus on React development, include Agile methodology, emphasize accessibility...",
            height=100,
            help="Specific topics or constraints to include"
        )
        
        prerequisites = st.text_input(
            "Prerequisites",
            placeholder="e.g., Basic JavaScript, HTML/CSS",
            help="Required knowledge (comma-separated)"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Generation button
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button(
            "🚀 Generate Quiz",
            use_container_width=True,
            type="primary"
        )
    
    # Generate questions
    if generate_btn:
        if not quiz_title or not dimension or not subcategory:
            st.error("❌ Please fill in all required fields marked with *")
            return
        
        # Store teacher name in session
        st.session_state.teacher_name = teacher_name
        
        metadata = {
            "title": quiz_title,
            "description": quiz_description,
            "teacher_name": teacher_name,
            "course": course,
            "dimension": dimension,
            "subcategory": subcategory,
            "year_level": year_level,
            "collaboration_level": collaboration_level,
            "difficulty": difficulty,
            "assessment_type": assessment_type,
            "subject": course,
            "prerequisites": [p.strip() for p in prerequisites.split(",") if p.strip()]
        }
        
        with st.spinner("🤖 Generating questions using AI..."):
            try:
                questions = st.session_state.rag_system.generate_question(
                    dimension=dimension,
                    subcategory=subcategory,
                    question_type=None if question_type == "Auto-select" else question_type,
                    target_year_level=year_level,
                    additional_context=additional_context,
                    num_questions=num_questions
                )
                
                # Filter out failed questions
                valid_questions = []
                skipped_count = 0
                for q in questions:
                    if isinstance(q, dict):
                        # Check for errors
                        if q.get('error') or q.get('fallback'):
                            skipped_count += 1
                            st.warning(f"⚠️ Question failed: {q.get('error', 'Unknown error')}")
                            continue
                        
                        # Check for valid question text
                        question_text = q.get('question_text', '').strip()
                        if question_text and question_text not in ['N/A', '', 'null', 'None'] and len(question_text) > 10:
                            valid_questions.append(q)
                        else:
                            skipped_count += 1
                            st.warning(f"⚠️ Question skipped due to invalid or empty text: '{question_text[:50]}...'")
                    else:
                        skipped_count += 1
                        st.warning(f"⚠️ Invalid question format received: {type(q)}")
                
                if skipped_count > 0:
                    st.info(f"ℹ️ Skipped {skipped_count} invalid questions out of {len(questions)} generated")
                
                if valid_questions and len(valid_questions) > 0:
                    st.session_state.generated_questions = valid_questions
                    
                    # Create quiz JSON
                    quiz_json = create_quiz_json(valid_questions, metadata)
                    
                    # Add to history
                    st.session_state.quiz_history.append({
                        "timestamp": datetime.now(),
                        "metadata": metadata,
                        "questions": valid_questions,
                        "quiz_json": quiz_json
                    })
                    
                    st.success(f"✅ Successfully generated {len(valid_questions)} out of {num_questions} requested questions!")
                    show_generated_questions(valid_questions, quiz_json)
                else:
                    st.error("❌ Failed to generate any valid questions. Please try again with different parameters.")
                    
            except Exception as e:
                st.error(f"❌ Error generating questions: {str(e)}")
                st.info("💡 Try using different parameters or check your internet connection.")

def show_generated_questions(questions: List[Dict], quiz_json: Dict):
    """Display generated questions with formatting"""
    
    st.markdown("""
    <div class="success-banner">
        <strong>✅ Quiz Generated Successfully!</strong><br>
        Your questions are ready for review and export.
    </div>
    """, unsafe_allow_html=True)
    
    # Quiz overview
    metadata = quiz_json["quiz_metadata"]
    
    st.subheader("📊 Quiz Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metadata['total_questions']}</h3>
            <p>Questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metadata['estimated_duration_minutes']}</h3>
            <p>Minutes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{quiz_json['scoring_configuration']['total_points']}</h3>
            <p>Total Points</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metadata['difficulty_level'].title()}</h3>
            <p>Difficulty</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Questions display
    st.subheader("📝 Generated Questions")
    
    for i, (question, q_json) in enumerate(zip(questions, quiz_json["questions"]), 1):
        # Check if question has valid content
        question_text = question.get('question_text', '')
        if not question_text or question_text == 'N/A':
            st.error(f"❌ Question {i} failed to generate properly. Please try again.")
            continue
            
        with st.expander(f"Question {i}: {question.get('question_type', 'Question').replace('_', ' ').title()}", expanded=True):
            
            # Clean visual display
            st.markdown(f"""
            <div class="question-card">
                <h4 style="color: #1a73e8; margin-bottom: 1rem;">Question {i}</h4>
                
                <div class="question-text">
                    {question_text}
                </div>
                
                <div class="question-meta">
                    <div class="meta-item">
                        <strong>Type:</strong> {question.get('question_type', 'Unknown').replace('_', ' ').title()}
                    </div>
                    <div class="meta-item">
                        <strong>Time:</strong> {question.get('time_limit_minutes', 15)} minutes
                    </div>
                    <div class="meta-item">
                        <strong>Difficulty:</strong> {q_json.get('difficulty_level', 'intermediate').title()}
                    </div>
                    <div class="meta-item">
                        <strong>Year Level:</strong> {question.get('target_year_level', '1-3')}
                    </div>
                </div>
                
                <div class="question-criteria">
                    <strong style="color: #1a73e8;">Assessment Criteria:</strong>
                    <ul class="criteria-list">
                        <li class="criteria-item">{q_json.get('assessment_criteria', {}).get('primary', 'Problem Solving').replace('_', ' ').title()}</li>
                        <li class="criteria-item">{q_json.get('assessment_criteria', {}).get('secondary', 'Creativity').replace('_', ' ').title()}</li>
                        <li class="criteria-item">{q_json.get('assessment_criteria', {}).get('tertiary', 'Technical Accuracy').replace('_', ' ').title()}</li>
                    </ul>
                </div>
                
                <div style="margin: 1rem 0; padding: 1rem; background: #f1f3f4; border-radius: 8px;">
                    <div style="margin-bottom: 0.5rem;">
                        <strong style="color: #1a73e8;">Collaboration:</strong> 
                        <span style="color: #5f6368;">{q_json.get('collaboration_requirements', {}).get('level', 'medium').title()} ({q_json.get('collaboration_requirements', {}).get('team_size', '2-3 students')})</span>
                    </div>
                    <div>
                        <strong style="color: #1a73e8;">Frontend Component:</strong> 
                        <span style="color: #5f6368; font-family: monospace; background: white; padding: 0.2rem 0.5rem; border-radius: 4px;">{q_json.get('frontend_display', {}).get('render_type', 'text_area')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add tabs for different views
            tab1, tab2 = st.tabs(["📋 Question JSON", "🔧 Full Question Object"])
            
            with tab1:
                st.subheader("📄 Individual Question JSON")
                st.caption("Copy this JSON for your frontend team")
                question_json_str = json.dumps(q_json, indent=2)
                st.code(question_json_str, language="json")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label=f"💾 Download Question {i} JSON",
                        data=question_json_str,
                        file_name=f"question_{i}_{q_json.get('question_id', f'q{i}')}.json",
                        mime="application/json",
                        key=f"download_q_{i}"
                    )
            
            with tab2:
                st.subheader("🔍 Raw Question Data")
                st.caption("Debug view - original question object from AI")
                st.json(question)
    
    # JSON Export Section
    st.subheader("📤 Export Complete Quiz JSON")
    
    st.markdown("""
    <div class="info-banner">
        <strong>📋 For Frontend Team</strong><br>
        Download the complete quiz JSON with all questions, metadata, and frontend configuration.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("� Complete Quiz JSON")
        st.caption("Full quiz structure for frontend integration")
        
    with col2:
        json_str = json.dumps(quiz_json, indent=2)
        st.download_button(
            label="💾 Download Complete Quiz JSON",
            data=json_str,
            file_name=f"quiz_{metadata['quiz_id']}.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
    
    with col3:
        if st.button("📋 Copy JSON to Clipboard", use_container_width=True):
            st.code("JSON copied to display below", language="text")
    
    # Show formatted JSON in expandable section
    with st.expander("🔍 View Complete Quiz JSON Structure"):
        st.caption("This is the complete JSON your frontend team will receive")
        st.json(quiz_json)

def get_subcategories_for_dimension(dimension: str) -> List[str]:
    """Get subcategories for a given dimension"""
    subcategory_map = {
        "creativity": [
            "innovation_problem_solving",
            "algorithm_design", 
            "system_architecture",
            "code_optimization",
            "ux_design"
        ],
        "teamwork": [
            "communication_documentation",
            "code_review_collaboration",
            "leadership_mentoring",
            "conflict_resolution",
            "agile_participation"
        ],
        "soft_skills": [
            "time_management",
            "adaptability_learning",
            "critical_thinking",
            "presentation_communication",
            "project_management"
        ],
        "hard_skills": [
            "programming_languages",
            "software_engineering_principles", 
            "database_management",
            "devops_deployment"
        ]
    }
    return subcategory_map.get(dimension, [])

def get_available_question_types() -> List[str]:
    """Get available question types"""
    return [
        "collaboration_scenario",
        "presentation_creativity",
        "academic_creativity",
        "design_creativity",
        "writing_creativity",
        "user_centered_design",
        "adaptive_presentation",
        "resourceful_design",
        "research_innovation",
        "creative_enhancement",
        "resourceful_creativity",
        "technical_presentation"
    ]

def show_quiz_history():
    """Show quiz generation history"""
    st.subheader("📚 Quiz Generation History")
    
    if not st.session_state.quiz_history:
        st.info("📝 No quizzes generated yet. Create your first quiz in the Generate Quiz tab!")
        return
    
    for i, entry in enumerate(reversed(st.session_state.quiz_history), 1):
        with st.expander(f"Quiz {i}: {entry['metadata']['title']} - {entry['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Teacher:** {entry['metadata']['teacher_name']}")
                st.write(f"**Course:** {entry['metadata']['course']}")
                st.write(f"**Dimension:** {entry['metadata']['dimension']}")
                st.write(f"**Questions:** {len(entry['questions'])}")
            
            with col2:
                st.write(f"**Year Level:** {entry['metadata']['year_level']}")
                st.write(f"**Difficulty:** {entry['metadata']['difficulty']}")
                st.write(f"**Assessment Type:** {entry['metadata']['assessment_type']}")
                
                json_str = json.dumps(entry['quiz_json'], indent=2)
                st.download_button(
                    label="💾 Download JSON",
                    data=json_str,
                    file_name=f"quiz_{entry['quiz_json']['quiz_metadata']['quiz_id']}.json",
                    mime="application/json",
                    key=f"download_{i}"
                )

def show_analytics():
    """Show analytics dashboard"""
    st.subheader("📊 Analytics Dashboard")
    
    if not st.session_state.quiz_history:
        st.info("📈 No data to analyze yet. Generate some quizzes first!")
        return
    
    # Create analytics data
    history_df = pd.DataFrame([
        {
            "timestamp": entry["timestamp"],
            "dimension": entry["metadata"]["dimension"],
            "subcategory": entry["metadata"]["subcategory"],
            "num_questions": len(entry["questions"]),
            "difficulty": entry["metadata"]["difficulty"],
            "year_level": entry["metadata"]["year_level"],
            "teacher": entry["metadata"]["teacher_name"]
        }
        for entry in st.session_state.quiz_history
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dimension distribution
        fig1 = px.pie(
            history_df, 
            names='dimension', 
            title='Questions by Dimension',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Difficulty distribution
        fig2 = px.bar(
            history_df.groupby('difficulty').size().reset_index(name='count'),
            x='difficulty',
            y='count',
            title='Questions by Difficulty Level',
            color='difficulty',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Timeline
    if len(history_df) > 1:
        fig3 = px.line(
            history_df.groupby(history_df['timestamp'].dt.date).size().reset_index(name='count'),
            x='timestamp',
            y='count',
            title='Quiz Generation Over Time',
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)

def show_export_options():
    """Show export options"""
    st.subheader("📤 Export Options")
    
    if not st.session_state.quiz_history:
        st.info("📦 No quizzes to export yet.")
        return
    
    st.write("Export your generated quizzes in various formats:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Export All as JSON", use_container_width=True):
            all_quizzes = [entry['quiz_json'] for entry in st.session_state.quiz_history]
            json_str = json.dumps(all_quizzes, indent=2)
            st.download_button(
                label="💾 Download All Quizzes JSON",
                data=json_str,
                file_name=f"all_quizzes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Export Analytics CSV", use_container_width=True):
            if st.session_state.quiz_history:
                analytics_data = []
                for entry in st.session_state.quiz_history:
                    for question in entry['questions']:
                        analytics_data.append({
                            "quiz_id": entry['quiz_json']['quiz_metadata']['quiz_id'],
                            "timestamp": entry['timestamp'],
                            "teacher": entry['metadata']['teacher_name'],
                            "dimension": entry['metadata']['dimension'],
                            "subcategory": entry['metadata']['subcategory'],
                            "question_type": question.get('question_type', ''),
                            "difficulty": entry['metadata']['difficulty'],
                            "year_level": entry['metadata']['year_level'],
                            "time_limit": question.get('time_limit_minutes', 0),
                            "collaboration_level": question.get('collaboration_indicator', '')
                        })
                
                df = pd.DataFrame(analytics_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download Analytics CSV",
                    data=csv,
                    file_name=f"quiz_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col3:
        if st.button("🎯 Export Summary Report", use_container_width=True):
            # Generate summary report
            summary = generate_summary_report()
            st.download_button(
                label="💾 Download Summary Report",
                data=summary,
                file_name=f"quiz_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

def generate_summary_report() -> str:
    """Generate a text summary report"""
    if not st.session_state.quiz_history:
        return "No quiz data available."
    
    total_quizzes = len(st.session_state.quiz_history)
    total_questions = sum(len(entry['questions']) for entry in st.session_state.quiz_history)
    
    # Get most common dimension
    dimensions = [entry['metadata']['dimension'] for entry in st.session_state.quiz_history]
    most_common_dimension = max(set(dimensions), key=dimensions.count)
    
    report = f"""
QUIZ GENERATION SUMMARY REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
- Total Quizzes Generated: {total_quizzes}
- Total Questions Created: {total_questions}
- Most Used Dimension: {most_common_dimension}

BREAKDOWN BY QUIZ:
"""
    
    for i, entry in enumerate(st.session_state.quiz_history, 1):
        report += f"""
Quiz {i}: {entry['metadata']['title']}
- Created: {entry['timestamp'].strftime('%Y-%m-%d %H:%M')}
- Teacher: {entry['metadata']['teacher_name']}
- Dimension: {entry['metadata']['dimension']}
- Questions: {len(entry['questions'])}
- Difficulty: {entry['metadata']['difficulty']}
- Year Level: {entry['metadata']['year_level']}
"""
    
    return report

if __name__ == "__main__":
    main()
