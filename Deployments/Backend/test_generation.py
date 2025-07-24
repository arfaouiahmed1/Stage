# Test the question generation endpoint
import requests
import json

# Test the dimensions endpoint
def test_dimensions():
    try:
        response = requests.get("http://localhost:8000/questions/dimensions")
        if response.status_code == 200:
            print("✅ Dimensions endpoint works:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Dimensions endpoint failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing dimensions: {e}")

# Test the subdimensions endpoint
def test_subdimensions():
    try:
        response = requests.get("http://localhost:8000/questions/subdimensions/creativity")
        if response.status_code == 200:
            print("✅ Subdimensions endpoint works:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Subdimensions endpoint failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing subdimensions: {e}")

# Test the generation endpoint
def test_generation():
    try:
        payload = {
            "dimension": "creativity",
            "subdimension": "innovation_problem_solving",
            "target_year_level": 2,
            "additional_context": "Focus on practical problem-solving scenarios",
            "idQuiz": "test_quiz_001",
            "idCategory": "test_category_001"
        }
        
        response = requests.post("http://localhost:8000/questions/generate", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Generation endpoint works:")
            print(f"Generated Question: {result['question']}")
            print(f"Dimension: {result['dimension']}")
            print(f"Subdimension: {result['subdimension']}")
            print(f"Target Year Level: {result['target_year_level']}")
            print(f"Response Scale: {result['response_scale']}")
            print(f"Saved Question ID: {result['saved_question_id']}")
        else:
            print(f"❌ Generation endpoint failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing generation: {e}")

if __name__ == "__main__":
    print("🧪 Testing Question Generation API...")
    print("\n" + "="*50)
    print("Testing /questions/dimensions")
    test_dimensions()
    
    print("\n" + "="*50)
    print("Testing /questions/subdimensions/creativity")
    test_subdimensions()
    
    print("\n" + "="*50)
    print("Testing /questions/generate")
    test_generation()
