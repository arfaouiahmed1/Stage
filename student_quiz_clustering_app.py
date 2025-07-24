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

# Initialize session state for storing students who took the quiz
if 'students_who_took_quiz' not in st.session_state:
    st.session_state.students_who_took_quiz = pd.DataFrame(columns=[
        'student_id', 'student_name', 'gender', 'age', 'nationality',
        'communication_score', 'leadership_score', 'time_management_score', 
        'analytical_score', 'overall_score', 'quiz_timestamp'
    ])

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
            file_path = os.path.join("Datasets", "Soft skills questions generation", "data", filename)
            df = pd.read_csv(file_path)
            
            # Check if the file has the necessary structure and pick first 5 questions
            if 'question' in df.columns:
                # Select up to 5 questions for this category
                df = df.head(5)
                
                # Add placeholder options since they don't exist in your CSV
                df['option_a'] = "Strongly Agree"
                df['option_b'] = "Agree"
                df['option_c'] = "Neutral"
                df['option_d'] = "Disagree"  
                df['option_e'] = "Strongly Disagree"
                df['correct_option'] = 'a'  # Default to 'a' as correct for self-assessment
                
                questions[category] = df
            else:
                raise ValueError(f"CSV does not have expected 'question' column")
                
        except Exception as e:
            st.error(f"Error loading {filename}: {e}")
            # Create sample questions if file not found
            questions[category] = pd.DataFrame({
                'question': [f"Sample {category} question {i}?" for i in range(1, 6)],
                'option_a': [f"Strongly Agree" for i in range(1, 6)],
                'option_b': [f"Agree" for i in range(1, 6)],
                'option_c': [f"Neutral" for i in range(1, 6)],
                'option_d': [f"Disagree" for i in range(1, 6)],
                'option_e': [f"Strongly Disagree" for i in range(1, 6)],
                'correct_option': ['a', 'a', 'a', 'a', 'a']  # For self-assessment, no right/wrong
            })
    
    return questions

