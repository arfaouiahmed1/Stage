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
            # Path to the balanced questions CSV - from Backend directory to project root
            # Backend/src/core/generation_service.py -> go up to Backend/ then ../../Datasets
            backend_dir = Path(__file__).parent.parent.parent  # This gets us to Backend/
            csv_path = (backend_dir / "../../Datasets/Final Datasets/All Questions.csv").resolve()
            
            if not csv_path.exists():
                raise FileNotFoundError(f"Questions dataset not found at: {csv_path}")
            
            # Load CSV (no comment row to skip in the new format)
            self.df = pd.read_csv(csv_path)
            
            # Strip whitespace from column names
            self.df.columns = self.df.columns.str.strip()
            
            # Extract texts and metadata (no response_scale column in new format)
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
        """Validate if the given parameters can be used for generation (relaxed for custom subdimensions)"""
        # Check if dimension exists in dataset
        available_dimensions = self.get_available_dimensions()
        if dimension not in available_dimensions:
            return False
        
        # Check if target year level is valid (1, 2, or 3)
        if target_year_level not in [1, 2, 3]:
            return False
        
        # For custom subdimensions, we don't need exact match - just check if dimension exists
        # This allows teachers to create custom subcategories
        return True
    
    def _get_context_questions(self, dimension: str, subdimension: str, target_year_level: int, 
                             num_context: int = 5) -> List[str]:
        """Get context questions for RAG-based generation (supports custom subdimensions)"""
        
        # First try to find exact match (existing subdimension)
        mask = (
            (self.df["dimension"] == dimension) & 
            (self.df["subdimension"] == subdimension) & 
            (self.df["target_year_level"] == target_year_level)
        )
        candidates = self.df[mask]
        
        # If no exact match found (custom subdimension), broaden search to dimension + year level
        if len(candidates) == 0:
            print(f"🔄 Custom subdimension '{subdimension}' detected. Using dimension-level context.")
            mask = (
                (self.df["dimension"] == dimension) & 
                (self.df["target_year_level"] == target_year_level)
            )
            candidates = self.df[mask]
            
            # If still no candidates, use dimension only
            if len(candidates) == 0:
                mask = (self.df["dimension"] == dimension)
                candidates = self.df[mask]
        
        # Use random sampling from filtered candidates
        sample_size = min(num_context, len(candidates))
        if sample_size > 0:
            context_questions = candidates["question_text"].sample(sample_size).tolist()
        else:
            # Fallback: use any questions from the dimension
            dimension_questions = self.df[self.df["dimension"] == dimension]
            sample_size = min(num_context, len(dimension_questions))
            context_questions = dimension_questions["question_text"].sample(sample_size).tolist()
        
        return context_questions
    
    def generate_questions(self, dimension: str, subdimension: str, target_year_level: int, 
                          additional_context: str = None) -> Dict[str, Any]:
        """
        Generate a single question using LLM with RAG context
        
        Args:
            dimension: The dimension (e.g., 'creativity', 'teamwork')
            subdimension: The subdimension (e.g., 'innovation_problem_solving')
            target_year_level: The target year level (1, 2, or 3)
            additional_context: Optional additional context (deprecated)
            
        Returns:
            Dict containing generated question and metadata
        """
        
        # Validate parameters
        if not self.validate_generation_params(dimension, subdimension, target_year_level):
            raise ValueError(f"Invalid parameters: dimension='{dimension}', target_year_level={target_year_level}")
        
        # Get context questions with enhanced diversity
        context_questions = self._get_context_questions(
            dimension, subdimension, target_year_level, num_context=3
        )
        
        # Add variation seed to ensure different outputs
        variation_context = self._get_variation_context()
        
        # Build enhanced prompt for LLM
        prompt = self._build_generation_prompt(
            dimension, subdimension, target_year_level, 1, context_questions
        )
        
        # Add variation context to the prompt
        if variation_context:
            prompt += f"\n\nADDITIONAL FOCUS: {variation_context}"
        
        # Generate questions using LLM
        try:
            response = self.model.generate_content(prompt)
            generated_text = response.text
            
            # Parse generated question (only one)
            questions = self._parse_generated_questions(generated_text, 1)
            question = questions[0] if questions else "Generated question could not be parsed"
            
            # Validate that the question is a proper Likert scale question
            validated_question = self._validate_likert_question(question, dimension, subdimension)
            
            return {
                "question": validated_question,
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
    
    def _get_variation_context(self) -> str:
        """Generate variation context to ensure diverse question outputs"""
        import random
        
        variation_aspects = [
            "Focus on practical application in real-world scenarios",
            "Emphasize peer interaction and collaboration aspects",
            "Consider individual reflection and self-assessment",
            "Include scenario-based thinking and problem-solving",
            "Focus on measurable behaviors and observable skills",
            "Emphasize growth mindset and learning orientation",
            "Consider workplace or academic environment contexts",
            "Focus on communication and expression aspects"
        ]
        
        return random.choice(variation_aspects)
    
    def _validate_likert_question(self, question: str, dimension: str, subdimension: str) -> str:
        """Validate and enhance the question to ensure it's a proper Likert scale question"""
        
        # Check if question starts with typical Likert patterns
        likert_patterns = ["I am", "I can", "I feel", "I have", "I consistently", "I effectively"]
        
        if not any(question.strip().startswith(pattern) for pattern in likert_patterns):
            # If it doesn't start properly, try to fix it
            if "?" in question:
                # Convert question format to statement format
                question = question.replace("How confident are you", "I am confident")
                question = question.replace("Can you", "I can")
                question = question.replace("?", "")
            
            # Ensure it starts with a first-person statement
            if not any(question.strip().startswith(pattern) for pattern in likert_patterns):
                question = f"I am confident in my ability to {question.lower()}"
        
        # Ensure the question ends properly (remove any trailing punctuation and add period)
        question = question.rstrip("?.!") + "."
        
        return question
    
    def _build_generation_prompt(self, dimension: str, subdimension: str, target_year_level: int, 
                                num_questions: int, context_questions: List[str]) -> str:
        """Build the prompt for LLM generation with dimension-specific enhancements"""
        
        # Get dimension-specific prompt elements
        dimension_context = self._get_dimension_specific_context(dimension, subdimension)
        question_starters = self._get_question_starters_for_dimension(dimension)
        context_text = "\n".join(f"- {q}" for q in context_questions)
        
        prompt = f"""Create a 5-point Likert scale self-assessment question for "{dimension} - {subdimension}" (Year Level {target_year_level}).

CONTEXT: {dimension_context}

REQUIREMENTS:
- Start with one of these: {', '.join(question_starters)}
- Must be answerable on 1-5 scale (1=Strongly Disagree, 5=Strongly Agree)
- Target Year Level {target_year_level} complexity
- Focus specifically on {subdimension}
- Make it unique and varied from examples below

EXAMPLES FOR REFERENCE:
{context_text}

OUTPUT: Return ONLY the question statement, nothing else. No explanations, no formatting, just the question.

Question:"""

        return prompt
    
    def _get_dimension_specific_context(self, dimension: str, subdimension: str) -> str:
        """Get dimension-specific context and guidance for question generation"""
        
        dimension_contexts = {
            "creativity": {
                "innovation_problem_solving": "Focus on students' ability to generate novel solutions, think outside conventional boundaries, and approach problems with original perspectives. Questions should assess creative thinking processes, idea generation, and innovative problem-solving approaches.",
                "original_thinking": "Assess students' capacity for independent thought, unique perspectives, and original idea development. Questions should evaluate their comfort with unconventional thinking and ability to generate fresh insights.",
                "creative_expression": "Evaluate students' confidence in expressing ideas creatively through various mediums and their willingness to share original work. Focus on creative communication and artistic expression."
            },
            "soft_skills": {
                "communication": "Assess verbal and written communication abilities, active listening skills, and clarity of expression. Questions should evaluate interpersonal communication effectiveness and presentation skills.",
                "teamwork": "Focus on collaboration abilities, conflict resolution, group dynamics, and collective goal achievement. Assess comfort with team roles and contribution to group success.",
                "leadership": "Evaluate leadership potential, decision-making confidence, ability to guide others, and taking initiative. Focus on both formal and informal leadership situations.",
                "time_management": "Assess organizational skills, prioritization abilities, deadline management, and work-life balance. Focus on planning and execution of tasks efficiently.",
                "adaptability": "Evaluate flexibility in changing situations, openness to new approaches, and resilience in face of challenges. Focus on comfort with uncertainty and change management."
            },
            "critical_thinking": {
                "analysis": "Focus on ability to break down complex information, identify patterns, and examine details systematically. Assess analytical reasoning and logical thinking processes.",
                "evaluation": "Assess judgment skills, ability to assess credibility of sources, and making informed decisions based on evidence. Focus on critical assessment abilities.",
                "synthesis": "Evaluate ability to combine information from multiple sources, create new understanding, and integrate diverse perspectives into coherent conclusions."
            },
            "emotional_intelligence": {
                "self_awareness": "Focus on understanding personal emotions, recognizing emotional triggers, and awareness of personal strengths and limitations.",
                "empathy": "Assess ability to understand others' emotions, perspective-taking skills, and sensitivity to others' feelings and needs.",
                "social_skills": "Evaluate interpersonal relationship management, social interaction comfort, and ability to navigate social situations effectively."
            }
        }
        
        return dimension_contexts.get(dimension, {}).get(subdimension, 
            f"Focus on {subdimension} within the {dimension} dimension. Assess relevant skills, behaviors, and competencies.")
    
    def _get_question_starters_for_dimension(self, dimension: str) -> List[str]:
        """Get varied question starters specific to each dimension"""
        
        starters_by_dimension = {
            "creativity": [
                "I am confident in my ability to",
                "When faced with challenges, I can",
                "I feel comfortable",
                "I am skilled at",
                "I consistently demonstrate",
                "I effectively",
                "I have strong capabilities in",
                "I am adept at"
            ],
            "soft_skills": [
                "I am effective at",
                "I feel confident in my ability to",
                "I consistently",
                "I am skilled in",
                "I can successfully",
                "I am comfortable",
                "I have developed strong",
                "I demonstrate good"
            ],
            "critical_thinking": [
                "I am capable of",
                "I can effectively",
                "I am skilled at",
                "I consistently apply",
                "I can successfully",
                "I feel confident in my ability to",
                "I demonstrate strong",
                "I am proficient in"
            ],
            "emotional_intelligence": [
                "I am aware of",
                "I can recognize",
                "I understand",
                "I am sensitive to",
                "I can effectively manage",
                "I am in tune with",
                "I can identify",
                "I have good awareness of"
            ]
        }
        
        # Return dimension-specific starters or default ones
        return starters_by_dimension.get(dimension, [
            "I am confident in my ability to",
            "I feel comfortable",
            "I am skilled at",
            "I can effectively",
            "I consistently demonstrate",
            "I have strong capabilities in"
        ])
    
    def _parse_generated_questions(self, generated_text: str, expected_count: int) -> List[str]:
        """Parse and clean generated questions from LLM output"""
        
        # Clean up the generated text first
        text = generated_text.strip()
        
        # Remove common prefixes and formatting artifacts
        lines_to_remove = [
            "here is 1 unique self-assessment question",
            "here is a unique self-assessment question",
            "here's 1 unique self-assessment question",
            "here's a unique self-assessment question",
            "generated question:",
            "question:",
            "self-assessment question:"
        ]
        
        for line_prefix in lines_to_remove:
            if line_prefix in text.lower():
                # Find the position after this prefix
                pos = text.lower().find(line_prefix) + len(line_prefix)
                text = text[pos:].strip()
        
        # Split by lines and clean up
        lines = text.split('\n')
        questions = []
        
        for line in lines:
            cleaned_line = line.strip()
            
            # Skip empty lines and lines that start with common prefixes
            if not cleaned_line:
                continue
                
            # Remove markdown formatting, bullets, and numbering
            if cleaned_line.startswith(('*', '-', '•', '**')):
                cleaned_line = cleaned_line.lstrip('*-•').strip()
            
            # Remove numbering like "1.", "2.", etc.
            if cleaned_line.startswith(tuple(f"{i}." for i in range(1, 21))):
                cleaned_line = cleaned_line.split('.', 1)[1].strip()
            
            # Remove colons at the end of setup text
            if cleaned_line.endswith(':'):
                continue
                
            # Remove common metadata patterns
            skip_patterns = [
                "for year level", "targeting year level", "dimension:", "subdimension:",
                "context:", "requirements:", "example:", "scale:", "students:"
            ]
            
            if any(pattern in cleaned_line.lower() for pattern in skip_patterns):
                continue
            
            # Only accept meaningful questions (first-person statements)
            if (cleaned_line and 
                len(cleaned_line) > 15 and  # Minimum meaningful length
                any(cleaned_line.startswith(starter) for starter in ["I am", "I can", "I feel", "I have", "I consistently", "I effectively", "I demonstrate"]) and
                not cleaned_line.endswith(':')):
                
                # Ensure proper punctuation
                if not cleaned_line.endswith('.'):
                    cleaned_line += '.'
                    
                questions.append(cleaned_line)
        
        # If no proper questions found, try to extract from the whole text
        if not questions and text:
            # Look for sentences that start with "I am", "I can", etc.
            import re
            pattern = r'(I (?:am|can|feel|have|consistently|effectively|demonstrate)[^.!?]*[.!?])'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                questions = [match.strip() for match in matches]
        
        # Take only the requested number of questions
        return questions[:expected_count] if questions else ["I am confident in my ability to apply innovative problem-solving approaches."]
