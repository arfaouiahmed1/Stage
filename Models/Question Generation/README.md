# Question Generation RAG System

A Retrieval-Augmented Generation (RAG) system for generating educational assessment questions using Google's Gemini API and your existing CSV data as context.

## Features

- 🤖 **LLM Integration**: Uses Google Gemini API for question generation
- 🔍 **RAG System**: Retrieves relevant context from existing CSV data
- 📊 **Vector Search**: FAISS-based similarity search with sentence transformers
- 🌐 **Multiple Interfaces**: Streamlit web UI, REST API, and command-line
- 🎨 **Google Forms-like UI**: Intuitive web interface for teachers
- 📄 **Frontend-Ready JSON**: Structured output for easy frontend integration
- 🆓 **Cloud-Ready**: Uses free/cloud-based services (no local GPU required)
- 📈 **Scalable**: Designed for GitHub Codespaces and cloud deployment

## Architecture

```
CSV Data → Embeddings → Vector Index → Context Retrieval → LLM → Generated Questions
```

1. **Data Loading**: Loads questions.csv, taxonomy.csv, and rubrics.csv
2. **Embedding**: Uses SentenceTransformer for creating vector embeddings
3. **Indexing**: FAISS vector index for fast similarity search
4. **Retrieval**: Finds relevant context based on user query
5. **Generation**: Google Gemini generates new questions with context

## Setup

### 1. Install Dependencies

```bash
cd /workspaces/Stage/Models/Question\ Generation/
pip install -r requirements.txt
```

### 2. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a free API key
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### 3. Run the System

#### Option A: Streamlit Web Interface (Recommended)
```bash
./run_streamlit.sh
# Or manually: streamlit run streamlit_app.py
```
Then visit: http://localhost:8501 for a Google Forms-like interface

#### Option B: Direct Python Script
```bash
python question_generation_rag.py
```

#### Option C: REST API Server
```bash
python api.py
```
Then visit: http://localhost:8000/docs for interactive API documentation

#### Option D: Client Demo
```bash
python client_demo.py
```

## Usage Examples

### Basic Question Generation

```python
from question_generation_rag import QuestionGenerationRAG

# Initialize system
rag = QuestionGenerationRAG()

# Generate questions
questions = rag.generate_question(
    dimension="creativity",
    subcategory="innovation_problem_solving", 
    question_type="collaboration_scenario",
    target_year_level="2",
    additional_context="Focus on React web development",
    num_questions=2
)

print(questions)
```

### API Usage

```bash
# Generate questions via API
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "dimension": "teamwork",
    "subcategory": "communication_documentation",
    "target_year_level": "3",
    "num_questions": 1
  }'

# Get suggestions
curl "http://localhost:8000/suggestions?partial_input=web"

# Get available dimensions
curl "http://localhost:8000/dimensions"
```

### Search Context

```python
# Search for relevant examples
relevant_docs = rag.retrieve_relevant_context("web development teamwork", top_k=5)

for doc in relevant_docs:
    print(f"Score: {doc['score']:.3f}")
    print(f"Content: {doc['text']}")
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /generate` - Generate questions
- `GET /suggestions` - Get parameter suggestions
- `GET /dimensions` - Get available dimensions
- `GET /subcategories/{dimension}` - Get subcategories
- `GET /question-types` - Get question types
- `POST /search` - Search context
- `GET /docs` - Interactive API documentation

## Data Sources

The system uses your existing CSV files as knowledge base:

- **questions.csv**: Example questions with metadata
- **taxonomy.csv**: Dimension and subcategory definitions
- **rubrics.csv**: Assessment criteria and expectations

## Architecture Components

### 1. RAG System (`question_generation_rag.py`)
- Core logic for loading data, building embeddings, and generating questions
- Uses sentence-transformers for embeddings (runs locally, lightweight)
- FAISS for vector similarity search
- Google Gemini API for question generation

### 2. API Server (`api.py`)
- FastAPI-based REST service
- Provides web interface for the RAG system
- Handles requests and responses
- Includes automatic API documentation

