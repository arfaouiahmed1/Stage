import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class QuestionGenerationRAG:
    """
    Question Generation system using RAG with Google Gemini API
    Uses existing CSV data as knowledge base for context-aware question generation
    """
    
    def __init__(self, data_folder_path: str = "../../Datasets/Quiz Generation"):
        """
        Initialize the RAG system
        
        Args:
            data_folder_path: Path to the folder containing CSV files
        """
        self.data_folder_path = Path(data_folder_path)
        self.embedding_model = None
        self.vector_index = None
        self.knowledge_base = []
        self.documents = []
        
        # Configure Google Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Please set GOOGLE_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize embedding model (free, runs locally but lightweight)
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded successfully!")
        
        # Load and process data
        self.load_data()
        self.build_vector_index()
    
    def load_data(self):
        """Load and process CSV data into knowledge base"""
        print("Loading data from CSV files...")
        
        # Load questions data
        questions_file = self.data_folder_path / "questions.csv"
        if questions_file.exists():
            questions_df = pd.read_csv(questions_file)
            for _, row in questions_df.iterrows():
                doc = {
                    'type': 'question',
                    'id': row.get('question_id', ''),
                    'dimension': row.get('dimension', ''),
                    'subcategory': row.get('subcategory', ''),
                    'question_text': row.get('question_text', ''),
                    'question_type': row.get('question_type', ''),
                    'target_year_level': row.get('target_year_level', ''),
                    'time_limit_minutes': row.get('time_limit_minutes', ''),
                    'assessment_criteria': [
                        row.get('assessment_criteria_1', ''),
                        row.get('assessment_criteria_2', ''),
                        row.get('assessment_criteria_3', '')
                    ],
                    'collaboration_indicator': row.get('collaboration_indicator', '')
                }
                
                # Create searchable text
                searchable_text = f"""
                Question: {doc['question_text']}
                Dimension: {doc['dimension']}
                Subcategory: {doc['subcategory']}
                Type: {doc['question_type']}
                Year Level: {doc['target_year_level']}
                Assessment Criteria: {', '.join(doc['assessment_criteria'])}
                Collaboration Level: {doc['collaboration_indicator']}
                """
                
                self.documents.append(searchable_text.strip())
                self.knowledge_base.append(doc)
        
        # Load taxonomy data
        taxonomy_file = self.data_folder_path / "taxonomy.csv"
        if taxonomy_file.exists():
            taxonomy_df = pd.read_csv(taxonomy_file)
            for _, row in taxonomy_df.iterrows():
                doc = {
                    'type': 'taxonomy',
                    'dimension_id': row.get('dimension_id', ''),
                    'dimension_name': row.get('dimension_name', ''),
                    'dimension_weight': row.get('dimension_weight', ''),
                    'subcategory_id': row.get('subcategory_id', ''),
                    'subcategory_name': row.get('subcategory_name', ''),
                    'subcategory_weight': row.get('subcategory_weight', ''),
                    'subcategory_description': row.get('subcategory_description', '')
                }
                
                searchable_text = f"""
                Taxonomy - Dimension: {doc['dimension_name']} ({doc['dimension_id']})
                Subcategory: {doc['subcategory_name']} ({doc['subcategory_id']})
                Description: {doc['subcategory_description']}
                Weight: {doc['subcategory_weight']}
                """
                
                self.documents.append(searchable_text.strip())
                self.knowledge_base.append(doc)
        
        # Load rubrics data
        rubrics_file = self.data_folder_path / "rubrics.csv"
        if rubrics_file.exists():
            rubrics_df = pd.read_csv(rubrics_file)
            for _, row in rubrics_df.iterrows():
                doc = {
                    'type': 'rubric',
                    'scoring_level': row.get('scoring_level', ''),
                    'label': row.get('label', ''),
                    'description': row.get('description', ''),
                    'year_expectations': {
                        'year_1': row.get('year_1_expectation', ''),
                        'year_2': row.get('year_2_expectation', ''),
                        'year_3': row.get('year_3_expectation', ''),
                        'year_4': row.get('year_4_expectation', ''),
                        'year_5': row.get('year_5_expectation', '')
                    }
                }
                
                searchable_text = f"""
                Rubric Level {doc['scoring_level']}: {doc['label']}
                Description: {doc['description']}
                Year 1: {doc['year_expectations']['year_1']}
                Year 2: {doc['year_expectations']['year_2']}
                Year 3: {doc['year_expectations']['year_3']}
                Year 4: {doc['year_expectations']['year_4']}
                Year 5: {doc['year_expectations']['year_5']}
                """
                
                self.documents.append(searchable_text.strip())
                self.knowledge_base.append(doc)
        
        print(f"Loaded {len(self.documents)} documents from CSV files")
    
    def build_vector_index(self):
        """Build FAISS vector index for similarity search"""
        print("Building vector index...")
        
        # Generate embeddings for all documents
        embeddings = self.embedding_model.encode(self.documents)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.vector_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.vector_index.add(embeddings.astype('float32'))
        
        print(f"Vector index built with {self.vector_index.ntotal} documents")
    
    def retrieve_relevant_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on query
        
        Args:
            query: Search query
            top_k: Number of top documents to retrieve
            
        Returns:
            List of relevant documents with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search for similar documents
        scores, indices = self.vector_index.search(query_embedding.astype('float32'), top_k)
        
        # Return relevant documents with scores
        relevant_docs = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx != -1:  # Valid index
                relevant_docs.append({
                    'document': self.knowledge_base[idx],
                    'text': self.documents[idx],
                    'score': float(score),
                    'rank': i + 1
                })
        
        return relevant_docs
    
    def generate_question(self, 
                         dimension: str = None,
                         subcategory: str = None,
                         question_type: str = None,
                         target_year_level: str = None,
                         additional_context: str = "",
                         num_questions: int = 1) -> List[Dict[str, Any]]:
        """
        Generate new questions using RAG approach
        
        Args:
            dimension: Target dimension (creativity, teamwork, soft_skills, hard_skills)
            subcategory: Target subcategory
            question_type: Type of question to generate
            target_year_level: Target year level (1-5)
            additional_context: Additional context for question generation
            num_questions: Number of questions to generate
            
        Returns:
            List of generated questions with metadata
        """
        # Build query for context retrieval
        query_parts = []
        if dimension:
            query_parts.append(f"dimension: {dimension}")
        if subcategory:
            query_parts.append(f"subcategory: {subcategory}")
        if question_type:
            query_parts.append(f"question type: {question_type}")
        if target_year_level:
            query_parts.append(f"year level: {target_year_level}")
        if additional_context:
            query_parts.append(additional_context)
        
        query = " ".join(query_parts) if query_parts else "programming education assessment question"
        
        # Retrieve relevant context
        relevant_docs = self.retrieve_relevant_context(query, top_k=8)
        
        # Build context for LLM
        context_text = "CONTEXT FROM EXISTING QUESTION DATABASE:\n\n"
        
        for doc in relevant_docs:
            if doc['document']['type'] == 'question':
                context_text += f"Example Question (Dimension: {doc['document']['dimension']}, Subcategory: {doc['document']['subcategory']}):\n"
                context_text += f"Text: {doc['document']['question_text']}\n"
                context_text += f"Type: {doc['document']['question_type']}\n"
                context_text += f"Year Level: {doc['document']['target_year_level']}\n"
                context_text += f"Assessment Criteria: {', '.join(doc['document']['assessment_criteria'])}\n\n"
            
            elif doc['document']['type'] == 'taxonomy':
                context_text += f"Taxonomy - {doc['document']['dimension_name']}/{doc['document']['subcategory_name']}:\n"
                context_text += f"Description: {doc['document']['subcategory_description']}\n\n"
            
            elif doc['document']['type'] == 'rubric':
                context_text += f"Assessment Rubric Level {doc['document']['scoring_level']} ({doc['document']['label']}):\n"
                context_text += f"Description: {doc['document']['description']}\n"
                if target_year_level:
                    year_key = f"year_{target_year_level}"
                    if year_key in doc['document']['year_expectations']:
                        context_text += f"Year {target_year_level} Expectation: {doc['document']['year_expectations'][year_key]}\n"
                context_text += "\n"
        
        # Build prompt for question generation
        prompt = f"""You are an expert educational assessment designer specializing in programming education. Your task is to generate {num_questions} high-quality assessment question(s).

REFERENCE CONTEXT:
{context_text[:2000]}

GENERATION REQUIREMENTS:
- Primary Dimension: {dimension}
- Subcategory: {subcategory}
- Target Year Level: {target_year_level}
- Question Type: {question_type or 'Any suitable type'}
- Additional Context: {additional_context}

OUTPUT FORMAT: 
You MUST respond with ONLY a valid JSON array containing {num_questions} question object(s). No explanatory text before or after.

Each question object must contain these exact fields:
- "question_text": A detailed, clear question (minimum 50 characters)
- "question_type": One of: "collaboration_scenario", "design_task", "problem_solving", "presentation_task", "analysis_task"
- "time_limit_minutes": Integer between 10-30
- "target_year_level": "{target_year_level}"
- "dimension": "{dimension}"
- "subcategory": "{subcategory}"
- "assessment_criteria_1": String describing first assessment criterion
- "assessment_criteria_2": String describing second assessment criterion
- "assessment_criteria_3": String describing third assessment criterion
- "collaboration_indicator": One of: "low", "medium", "high"

EXAMPLE OUTPUT (generate {num_questions} like this):
[
  {{
    "question_text": "Your team is developing a React web application for a local restaurant to manage their online menu and orders. The restaurant owner wants customers to be able to browse the menu, add items to a cart, and submit orders. However, the team has discovered that the current design doesn't work well on mobile devices, and the owner has requested that the application be fully responsive. Design and explain your approach to making this application mobile-friendly while maintaining all functionality.",
    "question_type": "collaboration_scenario",
    "time_limit_minutes": 20,
    "target_year_level": "{target_year_level}",
    "dimension": "{dimension}",
    "subcategory": "{subcategory}",
    "assessment_criteria_1": "responsive_design_implementation",
    "assessment_criteria_2": "team_communication_process",
    "assessment_criteria_3": "user_experience_consideration",
    "collaboration_indicator": "medium"
  }}
]"""

        try:
            # Generate response using Gemini
            response = self.llm.generate_content(prompt)
            
            if not response or not response.text:
                print("❌ No response from LLM")
                return [{
                    'error': "No response from LLM",
                    'question_text': 'N/A',
                    'fallback': True
                }]
            
            # Parse response
            response_text = response.text.strip()
            print(f"🤖 LLM Response: {response_text[:200]}...")
            
            # Try to extract JSON from response
            questions_data = None
            
            if response_text.startswith('['):
                # Response is already JSON array
                try:
                    questions_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error for direct array: {e}")
                    questions_data = None
            
            if questions_data is None:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        questions_data = json.loads(json_match.group())
                        print("✅ Extracted JSON from response")
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error for extracted: {e}")
                        questions_data = None
            
            if questions_data is None:
                print("⚠️ Using fallback response structure")
                # Fallback: create structured response from text
                questions_data = [{
                    'question_text': response_text[:500] if len(response_text) > 10 else "Failed to generate valid question",
                    'question_type': question_type or 'generated_question',
                    'time_limit_minutes': 15,
                    'target_year_level': target_year_level or '1-3',
                    'dimension': dimension or 'creativity',
                    'subcategory': subcategory or 'innovation_problem_solving',
                    'assessment_criteria_1': 'problem_solving_approach',
                    'assessment_criteria_2': 'creativity_level',
                    'assessment_criteria_3': 'technical_accuracy',
                    'collaboration_indicator': 'medium'
                }]
            
            # Validate and clean up questions
            validated_questions = []
            for i, question in enumerate(questions_data):
                if not isinstance(question, dict):
                    print(f"⚠️ Question {i+1} is not a dict: {type(question)}")
                    continue
                    
                # Get question text and validate
                question_text = question.get('question_text', '').strip()
                if not question_text or question_text in ['', 'N/A', 'null', 'None']:
                    print(f"⚠️ Question {i+1} has empty or invalid text: '{question_text}'")
                    continue
                
                if len(question_text) < 20:  # Ensure substantial question
                    print(f"⚠️ Question {i+1} text too short: {len(question_text)} chars")
                    continue
                
                # Ensure required fields have valid values
                cleaned_question = {
                    'question_text': question_text,
                    'question_type': question.get('question_type', question_type or 'collaboration_scenario'),
                    'time_limit_minutes': int(question.get('time_limit_minutes', 15)),
                    'target_year_level': str(question.get('target_year_level', target_year_level or '1-3')),
                    'dimension': str(question.get('dimension', dimension or 'creativity')),
                    'subcategory': str(question.get('subcategory', subcategory or 'innovation_problem_solving')),
                    'assessment_criteria_1': str(question.get('assessment_criteria_1', 'problem_solving_approach')),
                    'assessment_criteria_2': str(question.get('assessment_criteria_2', 'creativity_level')),
                    'assessment_criteria_3': str(question.get('assessment_criteria_3', 'technical_accuracy')),
                    'collaboration_indicator': str(question.get('collaboration_indicator', 'medium'))
                }
                
                print(f"✅ Question {i+1} validated successfully")
                cleaned_question['generated_id'] = f"gen_{len(self.knowledge_base) + len(validated_questions) + 1:03d}"
                cleaned_question['generation_context'] = {
                    'query': query,
                    'relevant_docs_count': len(relevant_docs),
                    'top_similarity_score': relevant_docs[0]['score'] if relevant_docs else 0.0
                }
                validated_questions.append(cleaned_question)
            
            if not validated_questions:
                print(f"❌ No valid questions generated from {len(questions_data)} raw questions")
                return [{
                    'error': "No valid questions generated",
                    'question_text': 'N/A',
                    'fallback': True,
                    'raw_response': response_text[:200]
                }]
            
            print(f"✅ Generated {len(validated_questions)} valid questions")
            return validated_questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return [{
                'error': f"Failed to generate question: {str(e)}",
                'query': query,
                'context_docs_found': len(relevant_docs)
            }]
    
    def get_question_suggestions(self, partial_input: str) -> List[str]:
        """
        Get suggestions for question parameters based on existing data
        
        Args:
            partial_input: Partial input to match against
            
        Returns:
            List of suggestions
        """
        suggestions = set()
        
        for doc in self.knowledge_base:
            if doc['type'] == 'question':
                suggestions.add(doc['dimension'])
                suggestions.add(doc['subcategory'])
                suggestions.add(doc['question_type'])
            elif doc['type'] == 'taxonomy':
                suggestions.add(doc['dimension_name'])
                suggestions.add(doc['subcategory_name'])
        
        # Filter suggestions based on partial input
        if partial_input:
            filtered = [s for s in suggestions if partial_input.lower() in s.lower()]
            return sorted(filtered)
        
        return sorted(list(suggestions))
    
    def save_generated_questions(self, questions: List[Dict[str, Any]], output_file: str = "generated_questions.json"):
        """Save generated questions to file"""
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        print(f"Generated questions saved to {output_path}")


