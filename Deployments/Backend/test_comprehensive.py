# Unified comprehensive test for the enhanced LLM Question Generation System
import requests
import json
import time

def test_comprehensive_system():
    """Comprehensive test covering all aspects of the LLM question generation system"""
    
    print("🧪 COMPREHENSIVE LLM QUESTION GENERATION SYSTEM TEST")
    print("="*80)
    
    # Test results tracking
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    def log_test(test_name, success, details=""):
        results["total_tests"] += 1
        if success:
            results["passed"] += 1
            print(f"   ✅ {test_name}")
            if details:
                print(f"      {details}")
        else:
            results["failed"] += 1
            results["errors"].append(f"{test_name}: {details}")
            print(f"   ❌ {test_name}")
            print(f"      {details}")
    
    # PHASE 1: Setup - Create test data
    print(f"\n📋 PHASE 1: SETUP AND DATA CREATION")
    print("-" * 50)
    
    # Create test category
    print("🔸 Creating test category...")
    category_payload = {
        "island": "creativity", 
        "subcategories": ["innovation_problem_solving", "artistic_expression"]
    }
    
    try:
        response = requests.post("http://localhost:8000/categories/", json=category_payload)
        if response.status_code == 200:
            test_category = response.json()
            category_id = test_category['idCategory']
            log_test("Category Creation", True, f"ID: {category_id}")
        else:
            log_test("Category Creation", False, f"Status: {response.status_code}")
            return results
    except Exception as e:
        log_test("Category Creation", False, f"Error: {e}")
        return results
    
    # Create test quiz
    print("🔸 Creating test quiz...")
    from datetime import datetime
    quiz_payload = {
        "idTeacher": "test_teacher_001",
        "idCategory": [category_id, category_id, category_id, category_id],  # Quiz schema requires exactly 4 categories
        "dateCreation": datetime.now().isoformat(),
        "isAccessible": True,
        "accessCode": "TEST123",
        "nameQuiz": "Comprehensive Test Quiz"
    }
    
    quiz_id = None
    try:
        response = requests.post("http://localhost:8000/quizzes/", json=quiz_payload)
        if response.status_code == 200:
            test_quiz = response.json()
            quiz_id = test_quiz['idQuiz']
            log_test("Quiz Creation", True, f"ID: {quiz_id}")
        else:
            log_test("Quiz Creation", False, f"Status: {response.status_code}, Response: {response.text}")
            # Try to get an existing quiz instead
            print("🔸 Attempting to get existing quiz...")
            try:
                response = requests.get("http://localhost:8000/quizzes/")
                if response.status_code == 200:
                    quizzes = response.json()
                    if quizzes:
                        quiz_id = quizzes[0]['idQuiz']
                        log_test("Quiz Creation (Using Existing)", True, f"Using existing quiz ID: {quiz_id}")
                    else:
                        log_test("Quiz Creation (No Quizzes Found)", False, "No existing quizzes available")
                        return results
                else:
                    log_test("Quiz Creation (Fallback Failed)", False, f"Cannot get existing quizzes: {response.status_code}")
                    return results
            except Exception as e:
                log_test("Quiz Creation (Fallback Error)", False, f"Error getting existing quizzes: {e}")
                return results
    except Exception as e:
        log_test("Quiz Creation", False, f"Error: {e}")
        # Try to get an existing quiz
        print("🔸 Attempting to get existing quiz due to creation error...")
        try:
            response = requests.get("http://localhost:8000/quizzes/")
            if response.status_code == 200:
                quizzes = response.json()
                if quizzes:
                    quiz_id = quizzes[0]['idQuiz']
                    log_test("Quiz Creation (Using Existing After Error)", True, f"Using existing quiz ID: {quiz_id}")
                else:
                    log_test("Quiz Creation (No Quizzes Found After Error)", False, "No existing quizzes available")
                    return results
            else:
                log_test("Quiz Creation (Fallback Failed After Error)", False, f"Cannot get existing quizzes: {response.status_code}")
                return results
        except Exception as e2:
            log_test("Quiz Creation (Fallback Error After Error)", False, f"Error getting existing quizzes: {e2}")
            return results
    
    if not quiz_id:
        log_test("Quiz ID Resolution", False, "Could not obtain valid quiz ID")
        return results
    
    # PHASE 2: Test dimension and subdimension endpoints
    print(f"\n📋 PHASE 2: DIMENSION & SUBDIMENSION ENDPOINTS")
    print("-" * 50)
    
    # Test dimensions endpoint
    print("🔸 Testing dimensions endpoint...")
    try:
        response = requests.get("http://localhost:8000/questions/dimensions")
        if response.status_code == 200:
            dimensions_data = response.json()
            dimensions = dimensions_data.get("dimensions", [])
            log_test("Dimensions Endpoint", True, f"Found {len(dimensions)} dimensions: {dimensions}")
        else:
            log_test("Dimensions Endpoint", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Dimensions Endpoint", False, f"Error: {e}")
    
    # Test subdimensions endpoint
    print("🔸 Testing subdimensions endpoint...")
    try:
        response = requests.get("http://localhost:8000/questions/subdimensions/creativity")
        if response.status_code == 200:
            subdims_data = response.json()
            subdimensions = subdims_data.get("subdimensions", [])
            log_test("Subdimensions Endpoint", True, f"Found {len(subdimensions)} subdimensions: {subdimensions}")
        else:
            log_test("Subdimensions Endpoint", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Subdimensions Endpoint", False, f"Error: {e}")
    
    # PHASE 3: Test question generation scenarios
    print(f"\n📋 PHASE 3: QUESTION GENERATION SCENARIOS")
    print("-" * 50)
    
    test_scenarios = [
        {
            "name": "Auto-detect from Category (No Subdimension)",
            "payload": {
                "idQuiz": quiz_id,
                "idCategory": category_id,
                "target_year_level": 2
            },
            "description": "System should auto-detect dimension and subdimension from category"
        },
        {
            "name": "Specific Existing Subdimension",
            "payload": {
                "idQuiz": quiz_id,
                "idCategory": category_id,
                "subdimension": "innovation_problem_solving",
                "target_year_level": 1
            },
            "description": "Generate with existing subdimension from dataset"
        },
        {
            "name": "Custom Subdimension",
            "payload": {
                "idQuiz": quiz_id,
                "idCategory": category_id,
                "subdimension": "musical_creativity",
                "target_year_level": 3
            },
            "description": "Generate with teacher-created custom subdimension"
        },
        {
            "name": "Different Year Level",
            "payload": {
                "idQuiz": quiz_id,
                "idCategory": category_id,
                "subdimension": "artistic_expression",
                "target_year_level": 2
            },
            "description": "Test with different complexity level"
        }
    ]
    
    generated_questions = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🔸 Scenario {i}: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        
        try:
            response = requests.post("http://localhost:8000/questions/generate", json=scenario['payload'])
            
            if response.status_code == 200:
                result = response.json()
                question = result["question"]
                metadata = result["generation_metadata"]
                
                # Validate response structure
                required_fields = ["idQuestion", "content", "idQuiz", "idCategory"]
                missing_fields = [field for field in required_fields if field not in question]
                
                if not missing_fields:
                    log_test(f"Generation - {scenario['name']}", True, 
                            f"Question: \"{question['content'][:50]}...\"")
                    
                    generated_questions.append({
                        "scenario": scenario['name'],
                        "question": question,
                        "metadata": metadata
                    })
                    
                    # Additional validations
                    if question['idQuiz'] == quiz_id:
                        log_test(f"Quiz ID Validation - {scenario['name']}", True)
                    else:
                        log_test(f"Quiz ID Validation - {scenario['name']}", False, 
                                f"Expected: {quiz_id}, Got: {question['idQuiz']}")
                    
                    if question['idCategory'] == category_id:
                        log_test(f"Category ID Validation - {scenario['name']}", True)
                    else:
                        log_test(f"Category ID Validation - {scenario['name']}", False,
                                f"Expected: {category_id}, Got: {question['idCategory']}")
                    
                    # Check if it's a proper Likert scale question
                    content = question['content']
                    likert_patterns = ["I am", "I can", "I feel", "I have", "I consistently", "I effectively"]
                    is_likert = any(content.startswith(pattern) for pattern in likert_patterns)
                    
                    log_test(f"Likert Scale Format - {scenario['name']}", is_likert,
                            "Question follows proper first-person format" if is_likert else "Question format needs improvement")
                    
                else:
                    log_test(f"Generation - {scenario['name']}", False, 
                            f"Missing fields: {missing_fields}")
            else:
                log_test(f"Generation - {scenario['name']}", False, 
                        f"Status: {response.status_code}, Error: {response.text}")
                
        except Exception as e:
            log_test(f"Generation - {scenario['name']}", False, f"Error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    # PHASE 4: Test database integration
    print(f"\n📋 PHASE 4: DATABASE INTEGRATION")
    print("-" * 50)
    
    if generated_questions:
        # Test retrieving a generated question
        first_question = generated_questions[0]["question"]
        question_id = first_question["idQuestion"]
        
        print(f"🔸 Testing question retrieval...")
        try:
            response = requests.get(f"http://localhost:8000/questions/{question_id}")
            if response.status_code == 200:
                retrieved_question = response.json()
                if retrieved_question["content"] == first_question["content"]:
                    log_test("Question Retrieval", True, f"Successfully retrieved question {question_id}")
                else:
                    log_test("Question Retrieval", False, "Content mismatch")
            else:
                log_test("Question Retrieval", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Question Retrieval", False, f"Error: {e}")
        
        # Test questions by quiz
        print(f"🔸 Testing questions by quiz...")
        try:
            response = requests.get(f"http://localhost:8000/questions/by_quiz/{quiz_id}")
            if response.status_code == 200:
                quiz_questions = response.json()
                log_test("Questions by Quiz", True, f"Found {len(quiz_questions)} questions for quiz")
            else:
                log_test("Questions by Quiz", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Questions by Quiz", False, f"Error: {e}")
    
    # PHASE 5: Test category updates
    print(f"\n📋 PHASE 5: CATEGORY AUTO-UPDATE")
    print("-" * 50)
    
    print(f"🔸 Checking if category was updated with new subdimensions...")
    try:
        response = requests.get(f"http://localhost:8000/categories/{category_id}")
        if response.status_code == 200:
            updated_category = response.json()
            subcategories = updated_category.get("subcategories", [])
            
            # Check if custom subdimensions were added
            custom_subdims = ["musical_creativity", "artistic_expression"]
            added_customs = [sub for sub in custom_subdims if sub in subcategories]
            
            if added_customs:
                log_test("Category Auto-Update", True, f"Added custom subdimensions: {added_customs}")
            else:
                log_test("Category Auto-Update", False, "No custom subdimensions were added")
                
            log_test("Final Category State", True, f"Subcategories: {subcategories}")
        else:
            log_test("Category Auto-Update", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Category Auto-Update", False, f"Error: {e}")
    
    # FINAL RESULTS
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
    
    if results['errors']:
        print(f"\n❌ FAILED TESTS:")
        for error in results['errors']:
            print(f"   • {error}")
    
    if generated_questions:
        print(f"\n📝 GENERATED QUESTIONS SAMPLE:")
        for i, item in enumerate(generated_questions[:2], 1):  # Show first 2
            print(f"   {i}. {item['scenario']}")
            print(f"      \"{item['question']['content']}\"")
            print(f"      Dimension: {item['metadata']['dimension']}")
            print(f"      Subdimension: {item['metadata']['subdimension']}")
    
    print(f"\n🎉 COMPREHENSIVE TEST COMPLETED!")
    return results

if __name__ == "__main__":
    test_comprehensive_system()