### 3. Client Library (`client_demo.py`)
- Example client for interacting with the API
- Shows how to integrate the system into other applications
- Demonstrates all API endpoints

## Free/Cloud Services Used

1. **Google Gemini API**: Free tier available (1500 requests/day)
2. **Sentence Transformers**: Runs locally (lightweight model)
3. **FAISS**: Local vector index (no API needed)
4. **FastAPI**: Local web server

## Configuration

### Environment Variables

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### Model Settings

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions, fast)
- **LLM Model**: `gemini-1.5-flash` (fast, cost-effective)
- **Vector Index**: FAISS IndexFlatIP (inner product similarity)

## Deployment Options

### GitHub Codespaces (Current)
- Already configured for Codespaces
- Run API server and access via port forwarding

### Cloud Deployment
- Deploy to Heroku, Railway, or similar
- Set environment variables in platform
- Use requirements.txt for dependencies

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api.py"]
```

## Customization

### Adding New Data Sources
```python
# Extend load_data() method to include additional CSV files
def load_data(self):
    # Add your custom data loading logic
    custom_df = pd.read_csv("your_custom_data.csv")
    # Process and add to knowledge_base
```

### Custom Prompts
```python
# Modify generate_question() method
def generate_question(self, ...):
    # Customize the prompt template
    prompt = f"Your custom prompt template..."
```

### Different LLM Models
```python
# In __init__ method, change model
self.llm = genai.GenerativeModel('gemini-1.5-pro')  # More powerful
```

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Solution: Set GOOGLE_API_KEY environment variable
   export GOOGLE_API_KEY='your_key_here'
   ```

2. **Import Errors**
   ```
   Solution: Install dependencies
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```
   Solution: Change port in api.py
   uvicorn.run(app, host="0.0.0.0", port=8001)
   ```

4. **Model Download Issues**
   ```
   Solution: Ensure internet access for sentence-transformers
   ```

### Performance Optimization

- Use smaller embedding models for faster startup
- Implement caching for frequently requested questions
- Batch process multiple requests
- Use async/await for better concurrency

## Next Steps

1. **Add More Data Sources**: Include additional CSV files or databases
2. **Implement Caching**: Cache embeddings and generated questions
3. **Add Authentication**: Secure the API with API keys
4. **Create Web UI**: Build a frontend interface
5. **Advanced RAG**: Implement hybrid search, re-ranking, etc.
6. **Model Fine-tuning**: Fine-tune embeddings on domain-specific data

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the error messages in the logs
3. Ensure all environment variables are set correctly
4. Verify internet connectivity for API calls

## Streamlit Web Interface

The system includes a Google Forms-like web interface that makes it easy for teachers to generate quizzes:

### Key Features:
- **📝 Intuitive Form Interface**: Similar to Google Forms with clean, professional design
- **🎯 Smart Parameter Selection**: Dropdowns populated from your existing data
- **📊 Real-time Preview**: See generated questions immediately
- **📤 Frontend-Ready Export**: JSON output optimized for frontend teams
- **📈 Analytics Dashboard**: Track quiz generation patterns
- **📚 Quiz History**: Save and manage all generated quizzes

### Interface Sections:
1. **Generate Quiz**: Main form for creating new assessments
2. **Quiz History**: View and export previously generated quizzes  
3. **Analytics**: Dashboard showing usage patterns and statistics
4. **Export**: Download options for JSON, CSV, and reports

### JSON Output Structure:
The system generates comprehensive JSON that includes:
- Quiz metadata (title, duration, difficulty, etc.)
- Assessment framework details
- Scoring configuration with rubrics
- Individual questions with all necessary fields
- Frontend display hints and component mapping
- Collaboration requirements and team sizes

### Sample Workflow:
1. Teacher fills out the form (dimension, year level, etc.)
2. AI generates contextually appropriate questions
3. System outputs structured JSON with all frontend needs
4. Frontend team receives complete data structure for rendering