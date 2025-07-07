# Soft Skills Assessment Platform

A comprehensive tool for evaluating and developing soft skills through interactive assessments, machine learning-powered recommendations, and intelligent question generation.

## 🎯 Overview

This project provides a complete solution for soft skills assessment covering four key areas:
- **Communication Skills**: Written and verbal communication effectiveness
- **Leadership Skills**: Team management, motivation, and decision-making abilities  
- **Time Management Skills**: Prioritization, planning, and productivity optimization
- **Analytical Skills**: Problem-solving, data analysis, and critical thinking

## 🚀 Features

### 📊 Assessment System
- Interactive HTML-based assessment forms
- 5-point Likert scale rating system (Strongly Disagree to Strongly Agree)
- Real-time scoring and feedback
- Category-specific and comprehensive mixed assessments

### 🤖 Intelligent Question Generation
- **Web Scraping**: Automated collection from professional HR and assessment websites
- **Template-Based Generation**: Structured approach using predefined templates and components
- **AI-Powered Generation**: Integration with Hugging Face's language models for varied question creation
- Dynamic question pool management

### 📈 Machine Learning Models
- Trained classification models for skill assessment
- Feature selection and optimization
- Predictive analytics for skill development recommendations

### 🎨 User Interface
- Modern, responsive web interface
- Intuitive assessment flow
- Immediate results and feedback
- Professional styling and user experience

## 📁 Project Structure

```
Stage/
├── README.md                           # Project documentation
├── scraped_soft_skills_questions_raw.csv  # Raw scraped questions
├── Datasets/                           # Data and analysis notebooks
│   └── soft_skills_assessment.ipynb   # Core assessment notebook
├── Deployments/                        # Deployment configurations
│   ├── Backend/                        # Backend deployment
│   └── Frontend/                       # Frontend deployment
└── Models/                             # AI/ML model implementations
    ├── Avatar Generation/              # User avatar generation
    ├── Question Generation/            # Question generation models
    └── Recommendation System/          # Skill recommendation engine
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Jupyter Notebook/Lab
- Required Python packages (see requirements below)

### Dependencies

```bash
pip install pandas numpy requests beautifulsoup4 tqdm ipython
pip install scikit-learn matplotlib seaborn plotly
pip install python-dotenv  # For environment variables
```

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/arfaouiahmed1/Stage.git
cd Stage
```

2. Set up environment variables (optional, for AI-powered generation):
```bash
# Create .env file for Hugging Face API token
echo "HUGGINGFACE_API_TOKEN=your_token_here" > .env
```

3. Run the main assessment notebook:
```bash
jupyter notebook Datasets/soft_skills_assessment.ipynb
```

## 📋 Usage

### Running an Assessment

1. **Open the Assessment Notebook**:
   ```bash
   jupyter notebook Datasets/soft_skills_assessment.ipynb
   ```

2. **Execute the Cells**: Run all cells to:
   - Scrape questions from professional websites
   - Generate additional questions using templates or AI
   - Create interactive assessment forms

3. **Take the Assessment**: 
   - Complete the interactive HTML form
   - Rate yourself on each statement (1-5 scale)
   - Receive immediate feedback and scoring

### Question Generation Methods

#### Method 1: Web Scraping
```python
# Automatically scrape questions from HR websites
scraped_df = scrape_soft_skills_questions('communication')
```

#### Method 2: Template-Based Generation
```python
# Generate questions using predefined templates
generated_df = generate_questions_with_templates('leadership', n=20)
```

#### Method 3: AI-Powered Generation
```python
# Use Hugging Face models for question generation
ai_questions = generate_questions_with_huggingface('analytical', n=15)
```

### Assessment Categories

Each assessment focuses on specific competencies:

#### 🗣️ Communication Skills
- Clear and effective verbal communication
- Written communication proficiency
- Active listening abilities
- Presentation and public speaking
- Cross-cultural communication

#### 👥 Leadership Skills
- Team motivation and inspiration
- Decision-making under pressure
- Delegation and empowerment
- Conflict resolution
- Strategic vision communication

#### ⏰ Time Management Skills
- Task prioritization and planning
- Deadline management
- Productivity optimization
- Interruption handling
- Work-life balance

#### 🧠 Analytical Skills
- Problem-solving methodologies
- Data interpretation and analysis
- Critical thinking processes
- Pattern recognition
- Evidence-based decision making

## 🎯 Assessment Scoring

### Scoring System
- **1**: Strongly Disagree
- **2**: Disagree  
- **3**: Neutral
- **4**: Agree
- **5**: Strongly Agree

### Feedback Levels
- **4.5-5.0**: Outstanding performance
- **3.5-4.4**: Good with room for improvement
- **2.5-3.4**: Moderate skills, development needed
- **Below 2.5**: Area requiring significant attention

## 🔧 Technical Details

### Data Sources
- Professional HR assessment websites
- Industry-standard competency frameworks
- Academic research on soft skills evaluation

### Machine Learning Pipeline
1. **Data Collection**: Web scraping and generation
2. **Feature Engineering**: Text processing and skill categorization
3. **Model Training**: Classification algorithms for skill assessment
4. **Optimization**: Hyperparameter tuning and feature selection
5. **Deployment**: Integrated assessment system

### API Integration
- Hugging Face Inference API for advanced question generation
- BeautifulSoup for web scraping
- Pandas for data manipulation and analysis

## 🚀 Deployment

The project supports multiple deployment options:

### Local Development
```bash
jupyter notebook Datasets/soft_skills_assessment.ipynb
```

### Production Deployment
See `Deployments/` directory for:
- Backend API deployment configurations
- Frontend web interface setup
- Cloud deployment scripts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📊 Data Privacy & Ethics

- All assessment data is processed locally by default
- No personal information is stored without consent
- Questions are designed to be culturally neutral and inclusive
- Results are provided for self-development purposes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Authors

- **Ahmed Arfaoui** - [@arfaouiahmed1](https://github.com/arfaouiahmed1)
- **Siwar** - Data Science and Assessment Development

## 🙏 Acknowledgments

- HR assessment websites for providing reference questions
- Hugging Face for AI model access
- Open source community for tools and libraries
- ESPRIT institution for project support

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation in the `Datasets/` directory

---

*Built with ❤️ for professional development and soft skills enhancement*