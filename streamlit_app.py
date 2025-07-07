import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
import random
import time
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Soft Skills Assessment Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .category-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1rem 0;
    }
    .question-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .results-container {
        background-color: #e8f5e8;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 2px solid #28a745;
    }
    .score-display {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Question generation functions (simplified versions from your notebook)
def get_question_templates(category):
    """Get templates for generating questions for a specific category"""
    templates = {
        'communication': [
            "I effectively {action} when {context}.",
            "I am skilled at {action} {modifier}.",
            "I {action} {audience} {modifier}.",
            "I find it easy to {action} even when {challenge}.",
            "When {situation}, I {action} {modifier}."
        ],
        'leadership': [
            "I {leadership_action} to {leadership_outcome}.",
            "I am effective at {leadership_skill} in {leadership_context}.",
            "When facing {leadership_challenge}, I {leadership_response}.",
            "My team members would say I {leadership_quality}.",
            "I {leadership_frequency} {leadership_action} to ensure {leadership_goal}."
        ],
        'time_management': [
            "I {time_action} to {time_outcome}.",
            "I effectively {time_skill} when {time_context}.",
            "I {time_frequency} {time_practice} to maximize productivity.",
            "When dealing with {time_challenge}, I {time_strategy}.",
            "I maintain {time_quality} by {time_method}."
        ],
        'analytical': [
            "When analyzing {analysis_object}, I {analysis_action} {analysis_modifier}.",
            "I am skilled at {analysis_skill} to {analysis_purpose}.",
            "I {analysis_frequency} {analysis_practice} when solving problems.",
            "When presented with {analysis_input}, I {analysis_process} before {analysis_output}.",
            "I can effectively {analysis_method} to {analysis_goal}."
        ]
    }
    return templates.get(category, [])

def get_question_components(category):
    """Get components for filling templates for a specific category"""
    components = {
        'communication': {
            "action": ["communicate", "listen", "express ideas", "provide feedback", "ask questions"],
            "context": ["in team meetings", "with senior management", "with clients", "in high-pressure situations"],
            "modifier": ["clearly and concisely", "with confidence", "in a structured manner", "with empathy"],
            "audience": ["team members", "stakeholders", "clients", "management"],
            "challenge": ["under time constraints", "facing resistance", "dealing with complex topics"],
            "situation": ["in conflict situations", "during project discussions", "in performance reviews"]
        },
        'leadership': {
            "leadership_action": ["motivate team members", "set clear expectations", "delegate responsibilities"],
            "leadership_outcome": ["achieve team goals", "improve team performance", "build a positive culture"],
            "leadership_skill": ["making difficult decisions", "coaching team members", "managing change"],
            "leadership_context": ["challenging times", "periods of growth", "organizational changes"],
            "leadership_challenge": ["team conflicts", "performance issues", "resource constraints"],
            "leadership_response": ["seek input from all stakeholders", "make decisive judgments", "communicate transparently"],
            "leadership_quality": ["inspire them to do their best work", "provide clear direction", "listen to their concerns"],
            "leadership_frequency": ["consistently", "regularly", "proactively"],
            "leadership_goal": ["team success", "individual growth", "high-quality outcomes"]
        },
        'time_management': {
            "time_action": ["prioritize tasks", "create schedules", "set clear deadlines"],
            "time_outcome": ["meet deadlines consistently", "maximize productivity", "reduce stress"],
            "time_skill": ["managing multiple deadlines", "planning my workday", "estimating task duration"],
            "time_context": ["working under pressure", "handling multiple projects", "faced with interruptions"],
            "time_frequency": ["consistently", "regularly", "daily"],
            "time_practice": ["use to-do lists", "break large tasks into smaller steps", "set specific goals"],
            "time_challenge": ["unexpected interruptions", "shifting priorities", "tight deadlines"],
            "time_strategy": ["reassess priorities", "communicate timeline changes", "find efficient shortcuts"],
            "time_quality": ["a well-organized schedule", "clear priorities", "focus during work hours"],
            "time_method": ["planning ahead", "using productivity tools", "setting boundaries"]
        },
        'analytical': {
            "analysis_object": ["data", "problems", "complex situations", "project requirements"],
            "analysis_action": ["identify patterns", "draw logical conclusions", "evaluate options"],
            "analysis_modifier": ["systematically", "objectively", "thoroughly"],
            "analysis_skill": ["breaking down complex problems", "interpreting data", "identifying connections"],
            "analysis_purpose": ["find optimal solutions", "make informed decisions", "identify improvement opportunities"],
            "analysis_frequency": ["consistently", "methodically", "routinely"],
            "analysis_practice": ["gather all relevant information", "consider alternative explanations", "test assumptions"],
            "analysis_input": ["conflicting information", "incomplete data", "complex problems"],
            "analysis_process": ["identify key factors", "evaluate different perspectives", "apply logical frameworks"],
            "analysis_output": ["making recommendations", "drawing conclusions", "implementing solutions"],
            "analysis_method": ["use data visualization", "apply statistical methods", "conduct root cause analysis"],
            "analysis_goal": ["solve complex problems", "identify improvement opportunities", "optimize processes"]
        }
    }
    return components.get(category, {})

def fill_template_with_components(template, components):
    """Fill a template with randomly selected components"""
    filled_template = template
    placeholders = re.findall(r'\{([^}]+)\}', template)
    
    for placeholder in placeholders:
        if placeholder in components:
            replacement = random.choice(components[placeholder])
            filled_template = filled_template.replace(f"{{{placeholder}}}", replacement)
    
    return filled_template

def generate_questions_with_templates(category, n=10):
    """Generate questions using templates and components"""
    templates = get_question_templates(category)
    components = get_question_components(category)
    
    if not templates or not components:
        return []
    
    questions = []
    attempts = 0
    max_attempts = n * 5
    
    while len(questions) < n and attempts < max_attempts:
        attempts += 1
        template = random.choice(templates)
        filled_question = fill_template_with_components(template, components)
        
        if filled_question not in questions:
            questions.append(filled_question)
    
    return questions

def generate_questions_with_huggingface(category, n=10):
    """Generate questions using Hugging Face API"""
    try:
        API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "").strip()
        
        if not API_TOKEN or API_TOKEN == "your_token_here":
            st.info("💡 **AI-powered generation requires a Hugging Face API token.**")
            st.markdown("""
            **To enable AI-powered question generation:**
            1. Visit [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
            2. Create a free account and generate a token
            3. Add your token to the `.env` file
            4. Restart the app
            
            **For now, using template-based generation...**
            """)
            return generate_questions_with_templates(category, n)
        
        category_prompts = {
            'communication': f"Generate {n} unique assessment questions for evaluating communication skills. Each question should be phrased as a statement that can be rated on a scale from 1 (strongly disagree) to 5 (strongly agree). Focus on professional communication in workplace settings.",
            'leadership': f"Generate {n} unique assessment questions for evaluating leadership skills. Each question should be phrased as a statement that can be rated on a scale from 1 (strongly disagree) to 5 (strongly agree). Cover different aspects of leadership including vision, motivation, delegation, and team development.",
            'time_management': f"Generate {n} unique assessment questions for evaluating time management skills. Each question should be phrased as a statement that can be rated on a scale from 1 (strongly disagree) to 5 (strongly agree). Include questions about prioritization, planning, efficiency, and avoiding procrastination.",
            'analytical': f"Generate {n} unique assessment questions for evaluating analytical skills. Each question should be phrased as a statement that can be rated on a scale from 1 (strongly disagree) to 5 (strongly agree). Cover aspects such as problem-solving, data analysis, logical reasoning, and critical thinking."
        }
        
        prompt = category_prompts.get(category, "")
        
        API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-xxl"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7
            }
        }
        
        with st.spinner(f"Generating {category} questions using AI..."):
            response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                generated_text = result[0]["generated_text"]
            else:
                generated_text = str(result)
            
            raw_questions = [q.strip() for q in generated_text.split('\n') if q.strip()]
            
            questions = []
            for q in raw_questions:
                if re.match(r'^\d+\.?\s+', q):
                    q = re.sub(r'^\d+\.?\s+', '', q)
                questions.append(q)
            
            return questions[:n]
        elif response.status_code == 401:
            st.error("🔐 **Authentication Error**: Invalid Hugging Face API token. Please check your token in the `.env` file.")
            st.markdown("""
            **To fix this:**
            1. Visit [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
            2. Generate a new token or verify your existing one
            3. Update the `.env` file with the correct token
            4. Restart the app
            
            **Using template-based generation for now...**
            """)
            return generate_questions_with_templates(category, n)
        elif response.status_code == 503:
            st.warning("🚧 **Model Loading**: The AI model is loading. This can take a few minutes. Using template-based generation for now...")
            return generate_questions_with_templates(category, n)
        else:
            st.error(f"❌ **API Error** (Status {response.status_code}): {response.text}")
            st.info("🔄 **Falling back to template-based generation...**")
            return generate_questions_with_templates(category, n)
            
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 **Connection Error**: Unable to connect to Hugging Face API. {str(e)}")
        st.info("🔄 **Using template-based generation instead...**")
        return generate_questions_with_templates(category, n)
    except Exception as e:
        st.error(f"❌ **Unexpected Error**: {str(e)}")
        st.info("🔄 **Using template-based generation instead...**")
        return generate_questions_with_templates(category, n)

