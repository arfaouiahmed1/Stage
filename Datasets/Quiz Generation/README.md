# Quiz Generation Dataset

## Overview
Complete dataset collection for the Gamified Student Clustering Platform, specifically designed for software engineering education. This comprehensive dataset supports LLM-driven quiz generation, student assessment, and ML-based clustering for optimal team formation.

## Files Structure

### Core Dataset Files
- **`dimensions_taxonomy.csv`** - Complete hierarchical structure of all 4 dimensions and 21 subcategories with weights
- **`clustering_features.csv`** - ML feature template with all scoring columns for clustering algorithms
- **`scoring_system.csv`** - 0-5 point scoring scale definitions and descriptions
- **`scoring_rubrics.csv`** - Detailed scoring criteria for each dimension/subcategory combination
- **`sample_questions.csv`** - Sample quiz questions organized by category with metadata

## Scoring System Details
- **Scale**: 0-5 points across all assessments
- **0**: No Evidence - No demonstration of the skill or competency
- **1**: Poor - Minimal demonstration with significant gaps
- **2**: Below Average - Some demonstration but below expected level
- **3**: Average - Meets basic expectations for the skill
- **4**: Good - Exceeds expectations with solid demonstration
- **5**: Excellent - Exceptional demonstration of the skill

## Comprehensive Dimensions Structure

### 1. Creativity (25% overall weight)
Focuses on innovative thinking and creative problem-solving in software engineering contexts.

**Subcategories:**
- **Innovation & Problem-solving (30%)** - Novel solution approaches and creative thinking
- **Algorithm Design (25%)** - Creative and efficient algorithm development
- **System Architecture (25%)** - Innovative system design and scalability thinking
- **Code Optimization (10%)** - Creative approaches to performance improvement
- **User Experience Design (10%)** - Creative UI/UX thinking and user-centered design

### 2. Teamwork (25% overall weight)
Evaluates collaborative skills essential for software development teams.

**Subcategories:**
- **Communication & Documentation (30%)** - Clear communication and effective documentation
- **Code Review & Collaboration (25%)** - Collaborative development and peer review skills
- **Leadership & Mentoring (20%)** - Team leadership and knowledge sharing abilities
- **Conflict Resolution (15%)** - Skills in managing team disagreements and challenges
- **Agile/Scrum Participation (10%)** - Effective participation in agile development processes

### 3. Soft Skills (25% overall weight)
Personal and interpersonal skills crucial for professional software engineering success.

**Subcategories:**
- **Time Management & Planning (25%)** - Project planning and deadline management
- **Adaptability & Learning (25%)** - Flexibility and continuous learning mindset
- **Critical Thinking (25%)** - Analytical reasoning and objective evaluation
- **Presentation & Client Communication (15%)** - Stakeholder communication and presentation skills
- **Project Management (10%)** - Understanding of project management methodologies

### 4. Hard Skills (25% overall weight)
Technical competencies specific to software engineering practice.

**Subcategories:**
- **Programming Languages (30%)** - Proficiency across multiple programming paradigms
- **Software Engineering Principles (25%)** - SOLID principles, design patterns, best practices
- **Database Management (15%)** - Database design, SQL, and data management skills
- **DevOps & Deployment (15%)** - CI/CD, containerization, and deployment strategies
- **Testing & Quality Assurance (10%)** - Testing methodologies and quality assurance practices
- **Mathematics & Algorithms (5%)** - Mathematical foundations and algorithmic problem-solving

## Usage Instructions

### For LLM Quiz Generation
1. **Load Taxonomy**: Use `dimensions_taxonomy.csv` to understand the complete structure and weights
2. **Reference Rubrics**: Consult `scoring_rubrics.csv` for detailed assessment criteria for each subcategory
3. **Question Examples**: Review `sample_questions.csv` for question format and assessment criteria examples
4. **Scoring Guidelines**: Use `scoring_system.csv` for consistent 0-5 scale application

### For ML Clustering Algorithms
1. **Feature Template**: Use `clustering_features.csv` as the exact column structure for student data
2. **Weight Application**: Apply dimension and subcategory weights from `dimensions_taxonomy.csv`
3. **Score Normalization**: Ensure all scores follow the 0-5 scale defined in `scoring_system.csv`
4. **Feature Engineering**: Consider creating composite scores using the hierarchical weight structure

### For Data Processing & Analysis
1. **Import Structure**: CSV format optimized for pandas, R, and database imports
2. **Consistent IDs**: Maintain dimension/subcategory ID consistency across all systems
3. **Weight Calculations**: Use the weight columns for proper score aggregation and analysis
4. **Quality Validation**: Cross-reference scoring against rubrics for consistency

## Data Pipeline Integration

### Quiz Creation Workflow
```
dimensions_taxonomy.csv → LLM → Generated Questions → scoring_rubrics.csv → Assessment
```

### Student Assessment Workflow
```
Student Responses → scoring_rubrics.csv → Individual Scores → clustering_features.csv → ML Features
```

### Team Formation Workflow
```
clustering_features.csv → ML Algorithms → Optimal Team Groupings → Gamification System
```

## Configuration Management

### Easy Modification Capabilities
- **Weights**: All dimension and subcategory weights centralized in taxonomy CSV
- **Scoring Criteria**: Rubrics can be updated independently for each subcategory
- **New Categories**: Add new dimensions/subcategories by extending the taxonomy structure
- **Question Bank**: Expand sample questions by adding to the questions CSV
- **Scaling**: Modify the scoring system scale while maintaining rubric consistency

### Version Control Best Practices
- **File Versioning**: Include date stamps and version numbers in file modifications
- **Backup Strategy**: Maintain previous versions before making structural changes
- **Change Documentation**: Log all weight and criteria modifications
- **Testing**: Validate changes against existing data before production deployment

## Advanced Features

### Weighted Scoring System
The hierarchical weight structure allows for sophisticated scoring calculations:
- **Dimension Level**: Each dimension contributes 25% to overall score
- **Subcategory Level**: Within each dimension, subcategories have specific weights
- **Flexible Weighting**: Weights can be adjusted for different course contexts or learning objectives

### Comprehensive Rubrics
Each subcategory includes detailed 0-5 scoring criteria that:
- **Define Clear Expectations**: Specific descriptions for each score level
- **Ensure Consistency**: Standardized assessment across different evaluators
- **Support Development**: Clear progression paths for student improvement
- **Enable Automation**: Structured format suitable for automated scoring systems

### Sample Question Framework
The question bank provides templates for:
- **Multiple Question Types**: Open-ended, scenarios, coding challenges, analysis tasks
- **Difficulty Levels**: Basic, intermediate, and advanced complexity
- **Time Management**: Suggested time limits for each question type
- **Assessment Criteria**: Multiple evaluation dimensions for comprehensive assessment

## Future Enhancement Opportunities

### Scalability Features
- **Additional Dimensions**: Framework supports easy addition of new assessment areas
- **Specialized Rubrics**: Custom scoring criteria for specific course or industry contexts
- **Advanced Weighting**: Dynamic weight adjustment based on course progression or learning objectives
- **Multi-Language Support**: Extension to support multiple programming language contexts

### Integration Capabilities
- **LMS Integration**: Compatible with learning management system data formats
- **API Development**: CSV structure ready for REST API implementation
- **Real-time Processing**: Suitable for live assessment and immediate feedback systems
- **Analytics Integration**: Structured for advanced learning analytics and progress tracking

This comprehensive dataset structure provides a robust foundation for intelligent student assessment and team formation in software engineering education contexts.