# Load existing student data for clustering
@st.cache_data
def load_student_data():
    # First, try to load from students_quiz_results.csv which contains all previous quiz takers
    try:
        saved_path = "students_quiz_results.csv"
        if os.path.exists(saved_path):
            df = pd.read_csv(saved_path)
            return df
    except Exception as e:
        pass  # If this fails, try the next method
        
    # Next, try to load from the dataset directory
    try:
        # Look in multiple possible locations for the student dataset
        possible_paths = [
            os.path.join("Datasets", "data", "students_dataset.csv"),
            os.path.join("Datasets", "Soft skills questions generation", "data", "students_dataset.csv"),
            os.path.join("data", "students_dataset.csv"),
            "students_dataset.csv"
        ]
        
        # Try each path
        df = None
        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_csv(path)
                break
                
        if df is not None:
            # Map the columns to our expected format
            # The CSV has columns: first_name, last_name, gender, age, nationality, hard_skills, soft_skills, teamwork, creativity, class
            df['student_id'] = df.index.map(lambda x: f"S{x:04d}")
            df['student_name'] = df['first_name'] + " " + df['last_name']
            
            # Map soft skills to our format (map existing skills to our categories)
            # Based on the dataset, we'll map:
            # - soft_skills -> communication_score
            # - teamwork -> leadership_score
            # - creativity -> analytical_score
            # - hard_skills -> time_management_score
            df['communication_score'] = df['soft_skills'].map(lambda x: 1 + x) # Scale from 0-5 to 1-5
            df['leadership_score'] = df['teamwork'].map(lambda x: 1 + x)
            df['analytical_score'] = df['creativity'].map(lambda x: 1 + x)
            df['time_management_score'] = df['hard_skills'].map(lambda x: 1 + x)
            
            # Calculate overall score
            df['overall_score'] = df[['communication_score', 'leadership_score', 
                                     'time_management_score', 'analytical_score']].mean(axis=1)
            
            # Keep only needed columns
            df = df[['student_id', 'student_name', 'communication_score', 
                    'leadership_score', 'time_management_score', 'analytical_score', 'overall_score']]
            
            return df
    except Exception as e:
        pass  # If this fails too, generate synthetic data
    
    # If all else fails, generate synthetic data
    st.warning("Using generated sample data for demonstration purposes.")
    np.random.seed(42)
    n_students = 50  # Fewer students for faster processing
    
    # Create student data with some patterns for realistic clusters
    data = {
        'student_id': [f"STU{i:03d}" for i in range(1, n_students+1)],
        'student_name': [f"Student {i}" for i in range(1, n_students+1)],
        'gender': np.random.choice(['Male', 'Female'], n_students),
        'age': np.random.randint(18, 46, n_students),
        'nationality': np.random.choice(['Tunisian', 'Cameroonian', 'Senegalese', 'Moroccan', 
                                       'Algerian', 'Ivorian', 'Malian', 'Egyptian', 'Other'], n_students),
        'communication_score': np.random.uniform(1, 5, n_students).round(2),
        'leadership_score': np.random.uniform(1, 5, n_students).round(2),
        'time_management_score': np.random.uniform(1, 5, n_students).round(2),
        'analytical_score': np.random.uniform(1, 5, n_students).round(2)
    }
    
    # Create patterns for clustering
    # Group 1: High communication, leadership (extroverts)
    data['communication_score'][:15] += 0.7
    data['leadership_score'][:15] += 0.5
    # Group 2: High analytical, time management (analytical planners)
    data['analytical_score'][15:30] += 0.7
    data['time_management_score'][15:30] += 0.6
    # Group 3: High leadership, low time management (natural leaders)
    data['leadership_score'][30:45] += 0.8
    data['time_management_score'][30:45] -= 0.3
    
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
        # We now have 7 features: 4 skills + 3 demographic features
        feature_names = ['Communication', 'Leadership', 'Time Management', 'Analytical', 
                        'Gender Diversity', 'Age Diversity', 'Cultural Diversity']
        
        complementary_skills = []  # Skills where students complement each other (high diversity)
        common_skills = []         # Skills that are common (low diversity)
        demographic_diversity = [] # Demographic diversity factors
        
        # In our inverted model:
        # - High values (>0.5) indicate features that have high diversity within this cluster
        # - Low values (<-0.5) indicate features that are similar within this cluster
        
        # Process skill features (first 4)
        for j in range(4):  # First 4 features are skills
            if center[j] > 0.5:
                complementary_skills.append(feature_names[j])
            elif center[j] < -0.5:
                common_skills.append(feature_names[j])
        
        # Process demographic features (last 3)
        for j in range(4, 7):  # Last 3 features are demographics
            if center[j] > 0.3:  # Lower threshold for demographics
                demographic_diversity.append(feature_names[j])
        
        # Default values if lists are empty
        if not complementary_skills:
            complementary_skills.append("No specific complementary skills")
        if not common_skills:
            common_skills.append("No specific common skills")
        
        # Create description
        group_desc = f"Your learning group has a mix of students with varying levels of {', '.join(complementary_skills)} skills"
        
        if common_skills[0] != "No specific common skills":
            group_desc += f", while most students have similar levels of {', '.join(common_skills)} skills."
        else:
            group_desc += "."
            
        if demographic_diversity:
            group_desc += f" The group also has diversity in terms of {', '.join(demographic_diversity).lower()}."
        
        descriptions[i] = {
            'name': f"Group {i+1}",
            'strengths': complementary_skills,
            'weaknesses': common_skills,
            'demographic_diversity': demographic_diversity,
            'description': group_desc
        }
        
        # Give more descriptive names to clusters
        if 'Communication' in complementary_skills and 'Leadership' in complementary_skills:
            descriptions[i]['name'] = "Communication & Leadership Group"
        elif 'Analytical' in complementary_skills and 'Time Management' in complementary_skills:
            descriptions[i]['name'] = "Analytical & Planning Group"
        elif 'Leadership' in complementary_skills:
            descriptions[i]['name'] = "Leadership Focus Group"
        
        # Add demographic modifier if there's significant diversity
        if len(demographic_diversity) >= 2:
            descriptions[i]['name'] = "Diverse " + descriptions[i]['name']
        
        if complementary_skills[0] == "No specific complementary skills" and len(demographic_diversity) >= 2:
            descriptions[i]['name'] = "Demographically Diverse Group"
    
    return descriptions

