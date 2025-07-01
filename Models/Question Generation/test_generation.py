#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from question_generation_rag import QuestionGenerationRAG

def test_question_generation():
    """Test the question generation system with simple parameters"""
    
    print("🔍 Testing Question Generation System...")
    
    # Check API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not set")
        return False
    
    try:
        # Initialize RAG system
        print("📦 Initializing RAG system...")
        rag = QuestionGenerationRAG()
        
        # Test simple generation
        print("🧪 Testing question generation...")
        questions = rag.generate_question(
            dimension="creativity",
            subcategory="innovation_problem_solving",
            target_year_level="2",
            additional_context="Simple web development project",
            num_questions=1
        )
        
        print(f"📊 Generated {len(questions)} questions")
        
        # Check results
        for i, q in enumerate(questions, 1):
            print(f"\n--- Question {i} ---")
            print(f"Question Text: {q.get('question_text', 'MISSING')[:100]}...")
            print(f"Type: {q.get('question_type', 'MISSING')}")
            print(f"Dimension: {q.get('dimension', 'MISSING')}")
            print(f"Has Error: {'error' in q}")
            
            if 'error' in q:
                print(f"Error: {q['error']}")
                return False
            
            if not q.get('question_text') or len(q.get('question_text', '')) < 10:
                print("❌ Question text is too short or missing")
                return False
        
        print("✅ Question generation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_question_generation()
    sys.exit(0 if success else 1)
