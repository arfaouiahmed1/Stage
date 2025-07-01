# Datasets

## Overview
Clean, production-ready datasets for the Gamified Student Clustering Platform. Designed by data scientists for data scientists - optimized for pandas, scikit-learn, and ML pipelines.

## Structure
```
Datasets/
└── Quiz Generation/          # Complete assessment and clustering dataset
    ├── taxonomy.csv          # 4 dimensions × 21 subcategories (21 rows)
    ├── questions.csv         # 160 realistic university scenarios (160 rows)  
    ├── rubrics.csv           # Year-appropriate scoring standards (6 rows)
    ├── features_template.csv # ML feature columns (32 features)
    ├── scoring_guide.md      # Mathematical methodology
    ├── validate_data.py      # Data integrity validation script
    └── README.md            # Detailed data science documentation
```

## Key Features
- **4 Assessment Dimensions**: Creativity, Teamwork, Soft Skills, Hard Skills
- **21 Subcategories**: Tailored for software engineering curriculum
- **160 Realistic Questions**: Based on actual university projects (SDL games, web apps, presentations)
- **Year-Level Scaling**: Appropriate expectations for Years 1-5
- **Collaboration Focus**: Designed to predict team compatibility and reduce conflicts
- **Clean Data Structure**: Optimized for pandas, scikit-learn, and data science workflows

## Quick Start (Data Scientists)
```python
import pandas as pd
import numpy as np

# Load core datasets
taxonomy = pd.read_csv('Quiz Generation/taxonomy.csv')
questions = pd.read_csv('Quiz Generation/questions.csv') 
rubrics = pd.read_csv('Quiz Generation/rubrics.csv')
features = pd.read_csv('Quiz Generation/features_template.csv')

# Verify data integrity
assert len(taxonomy) == 21  # 21 subcategories 
assert len(questions) == 160  # 160 questions
assert len(rubrics) == 6  # 6 scoring levels
assert taxonomy.groupby('dimension_id')['dimension_weight'].first().sum() == 1.0

# Quick analysis
print(f"Dimensions: {taxonomy['dimension_name'].unique()}")
print(f"Questions per dimension: {questions['dimension'].value_counts()}")
print(f"Year levels covered: {sorted(questions['target_year_level'].unique())}")
```

## Use Cases
- **LLM Quiz Generation**: Train language models to create assessment questions
- **Student Clustering**: Form optimal teams based on complementary skills  
- **Academic Research**: Analyze collaboration patterns in software engineering education
- **Learning Analytics**: Track student development across multiple dimensions