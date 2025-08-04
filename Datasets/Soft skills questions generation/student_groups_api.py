import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import warnings
import uvicorn
import io

# Suppress warnings
warnings.filterwarnings('ignore')

# Initialize FastAPI
app = FastAPI(
    title="Student Heterogeneous Group Formation API",
    description="API for forming balanced student teams based on complementary skill profiles",
    version="1.0.0"
)

# Define data models
class Student(BaseModel):
    student_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    nationality: Optional[str] = None
    hard_skills: float
    soft_skills: float
    teamwork: float
    creativity: float
    class_name: Optional[str] = None

class StudentGroup(BaseModel):
    group_id: int
    members: List[Dict[str, Any]]
    size: int
    avg_skills: Dict[str, float]
    min_skills: Dict[str, float]
    max_skills: Dict[str, float]
    skill_range: Dict[str, float]

class GroupFormationRequest(BaseModel):
    group_size: int = 4
    method: str = "complementary"  # 'complementary', 'balanced', or 'mixed'
    n_clusters: int = 4  # for initial clustering

class GroupFormationResponse(BaseModel):
    groups: Dict[str, Any]
    summary: Dict[str, Any]

# Helper functions from the notebook
def preprocess_student_data(df, skill_columns):
    """
    Preprocess student data for clustering.
    """
    # Create a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Handle missing values if any
    if processed_df[skill_columns].isnull().sum().sum() > 0:
        # Fill missing values with mean of the column
        for col in skill_columns:
            if processed_df[col].isnull().sum() > 0:
                mean_val = processed_df[col].mean()
                processed_df[col] = processed_df[col].fillna(mean_val)
    
    # Add derived features
    # Overall skill level (average across all skills)
    processed_df['overall_skill'] = processed_df[skill_columns].mean(axis=1)
    
    # Skill variance (how specialized or balanced a student is)
    processed_df['skill_variance'] = processed_df[skill_columns].var(axis=1)
    
    # Dominant skill area
    processed_df['dominant_skill'] = processed_df[skill_columns].idxmax(axis=1)
    
    # Weakest skill area
    processed_df['weakest_skill'] = processed_df[skill_columns].idxmin(axis=1)
    
    # Create normalized versions of the skills (0-1 scale)
    scaler = MinMaxScaler()
    normalized_skills = scaler.fit_transform(processed_df[skill_columns])
    
    for i, col in enumerate(skill_columns):
        processed_df[f'norm_{col}'] = normalized_skills[:, i]
        
    return processed_df

def cluster_student_skills(df, skill_columns, n_clusters=4):
    """
    Cluster students based on their skill profiles.
    """
    # Create a copy to avoid modifying the original
    clustered_df = df.copy()
    
    # Extract features for clustering (normalized skill scores)
    norm_cols = [f'norm_{col}' for col in skill_columns]
    if all(col in clustered_df.columns for col in norm_cols):
        X = clustered_df[norm_cols].values
    else:
        X = clustered_df[skill_columns].values
    
    # Scale the data to have mean=0 and variance=1
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Calculate silhouette scores for different k values
    silhouette_scores = []
    max_clusters = min(10, len(df) - 1)  # Don't try more clusters than data points minus 1
    
    for i in range(2, max_clusters + 1):  # Silhouette score needs at least 2 clusters
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Calculate silhouette score
        if len(set(cluster_labels)) > 1:  # Ensure we have at least 2 clusters with data points
            score = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(score)
        else:
            silhouette_scores.append(0)
    
    # Find the k with the best silhouette score
    best_k_silhouette = silhouette_scores.index(max(silhouette_scores)) + 2  # +2 because we started from 2
    
    # Use either the specified number of clusters or the best one based on silhouette
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=300, n_init=10, random_state=42)
    clustered_df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Calculate silhouette score for the selected number of clusters
    silhouette_avg = silhouette_score(X_scaled, clustered_df['cluster'])
    
    # Get cluster centers (in the original scale)
    centers_scaled = kmeans.cluster_centers_
    centers_original = scaler.inverse_transform(centers_scaled)
    
    # Create a DataFrame for cluster centers
    if all(col in clustered_df.columns for col in norm_cols):
        centers_df = pd.DataFrame(centers_original, columns=norm_cols)
        # Rename columns back to original
        centers_df.columns = [col.replace('norm_', '') for col in centers_df.columns]
    else:
        centers_df = pd.DataFrame(centers_original, columns=skill_columns)
    
    centers_df['cluster'] = range(n_clusters)
    
    return clustered_df, centers_df, X_scaled, silhouette_avg

