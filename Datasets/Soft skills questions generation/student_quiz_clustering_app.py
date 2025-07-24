import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import os
import json
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Soft Skills Assessment & Clustering",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load questions from CSV files
@st.cache_data
def load_questions():
    questions = {}
    categories = {
        'communication': 'communication_questions.csv',
        'leadership': 'leadership_questions.csv',
        'time_management': 'time_management_questions.csv',
        'analytical': 'analytical_questions.csv'
    }
    
    for category, filename in categories.items():
        try:
            file_path = os.path.join("data", filename)
            df = pd.read_csv(file_path)
            questions[category] = df
        except Exception as e:
            st.error(f"Error loading {filename}: {e}")
            # Create sample questions if file not found
            questions[category] = pd.DataFrame({
                'question': [f"Sample {category} question {i}?" for i in range(1, 6)],
                'option_a': [f"{category} option A {i}" for i in range(1, 6)],
                'option_b': [f"{category} option B {i}" for i in range(1, 6)],
                'option_c': [f"{category} option C {i}" for i in range(1, 6)],
                'option_d': [f"{category} option D {i}" for i in range(1, 6)],
                'correct_option': ['a', 'b', 'c', 'd', 'a']
            })
    
    return questions

# Load existing student data for clustering
@st.cache_data
def load_student_data():
    # In a real application, load this from a database
    # For now, create simulated data for comparison
    np.random.seed(42)
    n_students = 100
    
    # Create student data with some patterns for realistic clusters
    data = {
        'student_id': [f"STU{i:03d}" for i in range(1, n_students+1)],
        'student_name': [f"Student {i}" for i in range(1, n_students+1)],
        'communication_score': np.random.uniform(1, 5, n_students).round(2),
        'leadership_score': np.random.uniform(1, 5, n_students).round(2),
        'time_management_score': np.random.uniform(1, 5, n_students).round(2),
        'analytical_score': np.random.uniform(1, 5, n_students).round(2)
    }
    
    # Create patterns for clustering
    # Group 1: High communication, leadership (extroverts)
    data['communication_score'][:25] += 0.7
    data['leadership_score'][:25] += 0.5
    # Group 2: High analytical, time management (analytical planners)
    data['analytical_score'][25:50] += 0.7
    data['time_management_score'][25:50] += 0.6
    # Group 3: High leadership, low time management (natural leaders)
    data['leadership_score'][50:75] += 0.8
    data['time_management_score'][50:75] -= 0.3
    
    # Clip values to ensure they stay within 1-5 range
    for score_col in ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']:
        data[score_col] = np.clip(data[score_col], 1.0, 5.0)
    
    df = pd.DataFrame(data)
    df['overall_score'] = df[['communication_score', 'leadership_score', 
                            'time_management_score', 'analytical_score']].mean(axis=1)
    
    return df

# Function to get cluster descriptions
def get_cluster_descriptions(kmeans_centers):
    descriptions = {}
    for i, center in enumerate(kmeans_centers):
        skills = ['Communication', 'Leadership', 'Time Management', 'Analytical']
        strengths = []
        weaknesses = []
        
        # Find strengths and weaknesses
        for j, score in enumerate(center):
            if score > 0.5:
                strengths.append(skills[j])
            elif score < -0.5:
                weaknesses.append(skills[j])
        
        if not strengths:
            strengths.append("Balanced profile")
        if not weaknesses:
            weaknesses.append("No significant weaknesses")
        
        # Create description
        descriptions[i] = {
            'name': f"Cluster {i}",
            'strengths': strengths,
            'weaknesses': weaknesses,
            'description': f"Students in this cluster typically excel at {', '.join(strengths)}" + 
                          (f" but may need improvement in {', '.join(weaknesses)}." if weaknesses[0] != "No significant weaknesses" else ".")
        }
        
        # Give more specific names to clusters
        if 'Communication' in strengths and 'Leadership' in strengths:
            descriptions[i]['name'] = "Social Leaders"
        elif 'Analytical' in strengths and 'Time Management' in strengths:
            descriptions[i]['name'] = "Analytical Planners"
        elif 'Leadership' in strengths and 'Time Management' in weaknesses:
            descriptions[i]['name'] = "Natural Leaders"
        elif strengths[0] == "Balanced profile":
            descriptions[i]['name'] = "Well-Rounded Performers"
    
    return descriptions

