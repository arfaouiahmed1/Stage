# Quiz Generation Dataset

## Overview
Clean, production-ready dataset for ML-driven student assessment and team formation. Organized following data science best practices with clear separation between raw and processed data.

## Folder Structure
```
Quiz Generation/
├── README.md                    # This file
├── raw/                        # Original, immutable source data
│   ├── taxonomy.csv            # Assessment framework (4 dimensions × 21 subcategories)
│   ├── questions.csv           # Question bank (160 realistic scenarios)
│   └── rubrics.csv             # Scoring standards (0-5 scale with year expectations)
├── processed/                  # Derived and ML-ready data
│   ├── features_template.csv   # ML pipeline template (32 features)
│   ├── clustering_features.csv # Feature engineering outputs
│   ├── collaboration_indicators.csv # Team formation metrics
│   └── year_level_expectations.csv # Academic year benchmarks
├── scripts/                    # Data processing and validation
│   └── validate_data.py        # Data integrity checks
└── documentation/              # Detailed methodology
    ├── scoring_guide.md        # Mathematical scoring methodology
    └── scoring_calculation_guide.md # Implementation details
```

## Quick Start (Data Scientists)
```python
import pandas as pd
import numpy as np

# Load core datasets
taxonomy = pd.read_csv('raw/taxonomy.csv')
questions = pd.read_csv('raw/questions.csv') 
rubrics = pd.read_csv('raw/rubrics.csv')

# Load processed features
features_template = pd.read_csv('processed/features_template.csv')
collaboration_data = pd.read_csv('processed/collaboration_indicators.csv')

# Basic validation
assert len(taxonomy) == 21, "Expected 21 subcategories"
assert len(questions) == 160, "Expected 160 questions"
assert len(rubrics) == 6, "Expected 6 scoring levels (0-5)"

print("✅ Dataset loaded successfully")
print(f"Dimensions: {taxonomy['dimension_name'].unique()}")
print(f"Questions per dimension: {questions['dimension'].value_counts()}")
```

## Data Schema

### Raw Data (`raw/`)

#### `taxonomy.csv` - Assessment Framework
Defines the 4-dimensional assessment structure:
- **Creativity** (25%): Innovation, algorithm design, UX
- **Teamwork** (25%): Communication, collaboration, leadership  
- **Soft Skills** (25%): Time management, presentation, ethics
- **Hard Skills** (25%): Programming, debugging, testing

#### `questions.csv` - Question Bank
160 realistic university scenarios covering:
- Target year levels: 1-5
- Question types: Individual tasks, collaboration scenarios
- Time limits: 5-15 minutes
- Assessment criteria mapped to taxonomy

#### `rubrics.csv` - Scoring Standards
0-5 scale scoring with year-appropriate expectations:
- 0: No Evidence
- 1: Basic Attempt  
- 2: Developing
- 3: Proficient
- 4: Advanced
- 5: Exceptional

### Processed Data (`processed/`)

#### `features_template.csv` - ML Pipeline Template
32-column structure for clustering algorithms including:
- Individual dimension scores
- Composite metrics
- Collaboration indicators
- Conflict resolution scores

#### `collaboration_indicators.csv` - Team Formation Metrics
Derived metrics for optimal team formation based on complementary skills.

#### `year_level_expectations.csv` - Academic Benchmarks
Year-specific performance expectations for calibrating assessment difficulty.

## Use Cases
- **Student Clustering**: Form balanced teams based on complementary skills
- **LLM Training**: Generate contextually appropriate assessment questions
- **Learning Analytics**: Track student development across multiple dimensions
- **Academic Research**: Analyze collaboration patterns in CS education

## Data Quality
- ✅ Zero missing values
- ✅ Balanced question distribution across dimensions
- ✅ Mathematically consistent weights (dimensions sum to 1.0)
- ✅ Validated taxonomy mapping
- ✅ Realistic university scenarios

## Validation
Run data integrity checks:
```bash
cd scripts/
python validate_data.py
```

## Documentation
Detailed methodology available in `documentation/`:
- Mathematical scoring formulas
- Assessment design principles
- Implementation guidelines