# Function to perform clustering and get recommendations
def perform_clustering(student_scores, all_students_df):
    # Combine the new student with existing students
    combined_df = pd.concat([all_students_df, student_scores], ignore_index=True)
    
    # If there are no other students in the dataset, create some sample students
    if len(all_students_df) == 0:
        # Generate synthetic data for comparison
        np.random.seed(42)
        n_synthetic = 10
        
        synthetic_data = {
            'student_id': [f"SYN{i:03d}" for i in range(1, n_synthetic+1)],
            'student_name': [f"Sample Student {i}" for i in range(1, n_synthetic+1)],
            'gender': np.random.choice(['Male', 'Female'], n_synthetic),
            'age': np.random.randint(18, 46, n_synthetic),
            'nationality': np.random.choice(['Tunisian', 'Cameroonian', 'Senegalese', 'Moroccan', 
                                          'Algerian', 'Ivorian', 'Malian', 'Egyptian', 'Other'], n_synthetic),
            'communication_score': np.random.uniform(1, 5, n_synthetic).round(2),
            'leadership_score': np.random.uniform(1, 5, n_synthetic).round(2),
            'time_management_score': np.random.uniform(1, 5, n_synthetic).round(2),
            'analytical_score': np.random.uniform(1, 5, n_synthetic).round(2),
        }
        
        # Create patterns for better clustering
        synthetic_data['communication_score'][:3] = 5.0
        synthetic_data['leadership_score'][3:6] = 5.0
        synthetic_data['time_management_score'][6:9] = 5.0
        synthetic_data['analytical_score'][9:] = 5.0
        
        # Create DataFrame
        synthetic_df = pd.DataFrame(synthetic_data)
        synthetic_df['overall_score'] = synthetic_df[['communication_score', 'leadership_score', 
                                                    'time_management_score', 'analytical_score']].mean(axis=1)
        
        # Add the synthetic data to the combined_df
        combined_df = pd.concat([synthetic_df, student_scores], ignore_index=True)
    
    # Get feature columns - include both scores and demographic features
    score_columns = ['communication_score', 'leadership_score', 
                   'time_management_score', 'analytical_score']
                   
    # Process demographic features
    # Handle potential missing columns in the dataframe
    if 'gender' not in combined_df.columns:
        combined_df['gender'] = "Not specified"
    if 'age' not in combined_df.columns:
        combined_df['age'] = 20
    if 'nationality' not in combined_df.columns:
        combined_df['nationality'] = "Not specified"
    
    # Convert categorical variables to numeric using one-hot encoding
    # Gender encoding
    combined_df['gender_encoded'] = combined_df['gender'].map({'Male': 0, 'Female': 1, 'Not specified': 0.5})
    
    # Age standardization (already numeric)
    combined_df['age_normalized'] = (combined_df['age'] - 18) / (45 - 18)  # Normalize to 0-1 range
    
    # Nationality encoding (simplified using ordinal encoding for this example)
    nationality_mapping = {
        'Tunisian': 0, 'Cameroonian': 1, 'Senegalese': 2, 'Moroccan': 3,
        'Algerian': 4, 'Ivorian': 5, 'Malian': 6, 'Egyptian': 7, 'Other': 8,
        'Not specified': 4.5  # Middle value
    }
    combined_df['nationality_encoded'] = combined_df['nationality'].map(nationality_mapping)
    combined_df['nationality_normalized'] = combined_df['nationality_encoded'] / 8  # Normalize to 0-1 range
    
    # Combine skill scores and demographic features
    # Define weights to control the influence of demographics vs skills
    # You can adjust these weights to give more or less importance to demographics
    feature_columns = score_columns + ['gender_encoded', 'age_normalized', 'nationality_normalized']
    feature_weights = [1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5]  # Lower weights for demographic features
    
    # Extract features and handle missing values
    X = combined_df[feature_columns].values
    
    # Convert X to float type to ensure it's compatible with np.isnan
    X = X.astype(float)
    
    # Check for and handle NaN values before clustering
    try:
        has_nan = np.isnan(X).any()
    except TypeError:
        # If TypeError occurs, manually check for NaNs
        st.warning("Cannot automatically detect missing values. Using manual detection.")
        has_nan = False
        for col_idx in range(X.shape[1]):
            for row_idx in range(X.shape[0]):
                if pd.isna(X[row_idx, col_idx]):
                    has_nan = True
                    break
            if has_nan:
                break
    
    if has_nan:
        # Log the information about missing values
        st.warning("Some data contains missing values. These will be handled automatically.")
        
        # For each feature, replace NaN values with the mean of that feature
        for col_idx in range(X.shape[1]):
            feature_data = X[:, col_idx]
            # Use pandas isna which is more flexible with data types
            nan_mask = pd.isna(feature_data)
            if nan_mask.any():
                # Calculate mean of non-NaN values
                col_mean = np.nanmean(feature_data)
                # Replace NaN values with the mean
                X[nan_mask, col_idx] = col_mean
    
    # Apply weights after handling missing values
    for i, weight in enumerate(feature_weights):
        X[:, i] *= weight
    
    # Scale all features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Invert the scaled scores to cluster based on differences rather than similarities
    # This will make high scores appear as low scores and vice versa
    X_scaled_inverted = -1 * X_scaled
    
    # Determine optimal number of clusters using the inverted scores
    # Check if we have enough data for meaningful clustering
    if len(combined_df) <= 2:
        # For very small datasets, just use 2 clusters
        optimal_k = 2
    else:
        # Maximum number of clusters based on dataset size
        max_k = min(5, len(combined_df) - 1)
        
        # If max_k is less than 2, force it to 2 (minimum for clustering)
        if max_k < 2:
            max_k = 2
            
        k_range = range(2, max_k + 1)
        silhouette_scores = []
        
        for k in k_range:
            try:
                kmeans_test = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans_test.fit(X_scaled_inverted)  # Use inverted scores for clustering
                cluster_labels = kmeans_test.predict(X_scaled_inverted)
                
                # Check if we have enough unique labels for silhouette score
                unique_labels = len(np.unique(cluster_labels))
                if unique_labels > 1:  # Silhouette score needs at least 2 clusters
                    try:
                        silhouette_avg = silhouette_score(X_scaled_inverted, cluster_labels)
                        silhouette_scores.append(silhouette_avg)
                    except Exception as e:
                        # If silhouette fails, assign a default low score
                        silhouette_scores.append(-1)
                        st.warning(f"Silhouette score calculation failed for k={k}: {e}")
                else:
                    # If only one cluster was created, give it a poor score
                    silhouette_scores.append(-1)
                    st.warning(f"Only one cluster was formed for k={k}, which is not valid for evaluation.")
            except Exception as e:
                # If KMeans fails entirely, assign a default low score
                silhouette_scores.append(-1)
                st.warning(f"KMeans clustering failed for k={k}: {e}")
        
        # Choose optimal k if we have valid scores, otherwise default to 2
        if silhouette_scores and max(silhouette_scores) > -1:
            optimal_k = k_range[silhouette_scores.index(max(silhouette_scores))]
        else:
            optimal_k = 2
    
    # Perform KMeans clustering with optimal K using the inverted scores
    try:
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        combined_df['cluster'] = kmeans.fit_predict(X_scaled_inverted)  # Use inverted scores
        
        # Get the cluster center details (we need to invert them back for proper description)
        centers = -1 * kmeans.cluster_centers_  # Invert the centers back
    except Exception as e:
        st.error(f"Error during final clustering: {e}")
        # Fallback: assign random clusters if KMeans fails
        st.warning("Using fallback clustering method due to data issues.")
        combined_df['cluster'] = np.random.randint(0, optimal_k, size=len(combined_df))
        # Create dummy centers for cluster descriptions
        centers = np.zeros((optimal_k, len(feature_columns)))
    
    # Get cluster descriptions using the inverted-back centers
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
    
    # Visualize with PCA using the original (non-inverted) scores for visualization
    # This keeps the plot visualization consistent with the actual scores
    try:
        # Use PCA if we have enough data points (at least 2)
        if X_scaled.shape[0] >= 2:
            pca = PCA(n_components=min(2, X_scaled.shape[1]))
            X_pca = pca.fit_transform(X_scaled)  # Use original scores for visualization
        else:
            # For very small datasets, just use the first two features
            X_pca = X_scaled[:, :2]
        
        # Create PCA plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot all students
        for i in range(optimal_k):
            mask = combined_df['cluster'] == i
            
            # Check if we have any students in this cluster other than the new student
            if sum(mask) > 0:
                # If this is the cluster with the new student, exclude it from this scatter
                if i == new_student_cluster:
                    if sum(mask) > 1:  # Only try to plot if there are other students in this cluster
                        other_students_mask = mask.copy()
                        other_students_mask.iloc[-1] = False  # Exclude the new student
                        
                        if sum(other_students_mask) > 0:  # Double check we have points to plot
                            ax.scatter(
                                X_pca[other_students_mask, 0],
                                X_pca[other_students_mask, 1],
                                alpha=0.6, 
                                label=f"{cluster_descriptions[i]['name']}"
                            )
                    else:
                        # If new student is the only one in this cluster, label will be added when plotting that point
                        pass
                else:
                    ax.scatter(
                        X_pca[mask, 0],
                        X_pca[mask, 1],
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
    except Exception as e:
        # If PCA fails, create an empty plot with an error message
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Could not create visualization: not enough data", 
                ha='center', va='center', fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    
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
    
    # Get raw scores for more tailored recommendations
    raw_scores = {}
    for i, skill in skill_map.items():
        raw_scores[skill] = student_scores['%s_score' % skill].values[0]
    
    # Only process the first 4 features which are skills (indices 0-3)
    # The remaining features are demographic features (indices 4-6)
    for i in range(4):  # Only loop through skill features
        if i in skill_map:  # Extra safety check
            skill = skill_map[i]
            score = student_scores_normalized[i]  # Get normalized score for this skill
            raw_score = raw_scores[skill]
        
        if raw_score < 2.5:  # Low score (below middle of 1-5 scale)
            if skill == 'communication':
                skill_recommendations[skill] = "Your communication score suggests room for growth. Work on public speaking, active listening, and group discussions. In your learning group, you can learn from peers with stronger communication skills."
            elif skill == 'leadership':
                skill_recommendations[skill] = "Your leadership score indicates an opportunity to grow. Develop leadership abilities by taking initiative in group projects and observing successful leadership techniques from your peers."
            elif skill == 'time_management':
                skill_recommendations[skill] = "Your time management score suggests this is an area for development. Learn planning techniques from peers in your group who excel at time management."
            elif skill == 'analytical':
                skill_recommendations[skill] = "Your analytical thinking score indicates room for improvement. Engage in problem-solving activities with peers who have stronger analytical skills to develop this area."
        elif raw_score > 3.5:  # High score
            if skill == 'communication':
                skill_recommendations[skill] = "Your strong communication skills will be valuable in your learning group. Consider helping peers who may struggle with communication while further refining your own skills."
            elif skill == 'leadership':
                skill_recommendations[skill] = "With your strong leadership abilities, you can take initiative in group activities while helping others develop their leadership potential."
            elif skill == 'time_management':
                skill_recommendations[skill] = "Your excellent time management skills position you well to help peers who struggle in this area. Consider sharing your organizational techniques with your group."
            elif skill == 'analytical':
                skill_recommendations[skill] = "Your analytical thinking is a strength you can leverage to help peers while tackling more complex problems to further enhance your abilities."
    
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
                         [question['option_a'], question['option_b'], question['option_c'], question['option_d'], question['option_e']],
                         key=f"{st.session_state.current_category}_{st.session_state.question_idx}")
        
        # Map selected option to a, b, c, d, e
        option_mapping = {
            question['option_a']: 'a',
            question['option_b']: 'b',
            question['option_c']: 'c',
            question['option_d']: 'd',
            question['option_e']: 'e'
        }
        selected_option = option_mapping[option]
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        
        with col2:
            if st.button("Next Question"):
                # Record answer
                st.session_state.answers[st.session_state.current_category].append(selected_option)
                
                # Update score based on self-assessment (a=5, b=4, c=3, d=2, e=1)
                score_mapping = {'a': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1}
                st.session_state.scores[st.session_state.current_category] += score_mapping[selected_option]
                
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
    
    # Check if scores exist in session state
    if not hasattr(st.session_state, 'scores') or not st.session_state.scores:
        st.error("No quiz scores found. Please retake the quiz.")
        if st.button("Return to Quiz"):
            # Reset session state for quiz
            if 'student_name' in st.session_state:
                del st.session_state.student_name
            if 'quiz_complete' in st.session_state:
                del st.session_state.quiz_complete
            st.rerun()
        return
    
    # Calculate normalized scores (on a scale of 1-5)
    normalized_scores = {}
    for category, score in st.session_state.scores.items():
        # Convert score from range 5-25 (min-max possible points with 5-point scale) to 1-5 range
        normalized_scores[f"{category}_score"] = 1 + ((score - 5) / 20) * 4
    
    # Create timestamp for student ID
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    student_id = f"NEW_{timestamp}"
    
    # Create a DataFrame for the student
    student_data = {
        'student_id': [student_id],
        'student_name': [st.session_state.student_name if 'student_name' in st.session_state else "You"],
        'gender': [st.session_state.student_gender if 'student_gender' in st.session_state else "Not specified"],
        'age': [st.session_state.student_age if 'student_age' in st.session_state else 20],
        'nationality': [st.session_state.student_nationality if 'student_nationality' in st.session_state else "Not specified"],
        'communication_score': [normalized_scores['communication_score']],
        'leadership_score': [normalized_scores['leadership_score']],
        'time_management_score': [normalized_scores['time_management_score']],
        'analytical_score': [normalized_scores['analytical_score']]
    }
    student_df = pd.DataFrame(student_data)
    
    # Calculate overall score
    student_df['overall_score'] = student_df[['communication_score', 'leadership_score', 
                                            'time_management_score', 'analytical_score']].mean(axis=1)
    
    # Add quiz timestamp
    student_df['quiz_timestamp'] = timestamp
    
    # Add this student to the list of students who took the quiz
    st.session_state.students_who_took_quiz = pd.concat(
        [st.session_state.students_who_took_quiz, student_df], 
        ignore_index=True
    )
    
    # Save updated student data to CSV
    try:
        saved_path = "students_quiz_results.csv"
        
        # If file exists, append to it, otherwise create new
        if os.path.exists(saved_path):
            existing_df = pd.read_csv(saved_path)
            combined_df = pd.concat([existing_df, student_df], ignore_index=True)
            combined_df.to_csv(saved_path, index=False)
        else:
            student_df.to_csv(saved_path, index=False)
    except Exception as e:
        st.warning(f"Could not save quiz results: {e}")
    
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
    st.subheader("🧩 Your Collaborative Learning Group")
    
    # Get existing student data
    all_students_df = load_student_data()
    
    # Perform clustering and get recommendations
    recommendations, cluster_fig = perform_clustering(student_df, all_students_df)
    
    # Display the cluster information
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.write(f"**Your Learning Group:** {recommendations['cluster_name']}")
        st.write(recommendations['description'])
        
        # Explain what the clustering means
        st.write("### What This Means")
        st.write("""
        You've been placed in a learning group where students complement each other's strengths and weaknesses. 
        This group is designed for peer learning and collaborative skill development.
        """)
        
        # Display complementary and common skills
        st.write("**Skills Where Group Members Can Help Each Other:**")
        for strength in recommendations['strengths']:
            if strength != "No specific complementary skills":
                st.write(f"- {strength} (some students score high, others score low)")
            else:
                st.write("- Group members have balanced skill levels across all areas")
            
        st.write("**Skills With Similar Levels Across Group:**")
        for weakness in recommendations['weaknesses']:
            if weakness != "No specific common skills":
                st.write(f"- {weakness} (most group members have similar levels in this skill)")
            else:
                st.write("- No skills where all group members have similar levels")
    
    with col2:
        # Display the PCA plot
        st.pyplot(cluster_fig)
    
    # Display skill-specific recommendations if any
    if recommendations['skill_specific']:
        st.subheader("📈 Personalized Learning Recommendations")
        st.write("""
        Based on your skill profile and your learning group composition, here are some personalized 
        recommendations to help you make the most of your collaborative learning experience:
        """)
        for skill, recommendation in recommendations['skill_specific'].items():
            st.write(f"**{skill.title()}:** {recommendation}")
            
        # Add group learning recommendations
        complementary_skills = recommendations['strengths']
        if complementary_skills[0] != "No specific complementary skills":
            st.write("### Group Learning Opportunities")
            st.write(f"""
            In your learning group, you'll find students with varying levels of {', '.join(complementary_skills)} skills.
            This diversity creates excellent peer learning opportunities:
            
            - If you scored high in these areas, consider mentoring others or leading group activities
            - If you scored lower, seek guidance from peers who excel in these areas
            - Exchange knowledge and techniques to help everyone improve
            """)
    
    # Create two buttons: one to retake the quiz, another to view all groups
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Retake Assessment"):
            # Reset session state for quiz but keep student data
            quiz_keys = ['current_category', 'question_idx', 'answers', 'scores', 'quiz_complete', 'student_name']
            for key in quiz_keys:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("View All Student Groups"):
            # Keep the student data but change mode to view all groups
            st.session_state.app_mode = "View All Student Groups"
            st.rerun()