def form_heterogeneous_groups(df, skill_columns, group_size=4, method='complementary'):
    """
    Form heterogeneous student groups with complementary skills.
    """
    # Create a working copy
    students = df.copy()
    
    # Shuffle the students to ensure randomness in selection
    students = students.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Calculate number of groups
    n_students = len(students)
    n_groups = n_students // group_size
    remainder = n_students % group_size
    
    # Initialize groups
    groups = {}
    
    if method == 'complementary':
        # Sort students by overall skill level
        students = students.sort_values('overall_skill', ascending=False).reset_index(drop=True)
        
        # For each group, select students with diverse skill strengths
        for g in range(n_groups):
            group_members = []
            
            # Start with students that have different dominant skills
            remaining_students = students[~students.index.isin([m for group in groups.values() for m in group])]
            
            # Select first student (highest overall skill not yet assigned)
            if len(remaining_students) > 0:
                first_student_idx = remaining_students.index[0]
                group_members.append(first_student_idx)
                first_student = remaining_students.loc[first_student_idx]
                
                # Find students with complementary skills
                for _ in range(1, group_size):
                    if len(remaining_students) <= 1:
                        break
                        
                    # Remove already selected students
                    remaining_students = students[~students.index.isin([m for group in groups.values() for m in group] + group_members)]
                    
                    if len(remaining_students) == 0:
                        break
                        
                    # Create a compatibility score - higher for students with strengths
                    # where the current group is weak
                    compatibility_scores = []
                    
                    # Get current group skill profile
                    current_group_skills = students.loc[group_members, skill_columns].mean()
                    
                    for idx, student in remaining_students.iterrows():
                        # Calculate how complementary this student is to the current group
                        # High score if student is strong where group is weak
                        comp_score = 0
                        for skill in skill_columns:
                            # Weighted difference - give higher importance to skills where group is weak
                            weight = 1 + (5 - current_group_skills[skill]) / 5
                            comp_score += weight * (student[skill] - current_group_skills[skill])
                            
                        compatibility_scores.append((idx, comp_score))
                    
                    # Sort by compatibility score (higher is better)
                    compatibility_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Add most compatible student to the group
                    if compatibility_scores:
                        group_members.append(compatibility_scores[0][0])
            
            # Store the group
            if group_members:
                groups[g] = group_members
        
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
    
    else:
        raise ValueError(f"Unknown grouping method: {method}")
    
    # Handle remaining students by adding them to existing groups
    remaining_students = students[~students.index.isin([m for group in groups.values() for m in group])]
    
    for i, idx in enumerate(remaining_students.index):
        if i < len(groups):
            groups[i].append(idx)
    
    # Convert group indices to actual student data
    groups_data = {}
    for g, member_indices in groups.items():
        group_df = students.loc[member_indices].copy()
        groups_data[g] = {
            'members': group_df.to_dict('records'),
            'size': len(group_df),
            'avg_skills': group_df[skill_columns].mean().to_dict(),
            'min_skills': group_df[skill_columns].min().to_dict(),
            'max_skills': group_df[skill_columns].max().to_dict(),
            'skill_range': (group_df[skill_columns].max() - group_df[skill_columns].min()).to_dict()
        }
    
    return groups_data

