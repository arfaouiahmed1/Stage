# Test enhanced question generation with different dimensions
import requests
import json

def test_multiple_generations():
    """Test generation across different dimensions and subdimensions"""
    
    test_cases = [
        {
            "dimension": "creativity",
            "subdimension": "innovation_problem_solving",
            "target_year_level": 2,
            "additional_context": "Focus on collaborative brainstorming techniques"
        },
        {
            "dimension": "soft_skills",
            "subdimension": "presentation_communication",
            "target_year_level": 2,
            "additional_context": "Emphasize presentation and public speaking skills"
        },
        {
            "dimension": "creativity",
            "subdimension": "ux_design",
            "target_year_level": 1,
            "additional_context": "Focus on user empathy and design thinking"
        },
        {
            "dimension": "teamwork",
            "subdimension": "communication_documentation",
            "target_year_level": 2,
            "additional_context": "Emphasize cross-functional team dynamics"
        },
        {
            "dimension": "soft_skills",
            "subdimension": "critical_thinking",
            "target_year_level": 3,
            "additional_context": "Focus on analytical problem-solving approaches"
        }
    ]
    
    print("🧪 Testing Enhanced Question Generation Variability...")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔸 Test Case {i}: {test_case['dimension']} - {test_case['subdimension']}")
        print(f"   Year Level: {test_case['target_year_level']}")
        print(f"   Context: {test_case['additional_context']}")
        
        try:
            payload = {
                **test_case,
                "idQuiz": f"test_quiz_{i:03d}",
                "idCategory": f"test_category_{i:03d}"
            }
            
            response = requests.post("http://localhost:8000/questions/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Generated Question:")
                print(f"      \"{result['question']}\"")
                print(f"   📝 Question ID: {result['saved_question_id']}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ Enhanced generation testing completed!")

if __name__ == "__main__":
    test_multiple_generations()