# Function to show all students and clusters
def show_all_students_and_clusters():
    st.title("👥 Student Clusters and Group Assignments")
    
    # Add a button to take a new student quiz
    if st.button("➕ Add New Student"):
        # Clear student name to trigger new student entry
        if 'student_name' in st.session_state:
            del st.session_state.student_name
        
        # Switch to quiz mode
        st.session_state.app_mode = "Take Quiz"
        st.rerun()
    
    # Load all students
    all_students_df = load_student_data()
    
    # Add any students who took the quiz
    if not st.session_state.students_who_took_quiz.empty:
        all_students_df = pd.concat([all_students_df, st.session_state.students_who_took_quiz], ignore_index=True)
        
    # Show the number of students
    st.subheader(f"Total Students: {len(all_students_df)}")
    
    # Display demographic statistics
    if 'gender' in all_students_df.columns and 'nationality' in all_students_df.columns and 'age' in all_students_df.columns:
        st.write("### Student Demographics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gender distribution
            gender_counts = all_students_df['gender'].value_counts()
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            ax1.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%',
                   startangle=90, colors=['#ff9999','#66b3ff'])
            ax1.set_title('Gender Distribution')
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            st.pyplot(fig1)
        
        with col2:
            # Age distribution
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.hist(all_students_df['age'], bins=range(18, 46, 3), color='#8dd3c7')
            ax2.set_title('Age Distribution')
            ax2.set_xlabel('Age')
            ax2.set_ylabel('Number of Students')
            st.pyplot(fig2)
        
        # Nationality distribution
        nat_counts = all_students_df['nationality'].value_counts().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        ax3.bar(nat_counts.index, nat_counts.values, color='#bebada')
        ax3.set_title('Nationality Distribution')
        ax3.set_ylabel('Number of Students')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig3)    # Perform clustering on all students
    if len(all_students_df) < 5:
        st.warning("Not enough students to form meaningful clusters. Please add more students.")
        return
    
    # Get and prepare the feature data
    score_columns = ['communication_score', 'leadership_score', 
                   'time_management_score', 'analytical_score']
                   
    # Process demographic features if they exist
    if 'gender' not in all_students_df.columns:
        all_students_df['gender'] = "Not specified"
    if 'age' not in all_students_df.columns:
        all_students_df['age'] = 20
    if 'nationality' not in all_students_df.columns:
        all_students_df['nationality'] = "Not specified"
    
    # Convert categorical variables to numeric
    # Gender encoding
    all_students_df['gender_encoded'] = all_students_df['gender'].map({'Male': 0, 'Female': 1, 'Not specified': 0.5})
    
    # Age standardization (already numeric)
    all_students_df['age_normalized'] = (all_students_df['age'] - 18) / (45 - 18)  # Normalize to 0-1 range
    
    # Nationality encoding (simplified using ordinal encoding)
    nationality_mapping = {
        'Tunisian': 0, 'Cameroonian': 1, 'Senegalese': 2, 'Moroccan': 3,
        'Algerian': 4, 'Ivorian': 5, 'Malian': 6, 'Egyptian': 7, 'Other': 8,
        'Not specified': 4.5  # Middle value
    }
    all_students_df['nationality_encoded'] = all_students_df['nationality'].map(nationality_mapping)
    all_students_df['nationality_normalized'] = all_students_df['nationality_encoded'] / 8  # Normalize to 0-1 range
    
    # Combine skill scores and demographic features with weights
    feature_columns = score_columns + ['gender_encoded', 'age_normalized', 'nationality_normalized']
    feature_weights = [1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5]  # Lower weights for demographic features
    
    # Extract features and check for missing values
    X = all_students_df[feature_columns].values
    
    # Convert X to float type to ensure it's compatible with np.isnan
    X = X.astype(float)
    
    # Check for and handle NaN values before clustering
    try:
        has_nan = np.isnan(X).any()
    except TypeError:
        # If TypeError occurs, manually check for NaNs
        st.warning("Cannot automatically detect missing values. Using manual detection.")
        has_nan = False
        for col_idx in range(X.shape[1]):
            for row_idx in range(X.shape[0]):
                if pd.isna(X[row_idx, col_idx]):
                    has_nan = True
                    break
            if has_nan:
                break
    
    if has_nan:
        st.warning("Some data contains missing values. These will be handled automatically.")
        
        # For each feature, replace NaN values with the mean of that feature
        for col_idx in range(X.shape[1]):
            feature_data = X[:, col_idx]
            # Use pandas isna which is more flexible with data types
            nan_mask = pd.isna(feature_data)
            if nan_mask.any():
                # Calculate mean of non-NaN values
                col_mean = np.nanmean(feature_data)
                # Replace NaN values with the mean
                X[nan_mask, col_idx] = col_mean
    
    # Apply weights
    for i, weight in enumerate(feature_weights):
        X[:, i] *= weight
    
    # Scale all features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Invert the scaled scores to cluster based on differences rather than similarities
    X_scaled_inverted = -1 * X_scaled
    
    # Determine optimal number of clusters
    # Check if we have enough data for meaningful clustering
    if len(all_students_df) <= 2:
        # For very small datasets, just use 2 clusters
        optimal_k = 2
    else:
        # Maximum number of clusters based on dataset size
        max_k = min(5, len(all_students_df) - 1)
        
        # Make sure k_range has at least one value
        if max_k < 2:
            max_k = 2
            
        k_range = range(2, max_k + 1)
        silhouette_scores = []
        
        for k in k_range:
            try:
                kmeans_test = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans_test.fit(X_scaled_inverted)
                cluster_labels = kmeans_test.predict(X_scaled_inverted)
                
                # Check if we have enough unique labels for silhouette score
                unique_labels = len(np.unique(cluster_labels))
                if unique_labels > 1:  # Silhouette score needs at least 2 clusters
                    try:
                        silhouette_avg = silhouette_score(X_scaled_inverted, cluster_labels)
                        silhouette_scores.append(silhouette_avg)
                    except Exception as e:
                        # If silhouette fails, assign a default low score
                        silhouette_scores.append(-1)
                        st.warning(f"Silhouette score calculation failed for k={k}: {e}")
                else:
                    # If only one cluster was created, give it a poor score
                    silhouette_scores.append(-1)
            except Exception as e:
                # If KMeans fails, assign a default low score
                silhouette_scores.append(-1)
                st.warning(f"KMeans clustering failed for k={k}: {e}")
        
        # Choose optimal k if we have valid scores, otherwise default to 2
        if silhouette_scores and max(silhouette_scores) > -1:
            optimal_k = k_range[silhouette_scores.index(max(silhouette_scores))]
        else:
            optimal_k = 2
    
    # Perform KMeans clustering with optimal K
    try:
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        all_students_df['cluster'] = kmeans.fit_predict(X_scaled_inverted)
        
        # Get cluster centers and descriptions
        centers = -1 * kmeans.cluster_centers_
        cluster_descriptions = get_cluster_descriptions(centers)
    except Exception as e:
        st.error(f"Error during final clustering: {e}")
        # Fallback: assign random clusters if KMeans fails
        st.warning("Using fallback clustering method due to data issues.")
        all_students_df['cluster'] = np.random.randint(0, optimal_k, size=len(all_students_df))
        # Create dummy centers for cluster descriptions with the right number of features
        # (4 skill features + 3 demographic features)
        centers = np.zeros((optimal_k, len(feature_columns)))
        cluster_descriptions = get_cluster_descriptions(centers)
    
    # Add cluster name to students dataframe
    all_students_df['cluster_name'] = all_students_df['cluster'].apply(lambda x: cluster_descriptions[x]['name'])
    
    # Visualize with PCA
    try:
        # Use PCA if we have enough data points
        if X_scaled.shape[0] >= 2:
            pca = PCA(n_components=min(2, X_scaled.shape[1]))
            X_pca = pca.fit_transform(X_scaled)
        else:
            # For very small datasets, just use the first two features
            X_pca = X_scaled[:, :2]
        
        # Create PCA plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot all students colored by cluster
        for i in range(optimal_k):
            mask = all_students_df['cluster'] == i
            if sum(mask) > 0:  # Only plot if there are students in this cluster
                ax.scatter(
                    X_pca[mask, 0],
                    X_pca[mask, 1],
                    alpha=0.6, 
                    label=f"{cluster_descriptions[i]['name']}"
                )
        
        # Add labels and legend
        ax.set_title('Student Clusters Visualization (PCA)')
        ax.set_xlabel('Principal Component 1')
        ax.set_ylabel('Principal Component 2')
        ax.legend()
        
    except Exception as e:
        # If PCA fails, create an empty plot with an error message
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Could not create visualization: not enough data", 
                ha='center', va='center', fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    
    # Display the PCA plot
    st.pyplot(fig)
    
    # Show number of groups formed
    st.subheader(f"📊 {optimal_k} Heterogeneous Learning Groups Formed")
    st.write("""
    These groups are designed to maximize diversity of skills within each group.
    Students with complementary skills are grouped together to encourage peer learning and collaboration.
    """)
    
    # Display each cluster and its members
    for i in range(optimal_k):
        cluster_students = all_students_df[all_students_df['cluster'] == i]
        
        with st.expander(f"Group {i+1}: {cluster_descriptions[i]['name']} ({len(cluster_students)} students)"):
            st.write(cluster_descriptions[i]['description'])
            
            # Show complementary and common skills
            st.write("**Skills With High Diversity:**")
            for skill in cluster_descriptions[i]['strengths']:
                if skill != "No specific complementary skills":
                    st.write(f"- {skill}")
            
            st.write("**Skills With Similar Levels:**")
            for skill in cluster_descriptions[i]['weaknesses']:
                if skill != "No specific common skills":
                    st.write(f"- {skill}")
            
            # Show demographic diversity if available
            if 'demographic_diversity' in cluster_descriptions[i] and cluster_descriptions[i]['demographic_diversity']:
                st.write("**Demographic Diversity:**")
                for demo in cluster_descriptions[i]['demographic_diversity']:
                    st.write(f"- {demo}")
                
                # Show demographic breakdown for this cluster
                if ('gender' in cluster_students.columns and 
                    'age' in cluster_students.columns and 
                    'nationality' in cluster_students.columns):
                    
                    with st.expander("View Demographic Breakdown"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Gender breakdown
                            gender_counts = cluster_students['gender'].value_counts()
                            fig1, ax1 = plt.subplots(figsize=(6, 4))
                            ax1.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%',
                                colors=['#ff9999','#66b3ff'])
                            ax1.set_title('Gender Distribution')
                            st.pyplot(fig1)
                        
                        with col2:
                            # Age stats
                            fig2, ax2 = plt.subplots(figsize=(6, 4))
                            ax2.hist(cluster_students['age'], bins=range(18, 46, 5), color='#8dd3c7')
                            ax2.set_title('Age Distribution')
                            ax2.set_xlabel('Age')
                            ax2.set_ylabel('Count')
                            st.pyplot(fig2)
                        
                        # Nationality breakdown
                        nat_counts = cluster_students['nationality'].value_counts()
                        if len(nat_counts) > 0:
                            st.write("**Nationality Breakdown:**")
                            st.write(pd.DataFrame({
                                'Nationality': nat_counts.index,
                                'Count': nat_counts.values,
                                'Percentage': (nat_counts.values / nat_counts.sum() * 100).round(1)
                            }))
            
            # Show the students in this cluster with their scores
            st.write("### Students in this group:")
            # Format the dataframe for display - now with demographic info
            cols_to_display = ['student_name', 'gender', 'age', 'nationality', 
                              'communication_score', 'leadership_score', 
                              'time_management_score', 'analytical_score', 'overall_score']
            
            # Check if demographic columns exist in the dataframe
            display_cols = [col for col in cols_to_display if col in cluster_students.columns]
            
            display_df = cluster_students[display_cols]
            display_df = display_df.round(2)
            
            # Define column names mapping
            col_mapping = {
                'student_name': 'Student Name',
                'gender': 'Gender', 
                'age': 'Age', 
                'nationality': 'Nationality',
                'communication_score': 'Communication', 
                'leadership_score': 'Leadership', 
                'time_management_score': 'Time Management', 
                'analytical_score': 'Analytical', 
                'overall_score': 'Overall Score'
            }
            
            # Apply mapping to the columns that are present
            display_df.columns = [col_mapping[col] for col in display_cols]
            
            # Display the dataframe
            st.dataframe(display_df)