def generate_group_summary(groups, skill_columns):
    """
    Generate summary statistics for all formed groups
    """
    # Create summary data
    summary = {
        "num_groups": len(groups),
        "total_students": sum(data["size"] for data in groups.values()),
        "avg_group_size": sum(data["size"] for data in groups.values()) / len(groups),
        "skill_stats": {}
    }
    
    # Get all group averages
    all_avgs = pd.DataFrame([data['avg_skills'] for data in groups.values()])
    
    # Calculate statistics across groups
    for skill in skill_columns:
        summary["skill_stats"][skill] = {
            "mean": float(all_avgs[skill].mean()),
            "std": float(all_avgs[skill].std()),
            "min": float(all_avgs[skill].min()),
            "max": float(all_avgs[skill].max())
        }
    
    # Calculate average skill range (diversity within groups)
    all_ranges = pd.DataFrame([data['skill_range'] for data in groups.values()])
    summary["avg_skill_ranges"] = {skill: float(all_ranges[skill].mean()) for skill in skill_columns}
    
    return summary

def recommend_projects_and_roles(groups, skill_columns):
    """
    Generate project type and role recommendations for each group.
    """
    recommendations = {}
    
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
    
    for group_id, data in groups.items():
        group_rec = {}
        
        # Get group average skills
        avg_skills = data['avg_skills']
        
        # Determine group's overall strength
        top_skill = max(avg_skills, key=avg_skills.get)
        top_skill_score = avg_skills[top_skill]
        
        # Determine if the group is balanced or has a clear strength
        skill_values = list(avg_skills.values())
        skill_std = np.std(skill_values)
        
        # Recommend project type
        if skill_std < 0.5:  # Balanced group
            group_rec["project_type"] = project_types['balanced']
            group_rec["project_note"] = "This group has a balanced skill profile and should handle diverse project requirements well."
        else:  # Group with specific strengths
            if 'hard_skills' in avg_skills and avg_skills['hard_skills'] > 4:
                group_rec["project_type"] = project_types['high_technical']
            elif 'creativity' in avg_skills and avg_skills['creativity'] > 4:
                group_rec["project_type"] = project_types['high_creative']
            elif 'teamwork' in avg_skills and avg_skills['teamwork'] > 4:
                group_rec["project_type"] = project_types['high_teamwork']
            elif 'soft_skills' in avg_skills and avg_skills['soft_skills'] > 4:
                group_rec["project_type"] = project_types['high_soft_skills']
            else:
                group_rec["project_type"] = project_types['balanced']
                
            group_rec["strength_note"] = f"This group shows particular strength in {top_skill.replace('_', ' ').title()} ({top_skill_score:.2f}/5)"
        
        # Suggest roles for each group member based on individual strengths
        member_roles = []
        
        for i, student in enumerate(data['members']):
            student_role = {}
            
            # Find student's top skill
            student_skills = {skill: student[skill] for skill in skill_columns if skill in student}
            top_student_skill = max(student_skills, key=student_skills.get)
            
            # Get student name/id
            if 'student_id' in student:
                student_name = f"Student {student['student_id']}"
            elif 'name' in student:
                student_name = student['name']
            else:
                student_name = f"Member {i+1}"
            
            student_role["name"] = student_name
            
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
                if student.get('hard_skills', 0) > 3.5:
                    strengths.append('technical')
                if student.get('creativity', 0) > 3.5:
                    strengths.append('creative')
                if student.get('teamwork', 0) > 3.5:
                    strengths.append('teamwork')
                if student.get('soft_skills', 0) > 3.5:
                    strengths.append('communication')
                
                if not strengths:
                    strengths = ['supportive']
                    
                role = f"General support with focus on {', '.join(strengths)} tasks"
            
            student_role["role"] = role
            student_role["top_skill"] = top_student_skill.replace('_', ' ').title()
            
            member_roles.append(student_role)
        
        group_rec["member_roles"] = member_roles
        
        # Development areas
        group_rec["development_areas"] = []
        
        # Identify the group's weakest skill
        weakest_skill = min(avg_skills, key=avg_skills.get)
        group_rec["development_areas"].append(
            f"Focus on developing {weakest_skill.replace('_', ' ').title()} ({avg_skills[weakest_skill]:.2f}/5)"
        )
        
        # Additional recommendations based on skill distribution
        if skill_std > 1.0:
            group_rec["development_areas"].append(
                "Be aware of significant skill disparities within the group; Consider peer mentoring for knowledge sharing"
            )
        
        # Identify if there are any critical gaps (all members weak in same area)
        critical_gaps = []
        for skill in skill_columns:
            if skill in data['max_skills'] and data['max_skills'][skill] < 3.0:  # No one in group is strong in this area
                critical_gaps.append(skill)
                
        if critical_gaps:
            group_rec["development_areas"].append(
                f"Critical gaps: No team member is strong in {', '.join([g.replace('_', ' ').title() for g in critical_gaps])}; Consider seeking external support or focused training"
            )
            
        recommendations[group_id] = group_rec
    
    return recommendations

