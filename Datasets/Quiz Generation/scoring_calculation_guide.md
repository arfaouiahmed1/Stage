# Quiz Scoring and Calculation System

## Overview
This document explains how quiz responses are scored and final team formation scores are calculated for the Gamified Student Clustering Platform.

## Complete Scoring Workflow

### Phase 1: Individual Question Scoring
```
Student Response → Rubric Evaluation → Raw Score (0-5) → Question Score
```

**Process:**
1. **Response Collection**: Student answers quiz question
2. **Rubric Application**: Answer evaluated against `scoring_rubrics.csv` criteria
3. **Score Assignment**: 0-5 score assigned based on rubric match
4. **Collaboration Score**: Additional collaboration indicator score (very_high=5, high=4, medium=3, low=2, very_low=1)

### Phase 2: Subcategory Score Aggregation
```
Multiple Question Scores → Weighted Average → Subcategory Score (0-5)
```

**Calculation Example:**
```
Innovation & Problem-solving Questions:
- Question cip_001: Score = 4
- Question cip_002: Score = 3  
- Question cip_003: Score = 5

Subcategory Score = (4 + 3 + 5) / 3 = 4.0
```

### Phase 3: Dimension Score Calculation
```
Subcategory Scores × Weights → Dimension Score (0-5)
```

**Example for Creativity Dimension:**
```
From dimensions_taxonomy.csv:
- Innovation & Problem-solving: 4.0 × 0.30 = 1.20
- Algorithm Design: 3.5 × 0.25 = 0.875
- System Architecture: 4.2 × 0.25 = 1.05
- Code Optimization: 3.0 × 0.10 = 0.30
- UX Design: 4.5 × 0.10 = 0.45

Creativity Score = 1.20 + 0.875 + 1.05 + 0.30 + 0.45 = 3.875
```

### Phase 4: Overall Composite Score
```
Dimension Scores × Dimension Weights → Total Score (0-5)
```

**Final Calculation:**
```
From dimensions_taxonomy.csv (all dimensions weighted 0.25):
- Creativity: 3.875 × 0.25 = 0.969
- Teamwork: 4.2 × 0.25 = 1.05
- Soft Skills: 3.6 × 0.25 = 0.90
- Hard Skills: 4.0 × 0.25 = 1.00

Total Composite Score = 0.969 + 1.05 + 0.90 + 1.00 = 3.919
```

### Phase 5: Collaboration Metrics Calculation
```
Collaboration-Specific Questions → Special Collaboration Scores
```

**Additional Scores for Team Formation:**
- **Collaboration Capability**: Average of all collaboration_indicator scores
- **Mentoring Potential**: Average of mentoring-specific question scores  
- **Conflict Resolution**: Average of conflict resolution question scores
- **Help Seeking Comfort**: Calculated from questions about asking for help
- **Help Giving Willingness**: Calculated from questions about helping others

## Detailed Scoring Examples

### Example 1: Question Response Scoring

**Question:** "Your teammate's HTML/CSS code works but doesn't follow best practices. How do you provide feedback?"

**Student Response:** "I would sit down with them and explain why certain practices are better, showing examples and helping them understand the benefits rather than just telling them what's wrong."

**Scoring Process:**
1. **Check against rubrics** (`scoring_rubrics.csv`):
   - Dimension: teamwork
   - Subcategory: code_review_collaboration
   - Score level assessment: Shows constructive approach, educational focus, supportive attitude
   
2. **Score Assignment**: 4/5 (Good - exceeds expectations)
   - Demonstrates constructive feedback ✓
   - Shows teaching approach ✓  
   - Maintains positive relationship ✓
   - Could be more specific about techniques

3. **Collaboration Indicator**: very_high → 5 points

### Example 2: Complete Student Profile Calculation