def main():
    """Example usage of the QuestionGenerationRAG system"""
    
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("Please set your GOOGLE_API_KEY environment variable")
        print("You can get a free API key from: https://makersuite.google.com/app/apikey")
        return
    
    try:
        # Initialize the RAG system
        print("Initializing Question Generation RAG system...")
        rag_system = QuestionGenerationRAG()
        
        # Example: Generate questions for creativity dimension
        print("\n" + "="*50)
        print("GENERATING QUESTIONS - CREATIVITY DIMENSION")
        print("="*50)
        
        questions = rag_system.generate_question(
            dimension="creativity",
            subcategory="innovation_problem_solving",
            question_type="collaboration_scenario",
            target_year_level="2",
            additional_context="Focus on web development projects with team dynamics",
            num_questions=2
        )
        
        print(f"\nGenerated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"\n--- Question {i} ---")
            print(f"ID: {q.get('generated_id', 'N/A')}")
            print(f"Text: {q.get('question_text', 'N/A')}")
            print(f"Type: {q.get('question_type', 'N/A')}")
            print(f"Dimension: {q.get('dimension', 'N/A')}")
            print(f"Subcategory: {q.get('subcategory', 'N/A')}")
            print(f"Year Level: {q.get('target_year_level', 'N/A')}")
            print(f"Time Limit: {q.get('time_limit_minutes', 'N/A')} minutes")
            print(f"Assessment Criteria: {q.get('assessment_criteria_1', '')}, {q.get('assessment_criteria_2', '')}, {q.get('assessment_criteria_3', '')}")
            print(f"Collaboration: {q.get('collaboration_indicator', 'N/A')}")
        
        # Save generated questions
        rag_system.save_generated_questions(questions)
        
        # Show suggestions
        print("\n" + "="*50)
        print("AVAILABLE SUGGESTIONS")
        print("="*50)
        suggestions = rag_system.get_question_suggestions("")
        print(f"Available parameters: {suggestions[:10]}...")  # Show first 10
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure you have set the GOOGLE_API_KEY environment variable and have internet access.")


if __name__ == "__main__":
    main()
