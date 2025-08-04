# Soft Skills Assessment Quiz Setup Guide

This guide will help you set up and run the Soft Skills Assessment Quiz application.

## Prerequisites

- Python 3.7 or higher
- FastAPI
- Uvicorn
- A modern web browser

## Step 1: Install Required Python Packages

```bash
pip install fastapi uvicorn pandas
```

## Step 2: Start the FastAPI Server

1. Open a terminal/command prompt
2. Navigate to the project directory:
   ```bash
   cd "c:\Users\MSI\OneDrive - ESPRIT\Bureau\4DS ESPRIT\StageESPRIT\Stage\Datasets\Soft skills questions generation"
   ```
3. Run the following command:
   ```bash
   python -m uvicorn soft_skills_api:app --reload
   ```
4. The server should start and display a message like:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   ```

## Step 3: Open the Quiz Client

1. Simply open the `quiz_client.html` file in your web browser
2. You can do this by:
   - Right-clicking on the file and selecting "Open with" and choosing your browser
   - Or drag and drop the file into an open browser window

## Step 4: Use the Quiz

1. Enter your name and student ID
2. Select a skill category (or leave it as "All Categories" for a mix)
3. Choose the number of questions you want to answer
4. Click "Start Quiz"
5. Answer all the questions by selecting a response from 1 (Strongly Disagree) to 5 (Strongly Agree)
6. Click "Submit Answers" when you're done
7. View your results and the radar chart showing your skills profile

## Troubleshooting

If you encounter any issues:

1. Make sure the FastAPI server is running (check the terminal)
2. Check that the API URL in `quiz_client.html` is set to `http://localhost:8000` or the correct URL where your server is running
3. Open your browser's developer tools (F12 or right-click and select "Inspect") to check for any JavaScript errors in the console
4. If you see 404 errors, make sure the endpoints in the client match the API endpoints:
   - The API uses `/categories`, `/quiz`, and `/submit` (without trailing slashes)
   - The client should use these exact paths

## API Endpoints

- `GET /`: API root - returns a welcome message
- `GET /categories`: Returns available skill categories
- `POST /quiz`: Generates a quiz with questions
- `POST /submit`: Submits assessment answers and returns results
- `GET /results/{student_id}`: Retrieves previous results for a student

## For Developers

If you want to modify the client or API:

1. The API code is in `soft_skills_api.py`
2. The client code is in `quiz_client.html`
3. The API uses CORS middleware, so it should work with the client even when opened as a local file
