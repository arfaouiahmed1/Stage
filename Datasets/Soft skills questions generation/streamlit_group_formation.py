import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
import os
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Student Heterogeneous Group Formation",
    page_icon="🧩",
    layout="wide"
)

# Title and description
st.title("🧩 Student Heterogeneous Group Formation")
st.markdown("""
This application helps form balanced student teams based on complementary skill profiles. 
The goal is to create heterogeneous groups where students with different strengths and weaknesses 
can work together effectively and learn from each other.
""")

# Sidebar for navigation and options
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a Page",
    ["Home", "Data Upload", "Data Analysis", "Group Formation", "Group Analysis", "Project Recommendations"]
)

# Initialize session state to store data across pages
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'clusters_formed' not in st.session_state:
    st.session_state.clusters_formed = False
if 'groups_formed' not in st.session_state:
    st.session_state.groups_formed = False
if 'groups_data' not in st.session_state:
    st.session_state.groups_data = None
if 'skill_columns' not in st.session_state:
    st.session_state.skill_columns = []

# Home page
if page == "Home":
    st.header("Student Heterogeneous Group Formation System")
    st.markdown("""
    ## Overview

    This application helps form balanced student groups across several key skill domains:

    - **Soft Skills**: Communication, leadership, teamwork, adaptability
    - **Hard Skills**: Technical knowledge, programming, analysis, domain-specific abilities
    - **Creativity**: Innovation, idea generation, thinking outside the box
    - **Teamwork**: Collaboration, conflict resolution, task coordination

    ## Approach

    1. **Data Upload**: Upload your student skill profiles
    2. **Data Analysis**: Understand the distribution and correlation of skills
    3. **Group Formation**: Create heterogeneous groups with complementary skills
    4. **Group Analysis**: Evaluate the balance and diversity of formed groups
    5. **Project Recommendations**: Get project suggestions based on group compositions
    
    ## Get Started
    
    Navigate to the "Data Upload" section to begin.
    """)
    
    st.info("This application was created based on a Jupyter notebook focused on heterogeneous student grouping.")

# Data Upload Page
elif page == "Data Upload":
    st.header("Upload Student Data")
    st.markdown("""
    Upload a CSV file containing student skill profiles. The file should have:
    - A column for student IDs or names
    - Multiple columns for different skill scores (on a scale, e.g., 1-5)
    
    Sample columns: `student_id`, `soft_skills`, `hard_skills`, `creativity`, `teamwork`
    """)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    # Sample data option
    use_sample = st.checkbox("Use sample data instead", value=False)
    
    if use_sample:
        st.write("Using sample student data...")
        
        # Create sample data
        num_students = st.slider("Number of sample students", min_value=10, max_value=100, value=30)
        np.random.seed(42)  # For reproducibility
        
        # Generate sample data with student_id and skill scores
        data = {
            'student_id': [f'S{i+1:03d}' for i in range(num_students)],
            'soft_skills': np.random.uniform(1, 5, num_students).round(2),
            'hard_skills': np.random.uniform(1, 5, num_students).round(2),
            'creativity': np.random.uniform(1, 5, num_students).round(2),
            'teamwork': np.random.uniform(1, 5, num_students).round(2)
        }
        
        df = pd.DataFrame(data)
        st.session_state.students_df = df
        st.session_state.data_loaded = True
        
        # Display sample data
        st.subheader("Sample Data")
        st.dataframe(df)
        
        # Let the user see the full data
        if st.checkbox("Show full sample dataset"):
            st.dataframe(df)
            
        # Success message
        st.success(f"Sample data with {num_students} students created successfully!")
        
    elif uploaded_file is not None:
        # Read the uploaded file
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.students_df = df
            st.session_state.data_loaded = True
            
            # Display uploaded data preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Basic data info
            st.subheader("Data Information")
            st.write(f"Number of students: {len(df)}")
            st.write(f"Number of columns: {len(df.columns)}")
            
            # Let the user see the column details
            if st.checkbox("Show column details"):
                col_info = pd.DataFrame({
                    'Column Name': df.columns,
                    'Data Type': df.dtypes,
                    'Non-Null Count': df.notna().sum(),
                    'Null Count': df.isna().sum()
                })
                st.dataframe(col_info)
                
            # Success message
            st.success(f"Data with {len(df)} students loaded successfully!")
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.error("Please check your CSV file format and try again.")
    else:
        st.info("Please upload a CSV file or use the sample data option.")