# Main app
def main():
    st.sidebar.title("Soft Skills Assessment & Clustering")
    st.sidebar.image("https://img.icons8.com/color/96/000000/mind-map.png", width=100)
    
    # About section in sidebar
    st.sidebar.subheader("About")
    st.sidebar.info(
        "This application helps students assess their soft skills "
        "through a quiz and then uses machine learning to cluster them "
        "based on their skills profile, forming heterogeneous learning groups."
    )
    
    # If app_mode is in session state, use that instead of the radio button
    if 'app_mode' in st.session_state:
        current_mode = st.session_state.app_mode
    else:
        current_mode = "Take Quiz"
    
    # Add options to sidebar and update session state
    app_mode = st.sidebar.radio(
        "Choose Mode:", 
        ["Take Quiz", "View All Student Groups"],
        index=0 if current_mode == "Take Quiz" else 1
    )
    
    # Update session state with the current mode
    st.session_state.app_mode = app_mode
    
    if app_mode == "Take Quiz":
        # Ask for student information if not already provided
        if 'student_name' not in st.session_state:
            st.title("🧩 Soft Skills Assessment Quiz")
            st.write("Please enter your information to begin the assessment.")
            
            # Create form for student information
            with st.form("student_info_form"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    student_name = st.text_input("Full Name:", key="name_input")
                    gender = st.selectbox("Gender:", ["Male", "Female"], key="gender_input")
                    
                with col2:
                    age = st.number_input("Age:", min_value=18, max_value=45, value=20, key="age_input")
                    nationality = st.selectbox("Nationality:", 
                                             ["Tunisian", "Cameroonian", "Senegalese", "Moroccan", 
                                              "Algerian", "Ivorian", "Malian", "Egyptian", "Other"], 
                                             key="nationality_input")
                
                # Submit button
                submitted = st.form_submit_button("Begin Quiz")
                
                if submitted and student_name.strip():
                    # Store all demographic information in session state
                    st.session_state.student_name = student_name
                    st.session_state.student_gender = gender
                    st.session_state.student_age = age
                    st.session_state.student_nationality = nationality
                    st.rerun()
        else:
            # Run the quiz or show results if quiz is complete
            if 'quiz_complete' in st.session_state and st.session_state.quiz_complete:
                show_results()
            else:
                run_quiz()
    else:
        # Show all students and their clusters
        show_all_students_and_clusters()

if __name__ == "__main__":
    main()
