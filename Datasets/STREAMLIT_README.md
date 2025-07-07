# Streamlit Soft Skills Assessment App

This is a web-based version of the Soft Skills Assessment Notebook, built with Streamlit for easy interaction and testing.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment (Optional)
If you want to use AI-powered question generation, create a `.env` file:
```
HUGGINGFACE_API_TOKEN=your_token_here
```

Get your free token from: https://huggingface.co/settings/tokens

### 3. Run the Application
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## ✨ Features

### 🎯 Assessment Capabilities
- **Four Skill Categories**: Communication, Leadership, Time Management, Analytical
- **Flexible Question Count**: Choose 3-15 questions per category
- **Category Selection**: Include/exclude specific skill areas
- **Real-time Scoring**: Immediate feedback and results

### 🤖 Question Generation Methods
- **Template-Based**: Fast, reliable question generation using predefined templates
- **AI-Powered**: Advanced question generation using Hugging Face's language models

### 📊 Results & Analytics
- **Radar Chart Visualization**: Visual representation of your skill levels
- **Detailed Feedback**: Personalized recommendations for each category
- **Score Export**: Download results as CSV for further analysis
- **Percentage Scoring**: Clear 0-100% scale for easy understanding

### 🎨 User Experience
- **Modern Interface**: Clean, professional design
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Configuration**: Easy-to-use sidebar controls
- **Progress Tracking**: Clear indication of assessment progress

## 🔧 Technical Features

### Question Generation
- **Template System**: Sophisticated template-based generation with category-specific components
- **AI Integration**: Hugging Face Inference API integration for advanced NLP
- **Fallback Mechanism**: Automatic fallback to templates if AI generation fails
- **Quality Control**: Duplicate detection and question validation

### Data Processing
- **Real-time Calculation**: Instant score computation and feedback generation
- **Category Analysis**: Individual and comparative category performance
- **Statistical Metrics**: Average scores, percentages, and performance indicators

### Visualization
- **Plotly Integration**: Interactive radar charts for skill visualization
- **Color-coded Results**: Visual feedback based on performance levels
- **Responsive Charts**: Automatically adjusting visualizations

## 📱 Usage Guide

### Step 1: Configure Assessment
1. Open the sidebar (⚙️ Assessment Configuration)
2. Choose your question generation method
3. Set the number of questions per category (3-15)
4. Select which skill categories to include
5. Click "🚀 Generate New Assessment"

### Step 2: Take Assessment
1. Read each question carefully
2. Rate yourself on a 1-5 scale:
   - 1 = Strongly Disagree
   - 2 = Disagree  
   - 3 = Neutral
   - 4 = Agree
   - 5 = Strongly Agree
3. Answer all questions in all selected categories
4. Click "📊 Calculate Results"

### Step 3: Review Results
1. View your radar chart showing performance across categories
2. Read detailed feedback for each skill area
3. Download results as CSV if desired
4. Use insights for professional development planning

## 🎓 Educational Value

### For Students
- **Practical AI Application**: See how NLP models work in real applications
- **Data Visualization**: Learn about interactive data presentation
- **Web Development**: Understand modern web app architecture
- **Assessment Design**: Learn principles of psychometric evaluation

### For Educators
- **Teaching Tool**: Use in courses on AI, data science, or professional development
- **Assessment Platform**: Deploy for student self-evaluation
- **Technical Example**: Demonstrate practical AI implementation
- **Research Tool**: Collect data on student soft skills

### For Professionals
- **Self-Assessment**: Regular evaluation of professional skills
- **Team Building**: Use in team development sessions
- **Training Programs**: Integrate into professional development curricula
- **Performance Tracking**: Monitor skill development over time

## 🔒 Privacy & Security

- **No Data Storage**: Assessment responses are not permanently stored
- **Local Processing**: All calculations happen in your browser session
- **Optional API**: Hugging Face integration is optional and configurable
- **Open Source**: Full transparency in code and methodology

## 🛠️ Customization Options

### Adding New Categories
1. Add category to question templates and components
2. Update the category selection interface
3. Add category-specific prompts for AI generation

### Modifying Scoring
1. Edit the `calculate_results()` function
2. Adjust feedback thresholds and messages
3. Customize visualization colors and ranges

### Enhancing Visualization
1. Add new chart types using Plotly
2. Create additional statistical views
3. Implement comparison features

## 📊 Technical Architecture

### Frontend
- **Streamlit**: Python-based web framework
- **Plotly**: Interactive visualization library
- **Custom CSS**: Enhanced styling and user experience

### Backend Logic
- **Template Engine**: Dynamic question generation system
- **API Integration**: Hugging Face Inference API
- **Score Calculation**: Real-time statistical processing

### Data Flow
1. User configures assessment parameters
2. System generates questions (template or AI)
3. User provides responses via web interface
4. System calculates scores and generates feedback
5. Results displayed with visualizations

## 🚀 Deployment Options

### Local Development
```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Deploy with automatic environment setup

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
```

### Heroku Deployment
1. Add `setup.sh` and `Procfile`
2. Configure buildpacks
3. Deploy via Git integration

## 📝 Contributing

Feel free to enhance the application by:
- Adding new question templates
- Improving the user interface
- Adding new visualization options
- Enhancing the AI integration
- Writing tests and documentation

## 📄 License

This project is part of an academic research initiative focused on AI applications in educational assessment and professional development.
