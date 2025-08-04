# Soft Skills Assessment API

This API provides endpoints for creating and evaluating soft skills assessment quizzes.

## Requirements

- Python 3.7+
- FastAPI
- Pandas
- Uvicorn

## Installation

1. Install dependencies:

```bash
pip install fastapi pandas uvicorn
```

2. Run the API:

```bash
uvicorn soft_skills_api:app --reload
```

3. Open the API documentation at: http://localhost:8000/docs

4. To use the frontend, simply open the `index.html` file in a browser while the API is running.

## API Endpoints

- `GET /`: Welcome message
- `GET /questions`: Get all available questions
- `POST /quiz`: Create a quiz with questions from specific categories
- `POST /submit`: Submit quiz answers and get results
- `GET /categories`: Get all skill categories
- `GET /results/{student_id}`: Get results for a specific student

## Frontend Usage

The `index.html` file provides a user-friendly interface for the assessment. It allows:

1. Entering student information
2. Selecting a specific skill category or a mix of categories
3. Choosing the number of questions
4. Answering questions on a 1-5 scale
5. Viewing results with:
   - Overall score
   - Detailed feedback
   - Radar chart visualization of skills

## Data Storage

Assessment results are stored in the `data/assessment_results.csv` file.
