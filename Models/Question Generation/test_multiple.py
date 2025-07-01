#!/usr/bin/env python3
"""
Test multiple question generation
"""

from question_generation_rag import QuestionGenerationRAG
import os

def test_multiple_questions():
    """Test generating multiple questions"""
    print("🔍 Testing Multiple Question Generation...")
    
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Please set your GOOGLE_API_KEY environment variable")
        return False
    
    try:
        print("📦 Initializing RAG system...")
        rag_system = QuestionGenerationRAG()
        
        print("🧪 Testing multiple question generation...")
        questions = rag_system.generate_question(
            dimension="creativity",
            subcategory="innovation_problem_solving",
            question_type=None,  # Auto-select
            target_year_level="2-3",
            additional_context="Focus on web development and user experience",
            num_questions=3  # Generate 3 questions
        )
        
        print(f"📊 Generated {len(questions)} questions")
        
        valid_count = 0
        for i, q in enumerate(questions, 1):
            print(f"\n--- Question {i} ---")
            question_text = q.get('question_text', '')
            has_error = q.get('error') or q.get('fallback')
            
            if has_error:
                print(f"❌ Question {i} has error: {q.get('error', 'Unknown error')}")
            elif question_text and len(question_text) > 20:
                print(f"✅ Question Text: {question_text[:100]}...")
                print(f"   Type: {q.get('question_type', 'N/A')}")
                print(f"   Dimension: {q.get('dimension', 'N/A')}")
                valid_count += 1
            else:
                print(f"❌ Question {i} has invalid text: '{question_text}'")
        
        if valid_count > 0:
            print(f"✅ Multiple question generation test passed! ({valid_count}/{len(questions)} valid)")
            return True
        else:
            print("❌ No valid questions generated")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    test_multiple_questions()
