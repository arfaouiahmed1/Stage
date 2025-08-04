from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import json
from datetime import datetime
import uuid
import os
import io
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Initialize FastAPI app
app = FastAPI(
    title="Student Heterogeneous Clustering API",
    description="API for clustering students with complementary skills for optimal peer learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class StudentData(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    student_name: str = Field(..., description="Student's full name")
    gender: str = Field(..., description="Student's gender (Male/Female)")
    age: int = Field(..., ge=18, le=45, description="Student's age")
    nationality: str = Field(..., description="Student's nationality")
    communication_score: float = Field(..., ge=1.0, le=5.0, description="Communication skill score (1-5)")
    leadership_score: float = Field(..., ge=1.0, le=5.0, description="Leadership skill score (1-5)")
    time_management_score: float = Field(..., ge=1.0, le=5.0, description="Time management skill score (1-5)")
    analytical_score: float = Field(..., ge=1.0, le=5.0, description="Analytical skill score (1-5)")

class ClusteringRequest(BaseModel):
    students: List[StudentData] = Field(..., description="List of students to cluster")
    target_group_size: Optional[int] = Field(default=4, ge=2, le=8, description="Target number of students per group")
    force_heterogeneous: Optional[bool] = Field(default=True, description="Force heterogeneous grouping")

class ClusterInfo(BaseModel):
    cluster_id: int
    cluster_name: str
    description: str
    complementary_skills: List[str]
    similar_skills: List[str]
    demographic_diversity: Dict[str, Any]
    student_count: int

class StudentClusterAssignment(BaseModel):
    student_id: str
    student_name: str
    cluster_id: int
    cluster_name: str
    skill_profile: Dict[str, float]
    strengths: List[str]
    areas_for_development: List[str]

class ClusteringResponse(BaseModel):
    request_id: str
    timestamp: str
    total_students: int
    total_groups: int
    average_complementarity_score: float
    clusters: List[ClusterInfo]
    student_assignments: List[StudentClusterAssignment]
    visualization_data: Optional[Dict[str, Any]] = None

class QuizSubmission(BaseModel):
    student_name: str
    gender: str
    age: int
    nationality: str
    communication_answers: List[int] = Field(..., min_items=5, max_items=5)
    leadership_answers: List[int] = Field(..., min_items=5, max_items=5)
    time_management_answers: List[int] = Field(..., min_items=5, max_items=5)
    analytical_answers: List[int] = Field(..., min_items=5, max_items=5)

# Alternative models for the existing group formation API
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

class GroupFormationRequest(BaseModel):
    group_size: int = 4
    method: str = "complementary"  # 'complementary', 'balanced', or 'mixed'
    n_clusters: int = 4  # for initial clustering

class GroupFormationResponse(BaseModel):
    groups: Dict[str, Any]
    summary: Dict[str, Any]

# Global storage for student data
student_database = []
clustering_history = []

def calculate_quiz_scores(answers: List[int]) -> float:
    """Calculate normalized score from quiz answers (1-5 scale)"""
    if not answers or len(answers) != 5:
        raise ValueError("Must provide exactly 5 answers")
    
    # Convert answers to scores (1-5 scale)
    total_score = sum(answers)
    # Normalize to 1-5 range (assuming answers are 1-5)
    normalized_score = 1 + ((total_score - 5) / 20) * 4
    return round(normalized_score, 2)

def create_heterogeneous_groups(students_df: pd.DataFrame, target_group_size: int = 4) -> List[List[int]]:
    """Create heterogeneous groups by pairing high and low performers"""
    n_students = len(students_df)
    n_groups = max(2, n_students // target_group_size)
    
    # Calculate skill percentiles for each student
    score_columns = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
    skill_percentiles = {}
    
    for skill in score_columns:
        skill_values = students_df[skill].values
        percentiles = []
        for i, value in enumerate(skill_values):
            below_count = sum(1 for v in skill_values if v < value)
            percentile = below_count / len(skill_values)
            percentiles.append(percentile)
        skill_percentiles[skill] = percentiles
    
    # Calculate student diversity scores
    student_diversity_scores = []
    for i in range(n_students):
        diversity_score = 0
        for skill in score_columns:
            percentile = skill_percentiles[skill][i]
            if percentile > 0.8 or percentile < 0.2:
                diversity_score += 1
        student_diversity_scores.append(diversity_score)
    
    # Sort students by diversity (most diverse first)
    student_indices = list(range(n_students))
    student_indices.sort(key=lambda i: student_diversity_scores[i], reverse=True)
    
    # Distribute students to groups ensuring heterogeneity
    groups = [[] for _ in range(n_groups)]
    for i, student_idx in enumerate(student_indices):
        group_idx = i % n_groups
        groups[group_idx].append(student_idx)
    
    return groups

def analyze_group_complementarity(group_students: List[int], students_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze complementarity within a group"""
    group_data = students_df.iloc[group_students]
    score_columns = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
    skill_names = ['Communication', 'Leadership', 'Time Management', 'Analytical']
    
    complementary_skills = []
    similar_skills = []
    
    for skill, name in zip(score_columns, skill_names):
        skill_values = group_data[skill].values
        skill_std = np.std(skill_values)
        skill_range = np.max(skill_values) - np.min(skill_values)
        
        # Check if group has both high and low performers
        high_performers = sum(1 for v in skill_values if v > 4.0)
        low_performers = sum(1 for v in skill_values if v < 2.5)
        
        if high_performers > 0 and low_performers > 0 and skill_range > 1.5:
            complementary_skills.append(name)
        elif skill_std < 0.5:
            similar_skills.append(name)
    
    # Calculate demographic diversity
    gender_diversity = group_data['gender'].nunique() if 'gender' in group_data.columns else 1
    nationality_diversity = group_data['nationality'].nunique() if 'nationality' in group_data.columns else 1
    age_range = group_data['age'].max() - group_data['age'].min() if 'age' in group_data.columns else 0
    
    return {
        'complementary_skills': complementary_skills,
        'similar_skills': similar_skills,
        'demographic_diversity': {
            'gender_diversity': gender_diversity,
            'nationality_diversity': nationality_diversity,
            'age_range': age_range
        }
    }

def generate_cluster_description(complementary_skills: List[str], similar_skills: List[str], 
                               demographic_diversity: Dict[str, Any]) -> str:
    """Generate human-readable cluster description"""
    if complementary_skills:
        desc = f"This learning group has diverse skill levels in {', '.join(complementary_skills)}. "
        desc += "This creates excellent peer learning opportunities where students can help each other develop these skills."
    else:
        desc = "This learning group has balanced skill levels across all areas, providing a supportive environment for collaborative learning."
    
    if similar_skills:
        desc += f" Students in this group have similar levels in {', '.join(similar_skills)} skills."
    
    if demographic_diversity['gender_diversity'] > 1 or demographic_diversity['nationality_diversity'] > 1:
        desc += " The group also includes demographic diversity."
    
    return desc

def generate_cluster_name(complementary_skills: List[str], demographic_diversity: Dict[str, Any]) -> str:
    """Generate cluster name based on complementarity"""
    if len(complementary_skills) >= 2:
        name = f"Complementary {', '.join(complementary_skills[:2])} Group"
    elif len(complementary_skills) == 1:
        name = f"Enhanced {complementary_skills[0]} Group"
    else:
        name = f"Balanced Learning Group"
    
    if demographic_diversity['gender_diversity'] > 1 or demographic_diversity['nationality_diversity'] > 1:
        name = "Diverse " + name
    
    return name

# Helper functions from the existing group formation API
def preprocess_student_data(df, skill_columns):
    """Preprocess student data for clustering."""
    processed_df = df.copy()
    
    # Handle missing values if any
    if processed_df[skill_columns].isnull().sum().sum() > 0:
        for col in skill_columns:
            if processed_df[col].isnull().sum() > 0:
                mean_val = processed_df[col].mean()
                processed_df[col] = processed_df[col].fillna(mean_val)
    
    # Add derived features
    processed_df['overall_skill'] = processed_df[skill_columns].mean(axis=1)
    processed_df['skill_variance'] = processed_df[skill_columns].var(axis=1)
    processed_df['dominant_skill'] = processed_df[skill_columns].idxmax(axis=1)
    processed_df['weakest_skill'] = processed_df[skill_columns].idxmin(axis=1)
    
    # Create normalized versions of the skills (0-1 scale)
    scaler = MinMaxScaler()
    normalized_skills = scaler.fit_transform(processed_df[skill_columns])
    
    for i, col in enumerate(skill_columns):
        processed_df[f'norm_{col}'] = normalized_skills[:, i]
        
    return processed_df

def cluster_student_skills(df, skill_columns, n_clusters=4):
    """Cluster students based on their skill profiles."""
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
    
    # Use specified number of clusters
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
        centers_df.columns = [col.replace('norm_', '') for col in centers_df.columns]
    else:
        centers_df = pd.DataFrame(centers_original, columns=skill_columns)
    
    centers_df['cluster'] = range(n_clusters)
    
    return clustered_df, centers_df, X_scaled, silhouette_avg

def form_heterogeneous_groups_v2(df, skill_columns, group_size=4, method='complementary'):
    """Form heterogeneous student groups with complementary skills (alternative approach)."""
    students = df.copy()
    students = students.sample(frac=1, random_state=42).reset_index(drop=True)
    
    n_students = len(students)
    n_groups = n_students // group_size
    
    groups = {}
    
    if method == 'complementary':
        students = students.sort_values('overall_skill', ascending=False).reset_index(drop=True)
        
        for g in range(n_groups):
            group_members = []
            remaining_students = students[~students.index.isin([m for group in groups.values() for m in group])]
            
            if len(remaining_students) > 0:
                first_student_idx = remaining_students.index[0]
                group_members.append(first_student_idx)
                
                for _ in range(1, group_size):
                    if len(remaining_students) <= 1:
                        break
                        
                    remaining_students = students[~students.index.isin([m for group in groups.values() for m in group] + group_members)]
                    
                    if len(remaining_students) == 0:
                        break
                        
                    compatibility_scores = []
                    current_group_skills = students.loc[group_members, skill_columns].mean()
                    
                    for idx, student in remaining_students.iterrows():
                        comp_score = 0
                        for skill in skill_columns:
                            weight = 1 + (5 - current_group_skills[skill]) / 5
                            comp_score += weight * (student[skill] - current_group_skills[skill])
                            
                        compatibility_scores.append((idx, comp_score))
                    
                    compatibility_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    if compatibility_scores:
                        group_members.append(compatibility_scores[0][0])
            
            if group_members:
                groups[g] = group_members
    
    # Handle remaining students
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
    """Generate summary statistics for all formed groups"""
    summary = {
        "num_groups": len(groups),
        "total_students": sum(data["size"] for data in groups.values()),
        "avg_group_size": sum(data["size"] for data in groups.values()) / len(groups),
        "skill_stats": {}
    }
    
    all_avgs = pd.DataFrame([data['avg_skills'] for data in groups.values()])
    
    for skill in skill_columns:
        summary["skill_stats"][skill] = {
            "mean": float(all_avgs[skill].mean()),
            "std": float(all_avgs[skill].std()),
            "min": float(all_avgs[skill].min()),
            "max": float(all_avgs[skill].max())
        }
    
    all_ranges = pd.DataFrame([data['skill_range'] for data in groups.values()])
    summary["avg_skill_ranges"] = {skill: float(all_ranges[skill].mean()) for skill in skill_columns}
    
    return summary

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def get_test_interface():
    """Serve the test interface HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Student Clustering API Test Interface</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            button {
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            button:hover {
                background-color: #2980b9;
            }
            .success {
                background-color: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .result {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 10px 0;
                max-height: 400px;
                overflow-y: auto;
            }
            .tabs {
                display: flex;
                border-bottom: 1px solid #ddd;
                margin-bottom: 20px;
            }
            .tab {
                padding: 10px 20px;
                cursor: pointer;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-bottom: none;
                margin-right: 5px;
            }
            .tab.active {
                background-color: white;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .file-upload {
                border: 2px dashed #3498db;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            .sample-data {
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 12px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Student Clustering API Test Interface</h1>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('upload')">📁 Upload Dataset</div>
                <div class="tab" onclick="showTab('quiz')">📝 Quiz Submission</div>
                <div class="tab" onclick="showTab('clustering')">🔄 Clustering</div>
                <div class="tab" onclick="showTab('management')">⚙️ Data Management</div>
            </div>

            <!-- Upload Dataset Tab -->
            <div id="upload" class="tab-content active">
                <h2>Upload Your Dataset</h2>
                <p>Upload a CSV file with student data. Your dataset should contain columns matching one of these formats:</p>
                
                <div class="sample-data">
                <strong>Format 1 (Quiz-based):</strong><br>
                student_id, student_name, gender, age, nationality, communication_score, leadership_score, time_management_score, analytical_score<br><br>
                <strong>Format 2 (Skills-based):</strong><br>
                student_id, first_name, last_name, gender, age, nationality, hard_skills, soft_skills, teamwork, creativity
                </div>

                <div class="form-group">
                    <div class="file-upload">
                        <input type="file" id="csvFile" accept=".csv" />
                        <p>Drag and drop your CSV file here or click to select</p>
                    </div>
                </div>

                <div class="form-group">
                    <label for="groupSize">Group Size:</label>
                    <input type="number" id="groupSize" value="4" min="2" max="8" />
                </div>

                <div class="form-group">
                    <label for="method">Clustering Method:</label>
                    <select id="method">
                        <option value="complementary">Complementary Skills</option>
                        <option value="balanced">Balanced Groups</option>
                        <option value="mixed">Mixed Approach</option>
                    </select>
                </div>

                <button onclick="uploadAndCluster()">📊 Upload & Create Groups</button>
                <button onclick="downloadSampleCSV()">📥 Download Sample CSV</button>
            </div>

            <!-- Quiz Submission Tab -->
            <div id="quiz" class="tab-content">
                <h2>Submit Individual Quiz</h2>
                <form id="quizForm">
                    <div class="form-group">
                        <label for="studentName">Student Name:</label>
                        <input type="text" id="studentName" required />
                    </div>
                    
                    <div class="form-group">
                        <label for="gender">Gender:</label>
                        <select id="gender" required>
                            <option value="">Select Gender</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="age">Age:</label>
                        <input type="number" id="age" min="18" max="45" required />
                    </div>
                    
                    <div class="form-group">
                        <label for="nationality">Nationality:</label>
                        <input type="text" id="nationality" required />
                    </div>

                    <h3>Skill Assessment (Rate 1-5 for each question)</h3>
                    
                    <div class="form-group">
                        <label>Communication Skills (5 questions):</label>
                        <input type="text" id="commAnswers" placeholder="e.g., 4,3,5,4,3" />
                    </div>
                    
                    <div class="form-group">
                        <label>Leadership Skills (5 questions):</label>
                        <input type="text" id="leadAnswers" placeholder="e.g., 3,4,2,5,4" />
                    </div>
                    
                    <div class="form-group">
                        <label>Time Management Skills (5 questions):</label>
                        <input type="text" id="timeAnswers" placeholder="e.g., 5,4,4,3,5" />
                    </div>
                    
                    <div class="form-group">
                        <label>Analytical Skills (5 questions):</label>
                        <input type="text" id="analyAnswers" placeholder="e.g., 4,5,3,4,4" />
                    </div>
                    
                    <button type="submit">📝 Submit Quiz</button>
                </form>
            </div>

            <!-- Clustering Tab -->
            <div id="clustering" class="tab-content">
                <h2>Perform Clustering on Stored Data</h2>
                <p>Current students in database: <span id="studentCount">0</span></p>
                
                <div class="form-group">
                    <label for="clusterGroupSize">Target Group Size:</label>
                    <input type="number" id="clusterGroupSize" value="4" min="2" max="8" />
                </div>
                
                <button onclick="performClustering()">🔄 Create Groups from Database</button>
                <button onclick="getStudents()">👥 View All Students</button>
            </div>

            <!-- Data Management Tab -->
            <div id="management" class="tab-content">
                <h2>Data Management</h2>
                <button onclick="getStudents()">👥 View All Students</button>
                <button onclick="getClusteringHistory()">📊 View Clustering History</button>
                <button onclick="clearAllData()">🗑️ Clear All Data</button>
                <button onclick="healthCheck()">❤️ Health Check</button>
            </div>
        </div>

        <div class="container">
            <h2>Results</h2>
            <div id="results"></div>
        </div>

        <script>
            function showTab(tabName) {
                // Hide all tab contents
                const contents = document.querySelectorAll('.tab-content');
                contents.forEach(content => content.classList.remove('active'));
                
                // Remove active class from all tabs
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab content
                document.getElementById(tabName).classList.add('active');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
            }

            function showResult(data, isError = false) {
                const resultsDiv = document.getElementById('results');
                const className = isError ? 'error' : 'success';
                resultsDiv.innerHTML = `<div class="${className}"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
            }

            async function uploadAndCluster() {
                const fileInput = document.getElementById('csvFile');
                const groupSize = document.getElementById('groupSize').value;
                const method = document.getElementById('method').value;
                
                if (!fileInput.files[0]) {
                    showResult({error: "Please select a CSV file"}, true);
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('group_size', groupSize);
                formData.append('method', method);
                formData.append('n_clusters', '4');

                try {
                    const response = await fetch('/upload-csv', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showResult(result);
                    } else {
                        showResult(result, true);
                    }
                } catch (error) {
                    showResult({error: error.message}, true);
                }
            }

            document.getElementById('quizForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = {
                    student_name: document.getElementById('studentName').value,
                    gender: document.getElementById('gender').value,
                    age: parseInt(document.getElementById('age').value),
                    nationality: document.getElementById('nationality').value,
                    communication_answers: document.getElementById('commAnswers').value.split(',').map(x => parseInt(x.trim())),
                    leadership_answers: document.getElementById('leadAnswers').value.split(',').map(x => parseInt(x.trim())),
                    time_management_answers: document.getElementById('timeAnswers').value.split(',').map(x => parseInt(x.trim())),
                    analytical_answers: document.getElementById('analyAnswers').value.split(',').map(x => parseInt(x.trim()))
                };

                try {
                    const response = await fetch('/api/v1/quiz/submit', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showResult(result);
                        updateStudentCount();
                    } else {
                        showResult(result, true);
                    }
                } catch (error) {
                    showResult({error: error.message}, true);
                }
            });

            async function performClustering() {
                try {
                    const studentsResponse = await fetch('/api/v1/students');
                    const students = await studentsResponse.json();
                    
                    if (students.length === 0) {
                        showResult({error: "No students in database. Please add students first."}, true);
                        return;
                    }

                    const clusteringData = {
                        students: students.map(s => ({
                            student_id: s.student_id,
                            student_name: s.student_name,
                            gender: s.gender,
                            age: s.age,
                            nationality: s.nationality,
                            communication_score: s.communication_score,
                            leadership_score: s.leadership_score,
                            time_management_score: s.time_management_score,
                            analytical_score: s.analytical_score
                        })),
                        target_group_size: parseInt(document.getElementById('clusterGroupSize').value),
                        force_heterogeneous: true
                    };

                    const response = await fetch('/api/v1/clustering/perform', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(clusteringData)
                    });
                    
                    const result = await response.json();
                    if (response.ok) {
                        showResult(result);
                    } else {
                        showResult(result, true);
                    }
                } catch (error) {
                    showResult({error: error.message}, true);
                }
            }

            async function getStudents() {
                try {
                    const response = await fetch('/api/v1/students');
                    const result = await response.json();
                    showResult(result);
                    updateStudentCount();
                } catch (error) {
                    showResult({error: error.message}, true);
                }
            }

            async function getClusteringHistory() {
                try {
                    const response = await fetch('/api/v1/clustering/history');
                    const result = await response.json();
                    showResult(result);
                } catch (error) {
                    showResult({error: error.message}, true);
                }
            }

            async function clearAllData() {
                if (confirm('Are you sure you want to clear all student data?')) {
                    try {
                        const response = await fetch('/api/v1/students/clear', {method: 'DELETE'});
                        const result = await response.json();
                        showResult(result);
                        updateStudentCount();
                    } catch (error) {
                        showResult({error: error.message}, true);
                    }
                }
            }

            async function healthCheck() {
                try {
                    const response = await fetch('/api/v1/health');
                    const result = await response.json();
                    showResult(result);
                } catch (error) {
                    showResult({error: error.message}, true);
                }
            }

            async function updateStudentCount() {
                try {
                    const response = await fetch('/api/v1/students');
                    const students = await response.json();
                    document.getElementById('studentCount').textContent = students.length;
                } catch (error) {
                    console.error('Error updating student count:', error);
                }
            }

            function downloadSampleCSV() {
                const csvContent = `student_id,student_name,gender,age,nationality,communication_score,leadership_score,time_management_score,analytical_score
STU001,John Smith,Male,22,American,4.2,3.8,4.5,4.1
STU002,Maria Garcia,Female,21,Spanish,4.8,4.2,3.9,3.7
STU003,Ahmed Hassan,Male,23,Egyptian,3.5,4.6,4.2,4.3
STU004,Lisa Chen,Female,20,Chinese,4.1,3.9,4.7,4.8
STU005,David Johnson,Male,24,British,3.8,4.4,3.6,4.0`;
                
                const blob = new Blob([csvContent], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'sample_student_data.csv';
                a.click();
                window.URL.revokeObjectURL(url);
            }

            // Initialize
            updateStudentCount();
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/v1/quiz/submit", response_model=Dict[str, Any], tags=["Quiz"])
async def submit_quiz(quiz_data: QuizSubmission):
    """Submit quiz answers and get calculated skill scores"""
    try:
        # Calculate scores from answers
        communication_score = calculate_quiz_scores(quiz_data.communication_answers)
        leadership_score = calculate_quiz_scores(quiz_data.leadership_answers)
        time_management_score = calculate_quiz_scores(quiz_data.time_management_answers)
        analytical_score = calculate_quiz_scores(quiz_data.analytical_answers)
        
        # Create student data
        student_id = f"STU_{uuid.uuid4().hex[:8].upper()}"
        overall_score = round((communication_score + leadership_score + time_management_score + analytical_score) / 4, 2)
        
        student_data = {
            "student_id": student_id,
            "student_name": quiz_data.student_name,
            "gender": quiz_data.gender,
            "age": quiz_data.age,
            "nationality": quiz_data.nationality,
            "communication_score": communication_score,
            "leadership_score": leadership_score,
            "time_management_score": time_management_score,
            "analytical_score": analytical_score,
            "overall_score": overall_score,
            "quiz_timestamp": datetime.now().isoformat()
        }
        
        # Add to database
        student_database.append(student_data)
        
        return {
            "success": True,
            "student_id": student_id,
            "skill_scores": {
                "communication": communication_score,
                "leadership": leadership_score,
                "time_management": time_management_score,
                "analytical": analytical_score,
                "overall": overall_score
            },
            "message": "Quiz submitted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing quiz: {str(e)}")

@app.post("/api/v1/clustering/perform", response_model=ClusteringResponse, tags=["Clustering"])
async def perform_clustering(request: ClusteringRequest, background_tasks: BackgroundTasks):
    """Perform heterogeneous clustering on student data"""
    try:
        if len(request.students) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 students for clustering")
        
        # Convert to DataFrame
        students_data = []
        for student in request.students:
            students_data.append({
                'student_id': student.student_id,
                'student_name': student.student_name,
                'gender': student.gender,
                'age': student.age,
                'nationality': student.nationality,
                'communication_score': student.communication_score,
                'leadership_score': student.leadership_score,
                'time_management_score': student.time_management_score,
                'analytical_score': student.analytical_score
            })
        
        students_df = pd.DataFrame(students_data)
        students_df['overall_score'] = students_df[['communication_score', 'leadership_score', 
                                                  'time_management_score', 'analytical_score']].mean(axis=1)
        
        # Perform heterogeneous clustering
        groups = create_heterogeneous_groups(students_df, request.target_group_size)
        
        # Analyze each group
        clusters = []
        student_assignments = []
        total_complementarity_score = 0
        
        for group_idx, group_students in enumerate(groups):
            if len(group_students) == 0:
                continue
            
            # Analyze group complementarity
            analysis = analyze_group_complementarity(group_students, students_df)
            
            # Generate cluster info
            description = generate_cluster_description(
                analysis['complementary_skills'], 
                analysis['similar_skills'], 
                analysis['demographic_diversity']
            )
            
            cluster_name = generate_cluster_name(
                analysis['complementary_skills'], 
                analysis['demographic_diversity']
            )
            
            # Calculate complementarity score
            complementarity_score = len(analysis['complementary_skills']) / 4.0  # Normalize to 0-1
            total_complementarity_score += complementarity_score
            
            cluster_info = ClusterInfo(
                cluster_id=group_idx,
                cluster_name=cluster_name,
                description=description,
                complementary_skills=analysis['complementary_skills'],
                similar_skills=analysis['similar_skills'],
                demographic_diversity=analysis['demographic_diversity'],
                student_count=len(group_students)
            )
            clusters.append(cluster_info)
            
            # Create student assignments
            for student_idx in group_students:
                student = students_df.iloc[student_idx]
                
                # Determine strengths and areas for development
                strengths = []
                areas_for_development = []
                
                if student['communication_score'] > 4.0:
                    strengths.append("Strong Communication")
                elif student['communication_score'] < 2.5:
                    areas_for_development.append("Communication Skills")
                
                if student['leadership_score'] > 4.0:
                    strengths.append("Natural Leadership")
                elif student['leadership_score'] < 2.5:
                    areas_for_development.append("Leadership Skills")
                
                if student['time_management_score'] > 4.0:
                    strengths.append("Excellent Organization")
                elif student['time_management_score'] < 2.5:
                    areas_for_development.append("Time Management")
                
                if student['analytical_score'] > 4.0:
                    strengths.append("Strong Analytical Thinking")
                elif student['analytical_score'] < 2.5:
                    areas_for_development.append("Analytical Skills")
                
                assignment = StudentClusterAssignment(
                    student_id=student['student_id'],
                    student_name=student['student_name'],
                    cluster_id=group_idx,
                    cluster_name=cluster_name,
                    skill_profile={
                        "communication": student['communication_score'],
                        "leadership": student['leadership_score'],
                        "time_management": student['time_management_score'],
                        "analytical": student['analytical_score'],
                        "overall": student['overall_score']
                    },
                    strengths=strengths,
                    areas_for_development=areas_for_development
                )
                student_assignments.append(assignment)
        
        # Calculate average complementarity score
        avg_complementarity = total_complementarity_score / len(clusters) if clusters else 0
        
        # Create response
        response = ClusteringResponse(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            total_students=len(students_df),
            total_groups=len(clusters),
            average_complementarity_score=round(avg_complementarity, 3),
            clusters=clusters,
            student_assignments=student_assignments,
            visualization_data={
                "total_students": len(students_df),
                "total_groups": len(clusters),
                "complementarity_score": round(avg_complementarity, 3)
            }
        )
        
        # Store in history
        clustering_history.append({
            "request_id": response.request_id,
            "timestamp": response.timestamp,
            "total_students": response.total_students,
            "total_groups": response.total_groups,
            "average_complementarity_score": response.average_complementarity_score
        })
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing clustering: {str(e)}")

@app.post("/upload-csv")
async def upload_csv_form_groups(
    file: UploadFile = File(...),
    group_size: int = Form(4),
    method: str = Form("complementary"),
    n_clusters: int = Form(4)
):
    """Upload a CSV file with student data and form heterogeneous groups"""
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Check for different column formats
        quiz_columns = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
        skill_columns = ['hard_skills', 'soft_skills', 'teamwork', 'creativity']
        
        if all(col in df.columns for col in quiz_columns):
            # Use quiz-based clustering approach
            return await process_quiz_based_csv(df, group_size)
        elif all(col in df.columns for col in skill_columns):
            # Use skills-based clustering approach
            return await process_skills_based_csv(df, group_size, method, n_clusters)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain either quiz columns {quiz_columns} or skill columns {skill_columns}"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

async def process_quiz_based_csv(df: pd.DataFrame, group_size: int):
    """Process CSV with quiz-based columns"""
    # Convert DataFrame to StudentData objects
    students = []
    for _, row in df.iterrows():
        student = StudentData(
            student_id=row.get('student_id', f"STU_{uuid.uuid4().hex[:8].upper()}"),
            student_name=row.get('student_name', 'Unknown'),
            gender=row.get('gender', 'Unknown'),
            age=int(row.get('age', 20)),
            nationality=row.get('nationality', 'Unknown'),
            communication_score=float(row['communication_score']),
            leadership_score=float(row['leadership_score']),
            time_management_score=float(row['time_management_score']),
            analytical_score=float(row['analytical_score'])
        )
        students.append(student)
    
    # Perform clustering
    request = ClusteringRequest(students=students, target_group_size=group_size)
    return await perform_clustering(request, BackgroundTasks())

async def process_skills_based_csv(df: pd.DataFrame, group_size: int, method: str, n_clusters: int):
    """Process CSV with skills-based columns"""
    skill_columns = ['hard_skills', 'soft_skills', 'teamwork', 'creativity']
    
    # Check that we have sufficient data
    if len(df) < group_size:
        raise HTTPException(status_code=400, detail=f"Not enough students in CSV. Minimum required: {group_size}")
    
    # Preprocess data
    processed_df = preprocess_student_data(df, skill_columns)
    
    # Cluster students
    clustered_df, _, _, _ = cluster_student_skills(processed_df, skill_columns, n_clusters)
    
    # Form groups
    groups = form_heterogeneous_groups_v2(
        clustered_df, 
        skill_columns, 
        group_size=group_size,
        method=method
    )
    
    # Generate group summary
    summary = generate_group_summary(groups, skill_columns)
    
    return {
        "groups": groups,
        "summary": summary
    }

@app.get("/api/v1/students", response_model=List[Dict[str, Any]], tags=["Data Management"])
async def get_all_students():
    """Get all students in the database"""
    return student_database

@app.delete("/api/v1/students/clear", response_model=Dict[str, Any], tags=["Data Management"])
async def clear_all_students():
    """Clear all student data from the database"""
    global student_database, clustering_history
    student_database.clear()
    clustering_history.clear()
    return {"success": True, "message": "All student data cleared successfully"}

@app.get("/api/v1/clustering/history", response_model=List[Dict[str, Any]], tags=["Analytics"])
async def get_clustering_history():
    """Get history of clustering operations"""
    return clustering_history

@app.get("/api/v1/health", response_model=Dict[str, Any], tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_students": len(student_database),
        "total_clustering_operations": len(clustering_history)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)