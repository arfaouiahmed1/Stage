#!/usr/bin/env python3
"""Test script to verify storage functionality"""

from shared_storage import QuizStorage
import json

def test_storage():
    print("🧪 Testing storage functionality...")
    
    try:
        # Initialize storage
        storage = QuizStorage()
        print("✅ Storage initialized successfully")
        
        # Test saving a quiz
        test_quiz_data = [
            {
                "question_id": "test_001",
                "dimension": "creativity",
                "subdimension": "innovation",
                "question_text": "I often come up with creative solutions to problems",
                "target_year_level": 12,
                "response_scale": "1-5"
            }
        ]
        
        quiz_id = storage.save_quiz(test_quiz_data, "Test Quiz")
        print(f"✅ Quiz saved successfully with ID: {quiz_id}")
        
        # Test loading quizzes
        quizzes = storage.get_all_quizzes()
        print(f"✅ Loaded {len(quizzes)} quizzes")
        
        # Test saving responses
        test_responses = {
            "test_001": 4
        }
        test_scores = {
            "creativity": 4.0
        }
        
        storage.save_responses(quiz_id, "Test Student", test_responses, test_scores)
        print("✅ Responses saved successfully")
        
        # Test loading responses
        responses = storage.get_responses_for_quiz(quiz_id)
        print(f"✅ Loaded {len(responses)} responses")
        
        print("\n🎉 All tests passed! Storage is working correctly.")
        
        # Show what was saved
        print("\n📊 Storage contents:")
        print(f"Quizzes: {len(quizzes)}")
        print(f"Responses: {len(responses)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_storage()