# API Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Student Heterogeneous Group Formation API", 
        "version": "1.0.0",
        "endpoints": {
            "/form-groups": "POST - Form heterogeneous student groups",
            "/upload-csv": "POST - Upload student data CSV and form groups",
            "/docs": "API Documentation"
        }
    }

@app.post("/form-groups", response_model=GroupFormationResponse)
def form_groups(students: List[Student], request: GroupFormationRequest):
    """
    Form heterogeneous student groups based on provided student data
    """
    try:
        # Convert to dataframe
        df = pd.DataFrame([s.dict() for s in students])
        
        # Define skill columns
        skill_columns = ['hard_skills', 'soft_skills', 'teamwork', 'creativity']
        
        # Check that we have sufficient data
        if len(df) < request.group_size:
            raise HTTPException(status_code=400, detail=f"Not enough students provided. Minimum required: {request.group_size}")
            
        if not all(col in df.columns for col in skill_columns):
            raise HTTPException(status_code=400, detail=f"Missing required skill columns. Required: {skill_columns}")
        
        # Preprocess data
        processed_df = preprocess_student_data(df, skill_columns)
        
        # Cluster students
        clustered_df, _, _, _ = cluster_student_skills(processed_df, skill_columns, request.n_clusters)
        
        # Form groups
        groups = form_heterogeneous_groups(
            clustered_df, 
            skill_columns, 
            group_size=request.group_size,
            method=request.method
        )
        
        # Generate group summary
        summary = generate_group_summary(groups, skill_columns)
        
        # Generate recommendations
        recommendations = recommend_projects_and_roles(groups, skill_columns)
        
        # Add recommendations to groups
        for group_id in groups.keys():
            groups[group_id]["recommendations"] = recommendations[group_id]
        
        return {
            "groups": groups,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-csv")
async def upload_csv_form_groups(
    file: UploadFile = File(...),
    group_size: int = Form(4),
    method: str = Form("complementary"),
    n_clusters: int = Form(4)
):
    """
    Upload a CSV file with student data and form heterogeneous groups
    """
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Define skill columns
        skill_columns = [col for col in df.columns if col.lower() in ['hard_skills', 'soft_skills', 'teamwork', 'creativity']]
        
        if not skill_columns:
            raise HTTPException(status_code=400, 
                                detail="CSV file must contain at least one of these columns: 'hard_skills', 'soft_skills', 'teamwork', 'creativity'")
        
        # Check that we have sufficient data
        if len(df) < group_size:
            raise HTTPException(status_code=400, detail=f"Not enough students in CSV. Minimum required: {group_size}")
        
        # Preprocess data
        processed_df = preprocess_student_data(df, skill_columns)
        
        # Cluster students
        clustered_df, _, _, _ = cluster_student_skills(processed_df, skill_columns, n_clusters)
        
        # Form groups
        groups = form_heterogeneous_groups(
            clustered_df, 
            skill_columns, 
            group_size=group_size,
            method=method
        )
        
        # Generate group summary
        summary = generate_group_summary(groups, skill_columns)
        
        # Generate recommendations
        recommendations = recommend_projects_and_roles(groups, skill_columns)
        
        # Add recommendations to groups
        for group_id in groups.keys():
            groups[group_id]["recommendations"] = recommendations[group_id]
        
        return {
            "groups": groups,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run server when executed directly
if __name__ == "__main__":
    uvicorn.run("student_groups_api:app", host="0.0.0.0", port=8000, reload=True)
