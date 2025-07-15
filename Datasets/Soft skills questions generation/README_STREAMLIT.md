# Student Heterogeneous Group Formation - Streamlit App

This Streamlit application implements the functionality from the Student Heterogeneous Group Formation notebook. It allows you to form balanced student teams based on complementary skill profiles.

## Features

- Upload student data or use generated sample data
- Analyze student skill distributions and correlations
- Create heterogeneous student groups using three different methods:
  - **Complementary**: Pairs students with complementary strengths and weaknesses
  - **Balanced**: Ensures each group has a similar average skill level
  - **Mixed**: Combines cluster-based and skill-based assignment
- Visualize group skill profiles with radar charts
- Get project and role recommendations based on group compositions

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

To run the Streamlit app, execute:

```bash
streamlit run streamlit_group_formation.py
```

This will start a local server and open the application in your default web browser.

## Usage

1. Upload student data in CSV format or use the sample data option
2. Navigate through the pages in order:
   - Data Analysis
   - Group Formation
   - Group Analysis
   - Project Recommendations
3. Export group assignments and recommendations as needed

## Data Format

The application expects data with the following structure:
- A column for student IDs or names
- Multiple columns for different skill scores (on a scale, e.g., 1-5)
- Sample columns: `student_id`, `soft_skills`, `hard_skills`, `creativity`, `teamwork`

## Created by

Based on the Student Heterogeneous Group Formation Jupyter notebook.
