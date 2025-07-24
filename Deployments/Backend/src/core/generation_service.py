import os
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai
from typing import List, Dict, Any
import numpy as np
from dotenv import load_dotenv

class QuestionGenerationService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure Google Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Initialize embedding model and FAISS index
        self.embed_model = None
        self.index = None
        self.texts = []
        self.metadatas = []
        self.df = None
        
        # Load questions dataset
        self._load_dataset()
        self._setup_embeddings()
    
    def _load_dataset(self):
        """Load the questions CSV dataset"""
        try:
            # Path to the questions CSV - from Backend directory to project root
            # Backend/src/core/generation_service.py -> go up to Backend/ then ../../Datasets
            backend_dir = Path(__file__).parent.parent.parent  # This gets us to Backend/
            csv_path = (backend_dir / "../../Datasets/Quiz Generation/questions.csv").resolve()
            
            if not csv_path.exists():
                raise FileNotFoundError(f"Questions dataset not found at: {csv_path}")
            
            # Load CSV, skip the first row (comment)
            self.df = pd.read_csv(csv_path, skiprows=1)
            
            # Strip whitespace from column names
            self.df.columns = self.df.columns.str.strip()
            
            # Extract texts and metadata
            self.texts = self.df["question_text"].tolist()
            self.metadatas = self.df[["dimension", "subdimension", "target_year_level", "question_id"]].to_dict(orient="records")
            
            print(f"✅ Loaded {len(self.texts)} questions from dataset")
            
        except Exception as e:
            raise Exception(f"Failed to load questions dataset: {str(e)}")
    
    def _setup_embeddings(self):
        """Setup sentence transformer and FAISS index for similarity search"""
        try:
            print("🔄 Setting up embeddings and FAISS index...")
            
            # Initialize sentence transformer
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Generate embeddings for all questions
            embeddings = self.embed_model.encode(self.texts, convert_to_numpy=True)
            
            # Setup FAISS index
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
            print(f"✅ FAISS index created with {self.index.ntotal} vectors")
            
        except Exception as e:
            raise Exception(f"Failed to setup embeddings: {str(e)}")
    
    def get_available_dimensions(self) -> List[str]:
        """Get all available dimensions from the dataset"""
        return sorted(self.df["dimension"].unique().tolist())
    
    def get_available_subdimensions(self, dimension: str) -> List[str]:
        """Get all available subdimensions for a given dimension"""
        filtered_df = self.df[self.df["dimension"] == dimension]
        return sorted(filtered_df["subdimension"].unique().tolist())
    
    def get_available_year_levels(self) -> List[int]:
        """Get all available target year levels"""
        return sorted(self.df["target_year_level"].unique().tolist())
    
    def validate_generation_params(self, dimension: str, subdimension: str, target_year_level: int) -> bool:
        """Validate if the given parameters exist in the dataset"""
        mask = (
            (self.df["dimension"] == dimension) & 
            (self.df["subdimension"] == subdimension) & 
            (self.df["target_year_level"] == target_year_level)
        )
        return len(self.df[mask]) > 0
    
    def _get_context_questions(self, dimension: str, subdimension: str, target_year_level: int, 
                             additional_context: str = None, num_context: int = 5) -> List[str]:
        """Get context questions for RAG-based generation"""
        
        # Filter by metadata first
        mask = (
            (self.df["dimension"] == dimension) & 
            (self.df["subdimension"] == subdimension) & 
            (self.df["target_year_level"] == target_year_level)
        )
        candidates = self.df[mask]
        
        if additional_context and len(additional_context.strip()) > 0:
            # Use semantic similarity if additional context is provided
            query_emb = self.embed_model.encode([additional_context], convert_to_numpy=True)
            faiss.normalize_L2(query_emb)
            D, I = self.index.search(query_emb, k=num_context)
            context_questions = [self.texts[i] for i in I[0]]
        else:
            # Use random sampling from filtered candidates
            sample_size = min(num_context, len(candidates))
            context_questions = candidates["question_text"].sample(sample_size).tolist()
        
        return context_questions
    
    def generate_questions(self, dimension: str, subdimension: str, target_year_level: int, 
                          additional_context: str = None) -> Dict[str, Any]:
        """
        Generate a single question using LLM with RAG context
        
        Args:
            dimension: The dimension (e.g., 'creativity', 'teamwork')
            subdimension: The subdimension (e.g., 'innovation_problem_solving')
            target_year_level: The target year level (1, 2, or 3)
            additional_context: Optional additional context for generation
            
        Returns:
            Dict containing generated question and metadata
        """
        
        # Validate parameters
        if not self.validate_generation_params(dimension, subdimension, target_year_level):
            raise ValueError(f"No questions found for dimension='{dimension}', subdimension='{subdimension}', target_year_level={target_year_level}")
        
        # Get context questions
        context_questions = self._get_context_questions(
            dimension, subdimension, target_year_level, additional_context
        )
        
        # Build prompt for LLM
        prompt = self._build_generation_prompt(
            dimension, subdimension, target_year_level, 1, context_questions
        )
        
        # Generate questions using LLM
        try:
            response = self.model.generate_content(prompt)
            generated_text = response.text
            
            # Parse generated question (only one)
            questions = self._parse_generated_questions(generated_text, 1)
            question = questions[0] if questions else "Generated question could not be parsed"
            
            return {
                "question": question,
                "dimension": dimension,
                "subdimension": subdimension,
                "target_year_level": target_year_level,
                "context_used": context_questions
            }
            
        except Exception as e:
            if "401" in str(e) or "UNAUTHENTICATED" in str(e).upper():
                raise ValueError("Invalid or missing Google API key")
            else:
                raise Exception(f"LLM generation error: {str(e)}")
    
    def _build_generation_prompt(self, dimension: str, subdimension: str, target_year_level: int, 
                                num_questions: int, context_questions: List[str]) -> str:
        """Build the prompt for LLM generation"""
        
        context_text = "\n".join(f"- {q}" for q in context_questions)
        
        prompt = f"""Generate 1 self-assessment question for "{dimension} - {subdimension}" at year level {target_year_level}.

The question should be a clear self-assessment statement using 'How confident are you...' or similar phrasing.
This is a 5-point Likert scale question where:
1 = Strongly Disagree
2 = Disagree  
3 = Neutral
4 = Agree
5 = Strongly Agree

Use these examples as context:
{context_text}

Requirements:
- Generate exactly 1 question
- The question should be self-assessment focused
- Question should be appropriate for year level {target_year_level}
- Use clear, professional language
- Return only the question text, no numbering or formatting

Generate the question now:"""

        return prompt
    
    def _parse_generated_questions(self, generated_text: str, expected_count: int) -> List[str]:
        """Parse and clean generated questions from LLM output"""
        
        # Split by lines and clean up
        lines = generated_text.split('\n')
        questions = []
        
        for line in lines:
            cleaned_line = line.strip()
            
            # Skip empty lines and lines that start with common prefixes
            if not cleaned_line:
                continue
            if cleaned_line.startswith(('*', '-', '•')):
                cleaned_line = cleaned_line[1:].strip()
            if cleaned_line.startswith(tuple(f"{i}." for i in range(1, 21))):
                # Remove numbering like "1.", "2.", etc.
                cleaned_line = cleaned_line.split('.', 1)[1].strip()
            
            if cleaned_line and len(cleaned_line) > 10:  # Ensure it's a meaningful question
                questions.append(cleaned_line)
        
        # Take only the requested number of questions
        return questions[:expected_count]
