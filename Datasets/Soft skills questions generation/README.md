# Soft Skills Questions Generation & Student Clustering

## 📖 Overview

This project provides a comprehensive solution for **soft skills assessment** and **automated student group formation** using machine learning clustering algorithms. The system is specifically adapted for **Tunisian IT engineering students** using the local educational context (moyenne scale 0-20, IT specializations).

## 🎯 Features

### Question Generation
- **Web Scraping**: Automated collection of soft skills questions from professional websites
- **AI Generation**: Hugging Face API integration for intelligent question creation
- **Template-based Generation**: Fallback system using structured templates
- **Multi-category Support**: Communication, Leadership, Time Management, Analytical skills

### Student Clustering & Group Formation
- **4 Clusters**: Students grouped by skill profiles and learning characteristics
- **Groups of 5**: Heterogeneous groups with maximum diversity
- **Tunisian Context**: Uses "moyenne" (0-20 scale) and IT specializations
- **Automated Balance**: Ensures diversity across specializations, programming languages, and skill levels

## 📁 Files Structure

```
├── soft_skills_assessment.ipynb     # Main notebook with complete pipeline
├── all_soft_skills_questions.csv   # Combined questions from all categories
├── communication_questions.csv     # Communication skills questions
├── leadership_questions.csv        # Leadership skills questions  
├── time_management_questions.csv   # Time management questions
├── analytical_questions.csv        # Analytical thinking questions
├── student_group_assignments.csv   # Generated group assignments
├── complete_student_analysis.csv   # Full student analysis results
└── README.md                       # This documentation
```

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas numpy scikit-learn plotly tqdm beautifulsoup4 requests python-dotenv
```

### Optional: Hugging Face API
1. Get a free token from [huggingface.co](https://huggingface.co)
2. Create `.env` file: `HUGGINGFACE_API_TOKEN=your_token`
3. System works perfectly without API using template generation

### Usage
1. Open `soft_skills_assessment.ipynb` in Jupyter/VS Code
2. Run all cells to:
   - Generate soft skills questions
   - Create student assessment data
   - Perform clustering analysis (4 clusters)
   - Form heterogeneous groups (5 students each)
   - Generate visualizations and reports

## 🎓 Educational Context (Tunisia)

### Adapted for Tunisian IT Engineering:
- **Academic Scale**: Uses "moyenne" (0-20) instead of GPA
- **Specializations**: Software Engineering, Data Science, Cybersecurity, etc.
- **Programming Languages**: Python, Java, JavaScript, C++, etc.
- **Student Archetypes**: Technical Leader, Analytical Thinker, Creative Innovator, etc.

### Group Formation Benefits:
- **Diversity**: Each group contains students from different clusters
- **Balance**: Skills, specializations, and academic levels are distributed
- **Learning**: Heterogeneous groups enhance collaborative learning
- **Bias Reduction**: Automated process eliminates instructor preferences

## 📊 Results

### Clustering Output:
- **Cluster 0**: 24 students (20.0%) - Emerging scholars and creative types
- **Cluster 1**: 27 students (22.5%) - Collaborative communicators  
- **Cluster 2**: 37 students (30.8%) - Technical leaders and analysts
- **Cluster 3**: 32 students (26.7%) - Well-rounded students

### Group Formation:
- **24 groups** of 5 students each (120 total students)
- **Average 3.8 specializations** per group
- **4 clusters represented** across all groups
- **Balanced moyenne distribution** (academic performance)

## 🔧 Technical Details

### Clustering Algorithm:
- **Method**: K-Means with k=4 (fixed)
- **Features**: Soft skills scores, moyenne, specialization, programming language, learning style
- **Preprocessing**: StandardScaler for feature normalization
- **Validation**: Silhouette analysis and cluster distribution

### Group Formation Strategy:
- **Diverse Strategy**: Maximizes heterogeneity within groups
- **Selection**: One student from each cluster when possible
- **Balancing**: Different specializations and programming languages preferred
- **Fallback**: Random assignment for remaining spots

## 📈 Visualizations

The notebook generates interactive Plotly charts:
- **Cluster Analysis**: PCA visualization, cluster means heatmap
- **Group Distribution**: Size distribution, cluster representation
- **Student Profiles**: Individual radar charts for skill assessment
- **Diversity Metrics**: Specialization and academic performance distribution

## 🌟 Use Cases

- **Course Projects**: Automatically form balanced teams
- **Collaborative Learning**: Create diverse study groups  
- **Skill Development**: Expose students to different perspectives
- **Assessment**: Evaluate soft skills across multiple dimensions
- **Research**: Analyze group dynamics and learning outcomes

## 🤝 Contributing

This project is part of the Stage ESPRIT research initiative for educational technology innovation in Tunisia.

## 📄 License

Academic use for educational institutions and research purposes.

---

**Developed for ESPRIT - École Supérieure Privée d'Ingénierie et de Technologies**
*Adapté pour le contexte éducatif tunisien en ingénierie informatique*