# Data Analysis Page
elif page == "Data Analysis":
    if not st.session_state.data_loaded:
        st.warning("Please upload data first on the 'Data Upload' page.")
        st.stop()
    
    st.header("Data Analysis")
    st.markdown("""
    This page provides insights into the student skill distribution and relationships.
    """)
    
    # Get the data
    students_df = st.session_state.students_df
    
    # Allow the user to select skill columns
    all_columns = list(students_df.columns)
    default_skill_cols = [col for col in all_columns if 
                         any(x in col.lower() for x in ['skill', 'score', 'creativity', 'teamwork'])]
    
    # If no skill columns were detected, let the user choose
    if not default_skill_cols:
        default_skill_cols = all_columns[1:] if len(all_columns) > 1 else all_columns
    
    skill_cols = st.multiselect(
        "Select skill columns for analysis:",
        options=all_columns,
        default=default_skill_cols
    )
    
    st.session_state.skill_columns = skill_cols
    
    if not skill_cols:
        st.warning("Please select at least one skill column.")
        st.stop()
    
    # Summary statistics
    st.subheader("Summary Statistics")
    st.dataframe(students_df[skill_cols].describe())
    
    # Visualizations
    st.subheader("Skill Distributions")
    
    # Distribution plots
    fig, axes = plt.subplots(1, len(skill_cols), figsize=(5*len(skill_cols), 4))
    if len(skill_cols) == 1:
        axes = [axes]  # Make iterable for single column case
        
    for i, col in enumerate(skill_cols):
        sns.histplot(students_df[col], kde=True, bins=20, ax=axes[i])
        axes[i].set_title(f'Distribution of {col}')
        axes[i].set_xlabel('Score')
        axes[i].set_ylabel('Frequency')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Correlation heatmap
    st.subheader("Correlation Between Skills")
    if len(skill_cols) > 1:
        fig, ax = plt.subplots(figsize=(10, 8))
        corr = students_df[skill_cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', mask=mask, ax=ax)
        plt.title('Correlation Between Skill Scores')
        st.pyplot(fig)
    else:
        st.info("Need at least two skill columns to show correlations.")
    
    # Radar chart for average skill profile
    st.subheader("Average Student Skill Profile")
    
    # Calculate mean values for each skill
    means = students_df[skill_cols].mean().values
    
    # Create radar chart using plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(means) + [means[0]],  # Close the loop
        theta=[col.replace('_', ' ').title() for col in skill_cols] + [skill_cols[0].replace('_', ' ').title()],
        fill='toself',
        name='Average Profile'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title="Average Student Skill Profile"
    )
    
    st.plotly_chart(fig)
    
    # Preprocess the data
    with st.expander("Preprocess Data for Clustering and Group Formation"):
        st.write("This will add derived features and normalize the data for better analysis.")
        
        if st.button("Preprocess Data"):
            with st.spinner("Preprocessing data..."):
                # Function to preprocess data
                def preprocess_student_data(df, skill_columns):
                    # Create a copy
                    processed_df = df.copy()
                    
                    # Handle missing values if any
                    if processed_df[skill_columns].isnull().sum().sum() > 0:
                        # Fill missing values with mean of the column
                        for col in skill_columns:
                            if processed_df[col].isnull().sum() > 0:
                                mean_val = processed_df[col].mean()
                                processed_df[col] = processed_df[col].fillna(mean_val)
                    
                    # Overall skill level
                    processed_df['overall_skill'] = processed_df[skill_columns].mean(axis=1)
                    
                    # Skill variance
                    processed_df['skill_variance'] = processed_df[skill_columns].var(axis=1)
                    
                    # Dominant skill area
                    processed_df['dominant_skill'] = processed_df[skill_columns].idxmax(axis=1)
                    
                    # Weakest skill area
                    processed_df['weakest_skill'] = processed_df[skill_columns].idxmin(axis=1)
                    
                    # Normalize skills
                    scaler = MinMaxScaler()
                    normalized_skills = scaler.fit_transform(processed_df[skill_columns])
                    
                    for i, col in enumerate(skill_columns):
                        processed_df[f'norm_{col}'] = normalized_skills[:, i]
                    
                    return processed_df
                
                # Apply preprocessing
                processed_students = preprocess_student_data(students_df, skill_cols)
                st.session_state.processed_data = processed_students
                
                # Show preview of processed data
                st.subheader("Processed Data Preview")
                st.dataframe(processed_students.head())
                
                # Show distribution of dominant skills
                fig, ax = plt.subplots(figsize=(10, 6))
                dominant_counts = processed_students['dominant_skill'].value_counts()
                sns.barplot(x=dominant_counts.index, y=dominant_counts.values, ax=ax)
                plt.title('Distribution of Dominant Skills Among Students')
                plt.xlabel('Skill Area')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                st.success("Data preprocessing completed!")