# Function to perform clustering and get recommendations
def perform_clustering(student_scores, all_students_df):
    # Combine the new student with existing students
    combined_df = pd.concat([all_students_df, student_scores], ignore_index=True)
    
    # Get score columns
    score_columns = ['communication_score', 'leadership_score', 
                   'time_management_score', 'analytical_score']
    
    # Scale the scores
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(combined_df[score_columns])
    
    # Determine optimal number of clusters
    silhouette_scores = []
    k_range = range(2, 6)
    
    for k in k_range:
        kmeans_test = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_test.fit(X_scaled)
        cluster_labels = kmeans_test.predict(X_scaled)
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        silhouette_scores.append(silhouette_avg)
    
    optimal_k = k_range[silhouette_scores.index(max(silhouette_scores))]
    
    # Perform KMeans clustering with optimal K
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    combined_df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Get the cluster center details
    centers = kmeans.cluster_centers_
    
    # Get cluster descriptions
    cluster_descriptions = get_cluster_descriptions(centers)
    
    # Get the new student's cluster
    new_student_cluster = combined_df.iloc[-1]['cluster']
    
    # Get cluster recommendations
    recommendations = {
        'cluster': int(new_student_cluster),
        'cluster_name': cluster_descriptions[new_student_cluster]['name'],
        'description': cluster_descriptions[new_student_cluster]['description'],
        'strengths': cluster_descriptions[new_student_cluster]['strengths'],
        'weaknesses': cluster_descriptions[new_student_cluster]['weaknesses'],
    }
    
    # Visualize with PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # Create PCA plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot all students
    for i in range(optimal_k):
        mask = combined_df['cluster'] == i
        ax.scatter(
            X_pca[mask][:-1, 0] if i == new_student_cluster else X_pca[mask, 0],
            X_pca[mask][:-1, 1] if i == new_student_cluster else X_pca[mask, 1],
            alpha=0.6, 
            label=f"{cluster_descriptions[i]['name']}"
        )
    
    # Highlight the new student with a star marker
    ax.scatter(
        X_pca[-1, 0], 
        X_pca[-1, 1], 
        marker='*', 
        s=200, 
        color='red',
        edgecolor='black',
        label="You"
    )
    
    # Add labels and legend
    ax.set_title('Student Clusters Visualization (PCA)')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.legend()
    
    # Generate skill-specific recommendations
    skill_recommendations = {}
    student_scores_normalized = (X_scaled[-1] - X_scaled[:-1].mean(axis=0)) / X_scaled[:-1].std(axis=0)
    
    skill_map = {
        0: 'communication',
        1: 'leadership',
        2: 'time_management',
        3: 'analytical'
    }
    
    for i, score in enumerate(student_scores_normalized):
        skill = skill_map[i]
        
        if score < -0.5:
            if skill == 'communication':
                skill_recommendations[skill] = "Work on your communication skills through public speaking practice, active listening exercises, and group discussions."
            elif skill == 'leadership':
                skill_recommendations[skill] = "Develop leadership abilities by taking initiative in group projects, practicing decision-making, and studying leadership principles."
            elif skill == 'time_management':
                skill_recommendations[skill] = "Improve time management by using planning tools, prioritizing tasks, and breaking down large projects into manageable steps."
            elif skill == 'analytical':
                skill_recommendations[skill] = "Enhance analytical thinking through problem-solving exercises, logical reasoning practice, and data analysis projects."
    
    recommendations['skill_specific'] = skill_recommendations
    
    return recommendations, fig

# Quiz section
def run_quiz():
    st.title("🧩 Soft Skills Assessment Quiz")
    st.write("Complete this assessment to discover your soft skills profile and get personalized recommendations.")
    
    # Get questions
    questions = load_questions()
    
    # Initialize session state for tracking quiz progress
    if 'current_category' not in st.session_state:
        st.session_state.current_category = 'communication'
        st.session_state.question_idx = 0
        st.session_state.answers = {
            'communication': [],
            'leadership': [],
            'time_management': [],
            'analytical': []
        }
        st.session_state.scores = {
            'communication': 0,
            'leadership': 0,
            'time_management': 0,
            'analytical': 0
        }
        st.session_state.quiz_complete = False
    
    # Order of categories
    categories = ['communication', 'leadership', 'time_management', 'analytical']
    
    # Display progress
    current_category_idx = categories.index(st.session_state.current_category)
    st.progress((current_category_idx * 5 + st.session_state.question_idx + 1) / 20)
    
    # Display current category
    st.subheader(f"{st.session_state.current_category.title()} Skills")
    
    # Get current question
    category_questions = questions[st.session_state.current_category]
    if st.session_state.question_idx < len(category_questions):
        question = category_questions.iloc[st.session_state.question_idx]
        
        # Display question
        st.write(f"**Q{current_category_idx * 5 + st.session_state.question_idx + 1}:** {question['question']}")
        
        # Display options
        option = st.radio("Select your answer:", 
                         [question['option_a'], question['option_b'], question['option_c'], question['option_d']],
                         key=f"{st.session_state.current_category}_{st.session_state.question_idx}")
        
        # Map selected option to a, b, c, d
        option_mapping = {
            question['option_a']: 'a',
            question['option_b']: 'b',
            question['option_c']: 'c',
            question['option_d']: 'd'
        }
        selected_option = option_mapping[option]
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        
        with col2:
            if st.button("Next Question"):
                # Record answer
                st.session_state.answers[st.session_state.current_category].append(selected_option)
                
                # Update score based on correct answer (in a real quiz, scoring would be more nuanced)
                if selected_option == question['correct_option']:
                    st.session_state.scores[st.session_state.current_category] += 1
                
                # Move to next question or category
                st.session_state.question_idx += 1
                if st.session_state.question_idx >= 5:  # Using 5 questions per category for simplicity
                    next_category_idx = current_category_idx + 1
                    if next_category_idx < len(categories):
                        st.session_state.current_category = categories[next_category_idx]
                        st.session_state.question_idx = 0
                    else:
                        # Quiz complete
                        st.session_state.quiz_complete = True
                
                # Rerun to update the page
                st.rerun()
    
    # Show results when quiz is complete
    if st.session_state.quiz_complete:
        show_results()