**Student Data:**
```csv
student_id,year_level,creativity_innovation_problem_solving,creativity_algorithm_design,creativity_system_architecture,creativity_code_optimization,creativity_ux_design,teamwork_communication_documentation,teamwork_code_review_collaboration,teamwork_leadership_mentoring,teamwork_conflict_resolution,teamwork_agile_participation,soft_skills_time_management,soft_skills_adaptability_learning,soft_skills_critical_thinking,soft_skills_presentation_communication,soft_skills_project_management,hard_skills_programming_languages,hard_skills_software_engineering_principles,hard_skills_database_management,hard_skills_devops_deployment,hard_skills_testing_qa,hard_skills_mathematics_algorithms
STUD001,2,4.2,3.8,4.0,3.5,4.5,4.5,4.8,3.9,4.1,3.6,4.0,4.3,3.8,4.2,3.5,3.8,4.0,3.2,2.8,3.5,3.9
```

**Calculations:**

1. **Creativity Dimension:**
   - (4.2×0.30) + (3.8×0.25) + (4.0×0.25) + (3.5×0.10) + (4.5×0.10) = 4.01

2. **Teamwork Dimension:**
   - (4.5×0.30) + (4.8×0.25) + (3.9×0.20) + (4.1×0.15) + (3.6×0.10) = 4.34

3. **Soft Skills Dimension:**
   - (4.0×0.25) + (4.3×0.25) + (3.8×0.25) + (4.2×0.15) + (3.5×0.10) = 4.01

4. **Hard Skills Dimension:**
   - (3.8×0.30) + (4.0×0.25) + (3.2×0.15) + (2.8×0.15) + (3.5×0.10) + (3.9×0.05) = 3.63

5. **Total Composite Score:**
   - (4.01×0.25) + (4.34×0.25) + (4.01×0.25) + (3.63×0.25) = 4.00

6. **Collaboration Metrics:**
   - High collaboration capability (4.4/5)
   - Strong mentoring potential (4.1/5) 
   - Good conflict resolution (4.1/5)
   - Year 2 expectations: Exceeds expected level

## Team Formation Algorithm Input

### Final Feature Vector for ML Clustering:
```
Student Profile = [
    year_level: 2,
    creativity_scores: [4.2, 3.8, 4.0, 3.5, 4.5],
    teamwork_scores: [4.5, 4.8, 3.9, 4.1, 3.6],
    soft_skills_scores: [4.0, 4.3, 3.8, 4.2, 3.5],
    hard_skills_scores: [3.8, 4.0, 3.2, 2.8, 3.5, 3.9],
    dimension_totals: [4.01, 4.34, 4.01, 3.63],
    composite_score: 4.00,
    collaboration_capability: 4.4,
    mentoring_potential: 4.1,
    conflict_resolution: 4.1,
    help_seeking: 3.8,
    help_giving: 4.3
]
```

## Quality Assurance & Validation

### Score Validation Checks:
1. **Range Validation**: All scores must be 0-5
2. **Weight Validation**: All weights must sum to 1.0 within each dimension
3. **Rubric Consistency**: Scores must align with rubric descriptions
4. **Year-Level Appropriateness**: Scores adjusted for year-level expectations

### Outlier Detection:
- **Statistical Analysis**: Flag scores >2 standard deviations from mean
- **Pattern Recognition**: Identify inconsistent response patterns
- **Manual Review**: Human review of flagged profiles

### Bias Prevention:
- **Language Neutrality**: Scoring not penalized for English/French proficiency
- **Cultural Sensitivity**: Questions avoid cultural assumptions
- **Skill Balance**: No dimension disproportionately weighted

## Implementation Notes

### For LLM Integration:
1. **Prompt Engineering**: Include rubric context in LLM scoring prompts
2. **Consistency Checks**: Multiple LLM evaluations for critical questions
3. **Human Validation**: Sample manual reviews of LLM scoring

### For ML Clustering:
1. **Feature Scaling**: Normalize all scores to 0-1 range if needed
2. **Weight Application**: Apply dimension weights before clustering
3. **Collaboration Emphasis**: Give extra weight to collaboration metrics for team formation

### For Gamification:
1. **XP Calculation**: Total composite score × 100 = XP points
2. **Level Progression**: Thresholds based on year-level expectations
3. **Badge System**: Special recognition for high collaboration scores

This comprehensive scoring system ensures fair, consistent, and meaningful assessment that directly supports effective team formation and student development.
