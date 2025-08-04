# Student Heterogeneous Clustering API

A comprehensive FastAPI application for clustering students with complementary skills to create optimal peer learning groups.

## Features

- **Multiple Clustering Approaches**: Supports both quiz-based and skills-based clustering
- **File Upload Support**: Upload CSV datasets directly through the web interface
- **Interactive Web Interface**: Built-in testing interface with multiple tabs
- **Comprehensive API**: RESTful endpoints for all clustering operations
- **Real-time Analytics**: Track clustering history and performance metrics
- **Flexible Group Formation**: Configurable group sizes and clustering methods

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the application**:
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## Dataset Formats

The API supports two different dataset formats:

### Format 1: Quiz-based (Recommended)
```csv
student_id,student_name,gender,age,nationality,communication_score,leadership_score,time_management_score,analytical_score
STU001,John Smith,Male,22,American,4.2,3.8,4.5,4.1
```

**Columns:**
- `student_id`: Unique identifier for each student
- `student_name`: Full name of the student
- `gender`: Student's gender (Male/Female/Other)
- `age`: Student's age (18-45)
- `nationality`: Student's nationality
- `communication_score`: Communication skill score (1.0-5.0)
- `leadership_score`: Leadership skill score (1.0-5.0)
- `time_management_score`: Time management skill score (1.0-5.0)
- `analytical_score`: Analytical skill score (1.0-5.0)

### Format 2: Skills-based (Alternative)
```csv
student_id,first_name,last_name,gender,age,nationality,hard_skills,soft_skills,teamwork,creativity
STU001,John,Smith,Male,22,American,4.2,3.8,4.5,4.1
```

**Columns:**
- `student_id`: Unique identifier for each student
- `first_name`, `last_name`: Student's name components
- `gender`: Student's gender
- `age`: Student's age
- `nationality`: Student's nationality
- `hard_skills`: Technical/hard skills score (1.0-5.0)
- `soft_skills`: Soft skills score (1.0-5.0)
- `teamwork`: Teamwork ability score (1.0-5.0)
- `creativity`: Creativity score (1.0-5.0)

## Using the Web Interface

### 1. Upload Dataset Tab
- Upload your CSV file using the file picker
- Configure group size (2-8 students per group)
- Select clustering method:
  - **Complementary Skills**: Groups students with different strengths
  - **Balanced Groups**: Distributes high/medium/low performers evenly
  - **Mixed Approach**: Combines clustering with complementary pairing
- Click "Upload & Create Groups" to process
- Download sample CSV files for reference

### 2. Quiz Submission Tab
- Submit individual student quiz responses
- Enter demographic information
- Provide 5 answers (1-5 scale) for each skill area:
  - Communication Skills
  - Leadership Skills
  - Time Management Skills
  - Analytical Skills
- Students are automatically added to the database

### 3. Clustering Tab
- Perform clustering on students stored in the database
- Configure target group size
- View current student count
- Create groups from existing data

### 4. Data Management Tab
- View all students in the database
- Check clustering history
- Clear all data
- Perform health checks

## API Endpoints

### Core Endpoints

#### Upload CSV and Create Groups
```http
POST /upload-csv
Content-Type: multipart/form-data

Parameters:
- file: CSV file
- group_size: Target group size (default: 4)
- method: Clustering method (default: "complementary")
- n_clusters: Number of initial clusters (default: 4)
```

#### Submit Quiz
```http
POST /api/v1/quiz/submit
Content-Type: application/json

{
  "student_name": "John Doe",
  "gender": "Male",
  "age": 22,
  "nationality": "American",
  "communication_answers": [4, 3, 5, 4, 3],
  "leadership_answers": [3, 4, 2, 5, 4],
  "time_management_answers": [5, 4, 4, 3, 5],
  "analytical_answers": [4, 5, 3, 4, 4]
}
```

#### Perform Clustering
```http
POST /api/v1/clustering/perform
Content-Type: application/json

{
  "students": [...],
  "target_group_size": 4,
  "force_heterogeneous": true
}
```

### Data Management Endpoints

- `GET /api/v1/students` - Get all students
- `DELETE /api/v1/students/clear` - Clear all student data
- `GET /api/v1/clustering/history` - Get clustering history
- `GET /api/v1/health` - Health check

## Response Format

### Clustering Response
```json
{
  "request_id": "uuid",
  "timestamp": "2024-01-15T10:30:00",
  "total_students": 20,
  "total_groups": 5,
  "average_complementarity_score": 0.75,
  "clusters": [
    {
      "cluster_id": 0,
      "cluster_name": "Diverse Complementary Communication, Leadership Group",
      "description": "This learning group has diverse skill levels in Communication, Leadership...",
      "complementary_skills": ["Communication", "Leadership"],
      "similar_skills": ["Time Management"],
      "demographic_diversity": {
        "gender_diversity": 2,
        "nationality_diversity": 3,
        "age_range": 4
      },
      "student_count": 4
    }
  ],
  "student_assignments": [
    {
      "student_id": "STU001",
      "student_name": "John Smith",
      "cluster_id": 0,
      "cluster_name": "Diverse Complementary Communication, Leadership Group",
      "skill_profile": {
        "communication": 4.2,
        "leadership": 3.8,
        "time_management": 4.5,
        "analytical": 4.1,
        "overall": 4.15
      },
      "strengths": ["Strong Communication", "Excellent Organization"],
      "areas_for_development": []
    }
  ]
}
```

## Sample Data

The project includes sample datasets in the `sample_datasets/` directory:
- `quiz_based_sample.csv`: 20 students with quiz-based format
- `skills_based_sample.csv`: 20 students with skills-based format

## Testing Your Dataset

1. **Prepare your CSV file** with the correct column format
2. **Open the web interface** at http://localhost:8000
3. **Go to the "Upload Dataset" tab**
4. **Upload your CSV file** and configure settings
5. **Click "Upload & Create Groups"** to see results
6. **Review the clustering results** in the Results section

## Clustering Algorithms

### Quiz-based Clustering
- Calculates skill percentiles for each student
- Creates diversity scores based on extreme performances
- Distributes students to ensure heterogeneous groups
- Analyzes complementarity within each group

### Skills-based Clustering
- Uses K-means clustering for initial grouping
- Applies complementary skill pairing
- Balances groups based on overall skill levels
- Provides project and role recommendations

## Configuration Options

- **Group Size**: 2-8 students per group
- **Clustering Methods**: 
  - Complementary (recommended for peer learning)
  - Balanced (even skill distribution)
  - Mixed (hybrid approach)
- **Force Heterogeneous**: Ensures diverse skill combinations

## Troubleshooting

### Common Issues

1. **CSV Format Errors**:
   - Ensure column names match exactly
   - Check for missing values
   - Verify score ranges (1.0-5.0)

2. **Insufficient Data**:
   - Need minimum 2 students for clustering
   - Recommended: 8+ students for meaningful groups

3. **Server Errors**:
   - Check console logs for detailed error messages
   - Verify all dependencies are installed
   - Ensure Python version compatibility (3.8+)

### Getting Help

- Check the API documentation at `/docs`
- Review sample datasets for format reference
- Use the health check endpoint to verify server status

## License

This project is open source and available under the MIT License.