# Group Formation Page
elif page == "Group Formation":
    if not st.session_state.data_loaded:
        st.warning("Please upload data first on the 'Data Upload' page.")
        st.stop()
        
    if st.session_state.processed_data is None:
        st.warning("Please preprocess the data on the 'Data Analysis' page first.")
        st.stop()
    
    st.header("Group Formation")
    st.markdown("""
    This page allows you to form heterogeneous student groups using different methods:
    
    1. **Complementary**: Pairs students with complementary strengths and weaknesses
    2. **Balanced**: Ensures each group has a similar average skill level
    3. **Mixed**: Combines cluster-based and skill-based assignment
    """)
    
    # Get processed data and skill columns
    processed_students = st.session_state.processed_data
    skill_cols = st.session_state.skill_columns
    
    # Clustering parameters
    st.subheader("Step 1: Cluster Students by Skill Patterns")
    
    n_clusters = st.slider("Number of clusters", min_value=2, max_value=10, value=4)
    
    if st.button("Perform Clustering"):
        with st.spinner("Clustering students..."):
            # Function to perform clustering
            def cluster_student_skills(df, skill_columns, n_clusters):
                # Create a copy
                clustered_df = df.copy()
                
                # Extract features for clustering (normalized skill scores)
                norm_cols = [f'norm_{col}' for col in skill_columns]
                if all(col in clustered_df.columns for col in norm_cols):
                    X = clustered_df[norm_cols].values
                else:
                    X = clustered_df[skill_columns].values
                
                # Scale the data
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Perform K-means clustering
                kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=300, n_init=10, random_state=42)
                clustered_df['cluster'] = kmeans.fit_predict(X_scaled)
                
                # Get cluster centers
                centers_scaled = kmeans.cluster_centers_
                centers_original = scaler.inverse_transform(centers_scaled)
                
                # Create a DataFrame for cluster centers
                if all(col in clustered_df.columns for col in norm_cols):
                    centers_df = pd.DataFrame(centers_original, columns=norm_cols)
                    centers_df.columns = [col.replace('norm_', '') for col in centers_df.columns]
                else:
                    centers_df = pd.DataFrame(centers_original, columns=skill_columns)
                
                centers_df['cluster'] = range(n_clusters)
                
                return clustered_df, centers_df
            
            # Apply clustering
            clustered_students, cluster_centers = cluster_student_skills(processed_students, skill_cols, n_clusters)
            
            # Store in session state
            st.session_state.clustered_students = clustered_students
            st.session_state.cluster_centers = cluster_centers
            st.session_state.clusters_formed = True
            
            # Show cluster distribution
            st.subheader("Cluster Distribution")
            cluster_counts = clustered_students['cluster'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(cluster_counts.index, cluster_counts.values)
            ax.set_xlabel('Cluster')
            ax.set_ylabel('Number of Students')
            ax.set_title('Number of Students in Each Cluster')
            ax.set_xticks(range(n_clusters))
            st.pyplot(fig)
            
            # Show cluster profiles
            st.subheader("Cluster Skill Profiles")
            
            # Radar chart for each cluster
            fig = go.Figure()
            
            for i in range(n_clusters):
                center = cluster_centers[cluster_centers['cluster'] == i][skill_cols].values[0]
                
                fig.add_trace(go.Scatterpolar(
                    r=list(center) + [center[0]],  # Close the loop
                    theta=[col.replace('_', ' ').title() for col in skill_cols] + [skill_cols[0].replace('_', ' ').title()],
                    fill='toself',
                    name=f'Cluster {i}'
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                title="Cluster Skill Profiles"
            )
            
            st.plotly_chart(fig)
            
            # 2D visualization with PCA
            st.subheader("2D Visualization of Clusters")
            
            # Get normalized feature columns
            norm_cols = [f'norm_{col}' for col in skill_cols]
            if all(col in clustered_students.columns for col in norm_cols):
                X = clustered_students[norm_cols].values
            else:
                X = clustered_students[skill_cols].values
            
            # Apply PCA
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)
            
            # Create a DataFrame for plotting
            pca_df = pd.DataFrame({
                'PCA1': X_pca[:, 0],
                'PCA2': X_pca[:, 1],
                'Cluster': clustered_students['cluster']
            })
            
            # Plot using plotly
            fig = px.scatter(
                pca_df, x='PCA1', y='PCA2', color='Cluster',
                color_continuous_scale='viridis',
                title='Student Clusters Visualized with PCA'
            )
            
            st.plotly_chart(fig)
            
            st.success("Clustering completed successfully!")
    
    # Group formation
    st.subheader("Step 2: Form Student Groups")
    
    if not st.session_state.clusters_formed:
        st.warning("Please perform clustering first.")
    else:
        # Group formation parameters
        group_size = st.slider("Group Size", min_value=2, max_value=6, value=4)
        
        grouping_method = st.selectbox(
            "Grouping Method",
            options=['complementary', 'balanced', 'mixed'],
            format_func=lambda x: x.title()
        )
        
        if st.button("Form Groups"):
            with st.spinner("Forming student groups..."):
                # Function to form heterogeneous groups
                def form_heterogeneous_groups(df, skill_columns, group_size=4, method='complementary', max_time=30):
                    # Create a working copy
                    students = df.copy()
                    
                    # Shuffle the students to ensure randomness
                    students = students.sample(frac=1, random_state=42).reset_index(drop=True)
                    
                    # Calculate number of groups
                    n_students = len(students)
                    n_groups = n_students // group_size
                    remainder = n_students % group_size
                    
                    # Initialize groups
                    groups = {}
                    
                    if method == 'complementary':
                        # Import time for timeout check
                        import time
                        start_time = time.time()
                        
                        # Sort students by overall skill level
                        students = students.sort_values('overall_skill', ascending=False).reset_index()
                        original_index = students['index'].copy()  # Store original indices
                        students = students.reset_index(drop=True)  # Create new clean indices
                        
                        # Track assigned students
                        assigned_students = set()
                        
                        # For each group, select students with diverse skill strengths
                        for g in range(n_groups):
                            # Check if we're taking too long
                            if time.time() - start_time > max_time:
                                st.warning(f"Group formation taking too long (>{max_time}s). Using simpler approach for remaining groups.")
                                break  # Exit the loop and handle remaining students with simpler approach
                                
                            group_members = []
                            
                            # Find students not yet assigned to any group
                            unassigned_indices = [i for i in range(len(students)) if i not in assigned_students]
                            
                            # If we still have unassigned students
                            if unassigned_indices:
                                # Select first student (highest overall skill not yet assigned)
                                first_student_idx = unassigned_indices[0]
                                group_members.append(first_student_idx)
                                assigned_students.add(first_student_idx)
                                
                                # Find students with complementary skills
                                for _ in range(1, group_size):
                                    # If we've run out of students, break
                                    unassigned_indices = [i for i in range(len(students)) if i not in assigned_students]
                                    if not unassigned_indices:
                                        break
                                        
                                    # Check if we're taking too long
                                    if time.time() - start_time > max_time: 
                                        st.warning(f"Group formation taking too long (>{max_time}s). Completing current group with best available students.")
                                        # Add some students to complete the group
                                        needed = min(group_size - len(group_members), len(unassigned_indices))
                                        for idx in unassigned_indices[:needed]:
                                            group_members.append(idx)
                                            assigned_students.add(idx)
                                        break
                                    
                                    # Use a simpler complementary calculation for better performance
                                    compatibility_scores = []
                                    
                                    # Get current group skill profile - use the new indices for accessing
                                    current_group_skills = students.iloc[group_members][skill_columns].mean()
                                    
                                    # Only check a sample of unassigned students if there are many
                                    max_students_to_check = min(len(unassigned_indices), 20)
                                    students_to_check = unassigned_indices[:max_students_to_check]
                                    
                                    # Calculate compatibility for each unassigned student
                                    for idx in students_to_check:
                                        student = students.iloc[idx]
                                        
                                        # Calculate how complementary this student is to the current group
                                        # Simple approach: just find the student with the strongest skills 
                                        # in the group's weakest areas
                                        comp_score = 0
                                        for skill in skill_columns:
                                            try:
                                                # Get the skill values safely
                                                group_skill_value = float(current_group_skills[skill]) 
                                                student_skill_value = float(student[skill])
                                                
                                                # Simple complementary formula - higher where group is weak
                                                if group_skill_value < 3.0:  # If group is weak in this skill
                                                    comp_score += student_skill_value  # Give points for student strength
                                                else:
                                                    comp_score += (5 - student_skill_value) * 0.5  # Less weight for balance
                                            except (ValueError, TypeError):
                                                continue  # Skip this skill if values aren't numeric
                                            
                                        compatibility_scores.append((idx, comp_score))
                                    
                                    # Sort by compatibility score (higher is better)
                                    compatibility_scores.sort(key=lambda x: x[1], reverse=True)
                                    
                                    # Add most compatible student to the group
                                    if compatibility_scores:
                                        best_match_idx = compatibility_scores[0][0]
                                        group_members.append(best_match_idx)
                                        assigned_students.add(best_match_idx)
                            
                            # Store the group - converting back to original indices
                            if group_members:
                                # Check that indices exist in original_index
                                valid_indices = []
                                for idx in group_members:
                                    if 0 <= idx < len(original_index):
                                        valid_indices.append(original_index.iloc[idx])
                                groups[g] = valid_indices
                    
                    elif method == 'balanced':
                        # Calculate average skill for each student
                        students['avg_skill'] = students[skill_columns].mean(axis=1)
                        
                        # Sort by average skill
                        students = students.sort_values('avg_skill', ascending=False).reset_index(drop=True)
                        
                        # Distribute students so each group has mix of high, medium, and low performers
                        for g in range(n_groups):
                            group_members = []
                            
                            # Select one student from each quartile
                            for q in range(group_size):
                                pos = g + (q * n_groups)
                                if pos < len(students):
                                    group_members.append(students.index[pos])
                            
                            groups[g] = group_members
                    
                    elif method == 'mixed':
                        # Get number of clusters
                        n_clusters = students['cluster'].nunique()
                        
                        # For each group, try to include students from different clusters
                        for g in range(n_groups):
                            group_members = []
                            
                            # Try to add one student from each cluster
                            for c in range(min(n_clusters, group_size)):
                                cluster_students = students[(students['cluster'] == c) & 
                                                       (~students.index.isin([m for group in groups.values() for m in group]))]
                                
                                if len(cluster_students) > 0:
                                    # Take the student with highest overall_skill from this cluster
                                    student_idx = cluster_students.sort_values('overall_skill', ascending=False).index[0]
                                    group_members.append(student_idx)
                            
                            # If we need more students to reach group_size
                            remaining_spots = group_size - len(group_members)
                            if remaining_spots > 0:
                                # Get remaining students
                                remaining_students = students[~students.index.isin([m for group in groups.values() for m in group] + group_members)]
                                
                                # Sort by overall skill (descending)
                                remaining_students = remaining_students.sort_values('overall_skill', ascending=False)
                                
                                # Add top students
                                for i in range(min(remaining_spots, len(remaining_students))):
                                    group_members.append(remaining_students.index[i])
                            
                            groups[g] = group_members
                    
                    # Handle remaining students by adding them to existing groups
                    if method == 'complementary':
                        # Find unassigned students using the tracking set
                        unassigned_indices = [i for i in range(len(students)) if i not in assigned_students]
                        
                        # Add each unassigned student to a group
                        for i, idx in enumerate(unassigned_indices):
                            if i < len(groups):
                                original_idx = original_index.iloc[idx]
                                groups[i % len(groups)].append(original_idx)
                    else:
                        # For other methods, use the traditional approach
                        remaining_students = students[~students.index.isin([m for group in groups.values() for m in group])]
                        
                        for i, idx in enumerate(remaining_students.index):
                            if i < len(groups):
                                groups[i % len(groups)].append(idx)
                    
                    # Convert group indices to actual student data
                    groups_data = {}
                    for g, member_indices in groups.items():
                        try:
                            # Handle the different group formation methods
                            if method == 'complementary':
                                # For complementary method, we're using the original indices
                                try:
                                    # Check if indices exist
                                    valid_indices = [idx for idx in member_indices if idx in students['index'].values]
                                    if valid_indices:
                                        group_df = students.loc[students['index'].isin(valid_indices)].copy()
                                    else:
                                        # If no valid indices, create an empty DataFrame with same columns
                                        group_df = pd.DataFrame(columns=students.columns)
                                except Exception as e:
                                    st.error(f"Error accessing member indices: {str(e)}")
                                    # Create empty DataFrame as fallback
                                    group_df = pd.DataFrame(columns=students.columns)
                            else:
                                # For other methods, we're using DataFrame indices directly
                                try:
                                    # Check if indices exist
                                    valid_indices = [idx for idx in member_indices if idx in students.index]
                                    if valid_indices:
                                        group_df = students.loc[valid_indices].copy()
                                    else:
                                        # If no valid indices, create an empty DataFrame with same columns
                                        group_df = pd.DataFrame(columns=students.columns)
                                except Exception as e:
                                    st.error(f"Error accessing member indices: {str(e)}")
                                    # Create empty DataFrame as fallback
                                    group_df = pd.DataFrame(columns=students.columns)
                                
                            groups_data[g] = {
                                'members': group_df,
                                'size': len(group_df),
                                'avg_skills': group_df[skill_columns].mean().to_dict(),
                                'min_skills': group_df[skill_columns].min().to_dict(),
                                'max_skills': group_df[skill_columns].max().to_dict(),
                                'skill_range': (group_df[skill_columns].max() - group_df[skill_columns].min()).to_dict()
                            }
                        except Exception as e:
                            st.error(f"Error processing group {g}: {str(e)}")
                            # Create an empty group if there was an error
                            groups_data[g] = {
                                'members': pd.DataFrame(),
                                'size': 0,
                                'avg_skills': {skill: 0 for skill in skill_columns},
                                'min_skills': {skill: 0 for skill in skill_columns},
                                'max_skills': {skill: 0 for skill in skill_columns},
                                'skill_range': {skill: 0 for skill in skill_columns}
                            }
                    
                    return groups_data
                
                # Apply group formation with timeout protection
                try:
                    # Add a status message
                    status_text = st.empty()
                    status_text.text("Starting group formation process...")
                    
                    # Apply the group formation function with timeout protection
                    import time
                    start_time = time.time()
                    
                    # For larger datasets or if prior run failed, use simplified method
                    dataset_size = len(st.session_state.clustered_students)
                    status_text.text(f"Dataset size: {dataset_size} students")
                    
                    if dataset_size > 50 and grouping_method == 'complementary':
                        status_text.text("Large dataset detected. Using simplified complementary grouping...")
                        # Don't change the method, but use a shorter timeout
                        max_time = 10  # seconds
                    else:
                        max_time = 30  # seconds
                    
                    status_text.text(f"Forming groups using {grouping_method} method (timeout: {max_time}s)...")
                    groups_data = form_heterogeneous_groups(
                        st.session_state.clustered_students.copy(),  # Use a copy to prevent modifications
                        skill_cols,
                        group_size=group_size,
                        method=grouping_method,
                        max_time=max_time
                    )
                    status_text.text(f"Group formation completed in {time.time() - start_time:.2f} seconds")
                except Exception as e:
                    st.error(f"Error during group formation: {str(e)}")
                    # Try fallback to balanced method if complementary failed
                    if grouping_method == 'complementary':
                        st.warning("Falling back to balanced grouping method...")
                        try:
                            groups_data = form_heterogeneous_groups(
                                st.session_state.clustered_students,
                                skill_cols,
                                group_size=group_size,
                                method='balanced'
                            )
                        except Exception as e2:
                            st.error(f"Fallback also failed: {str(e2)}")
                            st.stop()
                
                # Store in session state
                st.session_state.groups_data = groups_data
                st.session_state.groups_formed = True
                
                # Show success message
                st.success(f"Successfully formed {len(groups_data)} groups using the {grouping_method} method!")
                
                # Preview group formation
                st.subheader("Group Formation Preview")
                
                # Create a DataFrame with group assignments
                all_group_data = []
                
                for group_id, data in groups_data.items():
                    # Add group ID to each student record
                    group_df = data['members'].copy()
                    group_df['group_id'] = group_id
                    
                    # Add to the list
                    all_group_data.append(group_df)
                
                # Combine all groups
                if all_group_data:
                    combined_df = pd.concat(all_group_data, ignore_index=True)
                    
                    # Display the group assignments
                    st.dataframe(combined_df[['group_id'] + skill_cols + ['overall_skill', 'dominant_skill']])
                    
                    # Plot group sizes
                    group_sizes = combined_df['group_id'].value_counts().sort_index()
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.bar(group_sizes.index, group_sizes.values)
                    ax.set_xlabel('Group ID')
                    ax.set_ylabel('Number of Students')
                    ax.set_title('Group Sizes')
                    ax.set_xticks(range(len(group_sizes)))
                    st.pyplot(fig)

# Group Analysis Page
elif page == "Group Analysis":
    if not st.session_state.data_loaded:
        st.warning("Please upload data first on the 'Data Upload' page.")
        st.stop()
        
    if not st.session_state.groups_formed:
        st.warning("Please form groups on the 'Group Formation' page first.")
        st.stop()
    
    st.header("Group Analysis")
    st.markdown("""
    This page provides analysis and visualization of the formed student groups.
    """)
    
    # Get formed groups and skill columns
    groups_data = st.session_state.groups_data
    skill_cols = st.session_state.skill_columns
    
    # Display number of groups
    st.write(f"Number of formed groups: {len(groups_data)}")
    
    # Group selection for detailed view
    group_ids = list(groups_data.keys())
    selected_group = st.selectbox("Select a group to view in detail:", options=group_ids)
    
    # Show selected group details
    if selected_group is not None:
        group_data = groups_data[selected_group]
        
        st.subheader(f"Group {selected_group} Details")
        st.write(f"Group size: {group_data['size']} students")
        
        # Create two columns for layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Group members
            st.write("Group members:")
            st.dataframe(group_data['members'][['overall_skill', 'dominant_skill'] + skill_cols])
        
        with col2:
            # Radar chart for the group's skill profile
            avg_profile = [group_data['avg_skills'][skill] for skill in skill_cols]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=list(avg_profile) + [avg_profile[0]],  # Close the loop
                theta=[col.replace('_', ' ').title() for col in skill_cols] + [skill_cols[0].replace('_', ' ').title()],
                fill='toself',
                name='Group Average'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                title=f"Group {selected_group} Average Skill Profile"
            )
            
            st.plotly_chart(fig)
    
    # Overall group comparison
    st.subheader("Group Comparison")
    
    # Create a DataFrame with group averages
    group_avgs = pd.DataFrame([data['avg_skills'] for data in groups_data.values()])
    group_avgs['group'] = list(groups_data.keys())
    
    # Display the average profiles
    st.write("Average skill profiles for each group:")
    st.dataframe(group_avgs)
    
    # Radar chart for all groups
    st.write("Radar chart comparing all groups:")
    
    fig = go.Figure()
    
    for group_id, data in groups_data.items():
        avg_profile = [data['avg_skills'][skill] for skill in skill_cols]
        
        fig.add_trace(go.Scatterpolar(
            r=list(avg_profile) + [avg_profile[0]],  # Close the loop
            theta=[col.replace('_', ' ').title() for col in skill_cols] + [skill_cols[0].replace('_', ' ').title()],
            fill='toself',
            name=f'Group {group_id}'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title="Comparison of Group Skill Profiles"
    )
    
    st.plotly_chart(fig)
    
    # Skill diversity within groups
    st.subheader("Skill Diversity Within Groups")
    
    # Calculate skill ranges in each group
    group_ranges = pd.DataFrame([data['skill_range'] for data in groups_data.values()])
    group_ranges['group'] = list(groups_data.keys())
    
    # Display the ranges
    st.write("Skill ranges within each group (Max - Min):")
    st.dataframe(group_ranges)
    
    # Bar chart for skill ranges
    fig = px.bar(
        group_ranges.melt(id_vars=['group'], value_vars=skill_cols),
        x='group', y='value', color='variable',
        labels={'variable': 'Skill', 'value': 'Skill Range', 'group': 'Group ID'},
        title='Skill Diversity Within Each Group'
    )
    
    st.plotly_chart(fig)
    
    # Export group assignments
    st.subheader("Export Group Assignments")
    
    if st.button("Export Groups to CSV"):
        # Create a list to store all group data
        all_group_data = []
        
        for group_id, data in groups_data.items():
            # Add group ID to each student record
            group_df = data['members'].copy()
            group_df['group_id'] = group_id
            
            # Add to the list
            all_group_data.append(group_df)
        
        # Combine all groups
        if all_group_data:
            combined_df = pd.concat(all_group_data, ignore_index=True)
            
            # Convert to CSV
            csv = combined_df.to_csv(index=False)
            
            # Create a download link
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="student_groups.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            st.success("Groups ready for download!")

# Project Recommendations Page
elif page == "Project Recommendations":
    if not st.session_state.data_loaded:
        st.warning("Please upload data first on the 'Data Upload' page.")
        st.stop()
        
    if not st.session_state.groups_formed:
        st.warning("Please form groups on the 'Group Formation' page first.")
        st.stop()
    
    st.header("Project and Role Recommendations")
    st.markdown("""
    This page provides tailored project recommendations and role suggestions for each group based on their skill profiles.
    """)
    
    # Get formed groups and skill columns
    groups_data = st.session_state.groups_data
    skill_cols = st.session_state.skill_columns
    
    # Project types based on group skill profiles
    project_types = {
        'high_technical': "Technical development project requiring strong hard skills",
        'high_creative': "Innovation-focused project requiring creative problem solving",
        'high_teamwork': "Complex collaborative project requiring effective team coordination",
        'high_soft_skills': "Client-facing project requiring strong communication and leadership",
        'balanced': "Multifaceted project requiring balanced application of various skills"
    }
    
    # Define role templates
    role_templates = {
        'technical_lead': "Technical implementation and problem-solving",
        'creative_director': "Idea generation and innovative solutions", 
        'team_coordinator': "Task management and team coordination",
        'client_liaison': "Client communication and presentation"
    }
    
    # Group selection for recommendations
    group_ids = list(groups_data.keys())
    selected_group = st.selectbox("Select a group:", options=group_ids)
    
    if selected_group is not None:
        st.subheader(f"Recommendations for Group {selected_group}")
        
        data = groups_data[selected_group]
        
        # Get group average skills
        avg_skills = data['avg_skills']
        
        # Determine group's overall strength
        top_skill = max(avg_skills, key=avg_skills.get)
        top_skill_score = avg_skills[top_skill]
        
        # Determine if the group is balanced or has a clear strength
        skill_values = list(avg_skills.values())
        skill_std = np.std(skill_values)
        
        # Recommend project type
        st.write("### Project Recommendation")
        
        if skill_std < 0.5:  # Balanced group
            recommended_project = project_types['balanced']
            st.info(f"📋 **Recommended Project Type:** {recommended_project}")
            st.write("This group has a balanced skill profile and should handle diverse project requirements well.")
        else:  # Group with specific strengths
            if 'hard_skills' in avg_skills and avg_skills['hard_skills'] > 4:
                recommended_project = project_types['high_technical']
            elif 'creativity' in avg_skills and avg_skills['creativity'] > 4:
                recommended_project = project_types['high_creative']
            elif 'teamwork' in avg_skills and avg_skills['teamwork'] > 4:
                recommended_project = project_types['high_teamwork']
            elif 'soft_skills' in avg_skills and avg_skills['soft_skills'] > 4:
                recommended_project = project_types['high_soft_skills']
            else:
                recommended_project = project_types['balanced']
                
            st.info(f"📋 **Recommended Project Type:** {recommended_project}")
            st.write(f"This group shows particular strength in {top_skill.replace('_', ' ').title()} ({top_skill_score:.2f}/5)")
        
        # Suggest roles for each group member
        st.write("### Suggested Role Assignments")
        
        # Create a dataframe for role assignments
        role_data = []
        
        for i, (idx, student) in enumerate(data['members'].iterrows(), 1):
            # Find student's top skill
            student_skills = {skill: student[skill] for skill in skill_cols}
            top_student_skill = max(student_skills, key=student_skills.get)
            
            # Assign role based on top skill
            if 'hard_skills' in student_skills and top_student_skill == 'hard_skills':
                role = role_templates['technical_lead']
            elif 'creativity' in student_skills and top_student_skill == 'creativity':
                role = role_templates['creative_director']
            elif 'teamwork' in student_skills and top_student_skill == 'teamwork':
                role = role_templates['team_coordinator']
            elif 'soft_skills' in student_skills and top_student_skill == 'soft_skills':
                role = role_templates['client_liaison']
            else:
                # Determine role based on relative strengths
                strengths = []
                for skill, score in student_skills.items():
                    if score > 3.5:
                        strengths.append(skill.replace('_', ' '))
                
                if not strengths:
                    strengths = ['supportive']
                    
                role = f"General support with focus on {', '.join(strengths)} tasks"
            
            # Get student name/id
            if 'student_id' in student:
                student_name = f"Student {student['student_id']}"
            elif 'name' in student:
                student_name = student['name']
            else:
                student_name = f"Student {idx}"
                
            # Add to role data
            role_data.append({
                'Student': student_name,
                'Top Skill': top_student_skill.replace('_', ' ').title(),
                'Recommended Role': role
            })
        
        # Display role assignments
        role_df = pd.DataFrame(role_data)
        st.table(role_df)
        
        # Development areas and considerations
        st.write("### Key Development Areas")
        
        # Identify the group's weakest skill
        weakest_skill = min(avg_skills, key=avg_skills.get)
        st.write(f"- Focus on developing **{weakest_skill.replace('_', ' ').title()}** ({avg_skills[weakest_skill]:.2f}/5)")
        
        # Additional recommendations based on skill distribution
        if skill_std > 1.0:
            st.write("- Be aware of significant skill disparities within the group")
            st.write("- Consider peer mentoring for knowledge sharing")
        
        # Identify critical gaps
        critical_gaps = []
        for skill in skill_cols:
            if data['max_skills'][skill] < 3.0:  # No one in group is strong in this area
                critical_gaps.append(skill)
                
        if critical_gaps:
            st.write(f"- Critical gaps: No team member is strong in {', '.join([g.replace('_', ' ').title() for g in critical_gaps])}")
            st.write("- Consider seeking external support or focused training in these areas")
        
        # Show radar chart with group profile
        st.write("### Group Skill Profile")
        
        avg_profile = [avg_skills[skill] for skill in skill_cols]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=list(avg_profile) + [avg_profile[0]],  # Close the loop
            theta=[col.replace('_', ' ').title() for col in skill_cols] + [skill_cols[0].replace('_', ' ').title()],
            fill='toself',
            name='Group Average'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )
            ),
            title=f"Group {selected_group} Skill Profile"
        )
        
        st.plotly_chart(fig)