def calculate_results(responses):
    """Calculate assessment results"""
    if not responses:
        return None
    
    total_score = sum(responses.values())
    max_possible = len(responses) * 5
    average_score = total_score / len(responses)
    percentage = (average_score / 5) * 100
    
    # Generate feedback based on score
    if average_score >= 4.5:
        feedback = "Outstanding! You demonstrate excellent skills in this area."
        color = "#28a745"
    elif average_score >= 3.5:
        feedback = "Good job! You have solid skills with some room for improvement."
        color = "#17a2b8"
    elif average_score >= 2.5:
        feedback = "You have moderate skills. Consider focusing on development in this area."
        color = "#ffc107"
    else:
        feedback = "This appears to be an area for growth. Consider seeking resources to develop your skills."
        color = "#dc3545"
    
    return {
        'total_score': total_score,
        'max_possible': max_possible,
        'average_score': average_score,
        'percentage': percentage,
        'feedback': feedback,
        'color': color
    }

def create_score_visualization(results_by_category):
    """Create visualization of scores by category"""
    categories = list(results_by_category.keys())
    scores = [results_by_category[cat]['percentage'] for cat in categories]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Your Scores'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Soft Skills Assessment Results",
        height=500
    )
    
    return fig

# Main Streamlit App
def main():
    st.markdown('<h1 class="main-header">🎯 Soft Skills Assessment Tool</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Welcome to the Soft Skills Assessment Tool!** 
    
    This application evaluates your skills in four key areas:
    - 📢 Communication Skills
    - 👥 Leadership Skills  
    - ⏰ Time Management Skills
    - 🧠 Analytical Skills
    
    Choose your preferred question generation method and take the assessment to get personalized feedback.
    """)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Assessment Configuration")
        
        # Question generation method
        generation_method = st.selectbox(
            "Question Generation Method:",
            ["Template-Based (Fast)", "AI-Powered (Hugging Face)"],
            help="Template-based is faster, AI-powered provides more variety but requires API token"
        )
        
        use_llm = generation_method == "AI-Powered (Hugging Face)"
        
        # Show API token status for AI method
        if use_llm:
            api_token = os.environ.get("HUGGINGFACE_API_TOKEN", "").strip()
            if not api_token or api_token == "your_token_here":
                st.warning("⚠️ No valid API token found")
                st.markdown("**Need help?** [Get free token](https://huggingface.co/settings/tokens)")
            else:
                st.success("✅ API token configured")
        
        st.markdown("---")
        
        # Number of questions per category
        questions_per_category = st.slider(
            "Questions per Category:",
            min_value=3,
            max_value=15,
            value=5,
            help="Number of questions to generate for each skill category"
        )
        
        # Categories to include
        st.subheader("Categories to Include:")
        include_communication = st.checkbox("📢 Communication", value=True)
        include_leadership = st.checkbox("👥 Leadership", value=True)
        include_time_management = st.checkbox("⏰ Time Management", value=True)
        include_analytical = st.checkbox("🧠 Analytical", value=True)
        
        # Generate assessment button
        if st.button("🚀 Generate New Assessment", type="primary"):
            st.session_state.assessment_generated = True
            st.session_state.responses = {}
            st.session_state.results_calculated = False
    
    # Generate assessment if requested
    if st.session_state.get('assessment_generated', False):
        
        # Determine which categories to include
        selected_categories = []
        if include_communication:
            selected_categories.append('communication')
        if include_leadership:
            selected_categories.append('leadership')
        if include_time_management:
            selected_categories.append('time_management')
        if include_analytical:
            selected_categories.append('analytical')
        
        if not selected_categories:
            st.error("Please select at least one category to assess!")
            return
        
        # Generate questions for selected categories
        all_questions = {}
        
        for category in selected_categories:
            with st.spinner(f"Generating {category.replace('_', ' ').title()} questions..."):
                if use_llm:
                    questions = generate_questions_with_huggingface(category, questions_per_category)
                else:
                    questions = generate_questions_with_templates(category, questions_per_category)
                
                all_questions[category] = questions
        
        # Store questions in session state
        st.session_state.all_questions = all_questions
        st.session_state.selected_categories = selected_categories
        
        # Display assessment form
        st.markdown("---")
        st.markdown('<h2 class="category-header">📝 Assessment Questions</h2>', unsafe_allow_html=True)
        
        with st.form("assessment_form"):
            responses = {}
            question_counter = 1
            
            for category in selected_categories:
                st.markdown(f'<h3 class="category-header">{category.replace("_", " ").title()} Skills</h3>', unsafe_allow_html=True)
                
                for i, question in enumerate(all_questions[category]):
                    st.markdown(f'<div class="question-container">', unsafe_allow_html=True)
                    
                    response = st.radio(
                        f"**Question {question_counter}:** {question}",
                        options=[1, 2, 3, 4, 5],
                        format_func=lambda x: {
                            1: "1 - Strongly Disagree",
                            2: "2 - Disagree", 
                            3: "3 - Neutral",
                            4: "4 - Agree",
                            5: "5 - Strongly Agree"
                        }[x],
                        key=f"{category}_{i}",
                        horizontal=True,
                        index=2  # Default to "3 - Neutral"
                    )
                    
                    responses[f"{category}_{i}"] = response
                    question_counter += 1
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Submit button
            submitted = st.form_submit_button("📊 Calculate Results", type="primary", use_container_width=True)
            
            if submitted:
                st.session_state.responses = responses
                st.session_state.results_calculated = True
                # Debug: Show what responses were captured
                st.write("Debug - Captured responses:", responses)
                st.rerun()
    
    # Display results if calculated
    if st.session_state.get('results_calculated', False) and 'responses' in st.session_state:
        st.markdown("---")
        st.markdown('<h2 class="category-header">📈 Your Assessment Results</h2>', unsafe_allow_html=True)
        
        # Calculate results by category
        results_by_category = {}
        
        for category in st.session_state.selected_categories:
            category_responses = {k: v for k, v in st.session_state.responses.items() if k.startswith(category)}
            if category_responses:
                results_by_category[category.replace('_', ' ').title()] = calculate_results(category_responses)
        
        # Display overall results
        if results_by_category:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Radar chart
                fig = create_score_visualization(results_by_category)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Detailed results
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                
                for category, results in results_by_category.items():
                    st.markdown(f"""
                    **{category}:**
                    <div class="score-display" style="color: {results['color']}">
                        {results['average_score']:.1f}/5 ({results['percentage']:.1f}%)
                    </div>
                    {results['feedback']}
                    """, unsafe_allow_html=True)
                    st.markdown("---")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Export results
            if st.button("📥 Download Results as CSV"):
                results_df = pd.DataFrame([
                    {
                        'Category': category,
                        'Average Score': results['average_score'],
                        'Percentage': results['percentage'],
                        'Feedback': results['feedback']
                    }
                    for category, results in results_by_category.items()
                ])
                
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="soft_skills_assessment_results.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    # Initialize session state
    if 'assessment_generated' not in st.session_state:
        st.session_state.assessment_generated = False
    if 'results_calculated' not in st.session_state:
        st.session_state.results_calculated = False
    
    main()
