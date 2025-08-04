# Student Quiz Clustering App

This Streamlit application integrates the soft skills assessment quiz with student clustering to provide personalized feedback and recommendations.

## Features

- **Soft Skills Assessment Quiz**: Students answer questions across four key soft skill areas:
  - Communication
  - Leadership
  - Time Management
  - Analytical Thinking

- **Clustering Analysis**: After completing the quiz, the app:
  - Calculates scores for each skill area
  - Performs clustering to group students with similar skill profiles
  - Places the current student in the appropriate cluster
  - Visualizes the results using PCA projection

- **Personalized Recommendations**: Based on the student's cluster and relative scores, the app provides:
  - Skill profile visualization (radar chart)
  - Cluster description and characteristics
  - Specific recommendations for improvement

## How to Use

1. Run the application:
```
streamlit run student_quiz_clustering_app.py
```

2. Complete the quiz by answering all questions in each category

3. View your results and personalized recommendations

4. (Optional) Retake the assessment if desired

## Technical Details

- Uses **KMeans clustering** with silhouette score optimization for the number of clusters
- Implements **PCA** for dimensionality reduction and visualization
- Creates synthetic student data for comparison and clustering
- Provides skill-specific recommendations based on normalized scores

## Requirements

The application requires:
- streamlit
- pandas
- numpy
- matplotlib
- scikit-learn
- seaborn

You can install all requirements with:
```
pip install -r requirements.txt
```