# Function to show quiz results and clustering
def show_results():
    st.title("🎯 Your Soft Skills Assessment Results")
    
    # Calculate normalized scores (on a scale of 1-5)
    normalized_scores = {}
    for category, score in st.session_state.scores.items():
        # Convert score from 0-5 range to 1-5 range
        normalized_scores[f"{category}_score"] = 1 + (score / 5) * 4
    
    # Create a DataFrame for the student
    student_data = {
        'student_id': [f"NEW_{datetime.now().strftime('%Y%m%d%H%M%S')}"],
        'student_name': ["You"],
        'communication_score': [normalized_scores['communication_score']],
        'leadership_score': [normalized_scores['leadership_score']],
        'time_management_score': [normalized_scores['time_management_score']],
        'analytical_score': [normalized_scores['analytical_score']]
    }
    student_df = pd.DataFrame(student_data)
    
    # Calculate overall score
    student_df['overall_score'] = student_df[['communication_score', 'leadership_score', 
                                            'time_management_score', 'analytical_score']].mean(axis=1)
    
    # Display scores
    st.subheader("Your Scores")
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create a radar chart of scores
        categories = ['Communication', 'Leadership', 'Time Management', 'Analytical']
        values = [normalized_scores['communication_score'], 
                normalized_scores['leadership_score'],
                normalized_scores['time_management_score'],
                normalized_scores['analytical_score']]
        
        # Close the radar plot
        values_closed = values + [values[0]]
        categories_closed = categories + [categories[0]]
        
        # Create angles for each category
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles_closed = angles + [angles[0]]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'polar': True})
        ax.plot(angles_closed, values_closed, 'o-', linewidth=2)
        ax.fill(angles_closed, values_closed, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles), categories)
        ax.set_ylim(0, 5)
        ax.grid(True)
        ax.set_title("Your Soft Skills Profile", size=20, pad=20)
        st.pyplot(fig)
    
    with col2:
        st.write("Score breakdown (scale of 1-5):")
        for category, normalized_score in normalized_scores.items():
            skill_name = category.replace('_score', '').title()
            st.metric(skill_name, f"{normalized_score:.1f}/5.0")
        
        st.metric("Overall Score", f"{student_df['overall_score'].values[0]:.1f}/5.0")
    
    # Perform clustering
    st.subheader("🧩 Your Skills Cluster Analysis")
    
    # Get existing student data
    all_students_df = load_student_data()
    
    # Perform clustering and get recommendations
    recommendations, cluster_fig = perform_clustering(student_df, all_students_df)
    
    # Display the cluster information
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.write(f"**Your Profile Cluster:** {recommendations['cluster_name']}")
        st.write(recommendations['description'])
        
        # Display strengths and weaknesses
        st.write("**Strengths:**")
        for strength in recommendations['strengths']:
            st.write(f"- {strength}")
            
        st.write("**Areas for Development:**")
        for weakness in recommendations['weaknesses']:
            if weakness != "No significant weaknesses":
                st.write(f"- {weakness}")
            else:
                st.write(f"- {weakness}")
    
    with col2:
        # Display the PCA plot
        st.pyplot(cluster_fig)
    
    # Display skill-specific recommendations if any
    if recommendations['skill_specific']:
        st.subheader("📈 Personalized Improvement Recommendations")
        for skill, recommendation in recommendations['skill_specific'].items():
            st.write(f"**{skill.title()}:** {recommendation}")
    
    # Option to retake the quiz
    if st.button("Retake Assessment"):
        # Reset session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main app
def main():
    st.sidebar.title("Soft Skills Assessment & Clustering")
    st.sidebar.image("https://img.icons8.com/color/96/000000/mind-map.png", width=100)
    
    # About section in sidebar
    st.sidebar.subheader("About")
    st.sidebar.info(
        "This application helps students assess their soft skills "
        "through a quiz and then uses machine learning to cluster them "
        "based on their skills profile, providing personalized recommendations."
    )
    
    # Run the quiz or show results if quiz is complete
    if 'quiz_complete' in st.session_state and st.session_state.quiz_complete:
        show_results()
    else:
        run_quiz()

if __name__ == "__main__":
    main()
