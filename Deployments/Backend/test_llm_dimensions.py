# LLM Dimension-Specific Output Quality Test
import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any

def test_llm_dimensions():
    """Comprehensive test for LLM output quality across all dimensions"""
    
    print("🧪 LLM DIMENSION-SPECIFIC OUTPUT QUALITY TEST")
    print("="*80)
    
    # Test results tracking
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": [],
        "dimension_results": {},
        "generated_questions": []
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
    
    def validate_likert_question(question_text: str) -> Dict[str, Any]:
        """Validate if a question follows proper Likert scale format"""
        validation_results = {
            "is_valid": True,
            "issues": [],
            "score": 0,
            "detailed_checks": {}
        }
        
        # Check 1: Starts with first-person statement
        first_person_patterns = ["I am", "I can", "I feel", "I have", "I consistently", "I effectively", "I demonstrate", "I possess", "I exhibit"]
        starts_correctly = any(question_text.strip().startswith(pattern) for pattern in first_person_patterns)
        
        validation_results["detailed_checks"]["first_person"] = {
            "passed": starts_correctly,
            "expected": "Should start with first-person statement",
            "found": question_text[:20] if len(question_text) > 20 else question_text
        }
        
        if starts_correctly:
            validation_results["score"] += 25
        else:
            validation_results["issues"].append("Does not start with first-person statement")
            validation_results["is_valid"] = False
        
        # Check 2: Appropriate length (not too short or too long)
        length = len(question_text)
        length_appropriate = 25 <= length <= 120  # More reasonable range
        
        validation_results["detailed_checks"]["length"] = {
            "passed": length_appropriate,
            "expected": "25-120 characters",
            "found": f"{length} characters"
        }
        
        if length_appropriate:
            validation_results["score"] += 20
        else:
            validation_results["issues"].append(f"Inappropriate length: {length} characters (should be 25-120)")
            if length < 25:
                validation_results["is_valid"] = False
        
        # Check 3: Ends with period (proper punctuation)
        ends_properly = question_text.strip().endswith('.')
        
        validation_results["detailed_checks"]["punctuation"] = {
            "passed": ends_properly,
            "expected": "Should end with period",
            "found": f"Ends with '{question_text.strip()[-1]}'" if question_text.strip() else "Empty"
        }
        
        if ends_properly:
            validation_results["score"] += 15
        else:
            validation_results["issues"].append("Does not end with proper punctuation")
        
        # Check 4: No question marks (should be statement, not question)
        has_question_marks = '?' in question_text
        
        validation_results["detailed_checks"]["statement_format"] = {
            "passed": not has_question_marks,
            "expected": "Should be statement, not question",
            "found": "Contains question marks" if has_question_marks else "Statement format"
        }
        
        if not has_question_marks:
            validation_results["score"] += 15
        else:
            validation_results["issues"].append("Contains question marks (should be a statement)")
        
        # Check 5: Contains meaningful content (not generic)
        generic_patterns = ["something", "anything", "things", "stuff", "various", "certain", "some"]
        generic_found = [pattern for pattern in generic_patterns if pattern in question_text.lower()]
        is_specific = len(generic_found) == 0
        
        validation_results["detailed_checks"]["specificity"] = {
            "passed": is_specific,
            "expected": "Should avoid generic language",
            "found": f"Generic words: {generic_found}" if generic_found else "Specific language"
        }
        
        if is_specific:
            validation_results["score"] += 15
        else:
            validation_results["issues"].append(f"Contains generic/vague language: {', '.join(generic_found)}")
        
        # Check 6: Professional/Academic tone
        professional_indicators = ["ability", "capacity", "skill", "competence", "proficiency", "effectiveness"]
        unprofessional_indicators = ["awesome", "cool", "super", "totally", "really good"]
        
        has_professional = any(indicator in question_text.lower() for indicator in professional_indicators)
        has_unprofessional = any(indicator in question_text.lower() for indicator in unprofessional_indicators)
        
        validation_results["detailed_checks"]["professional_tone"] = {
            "passed": has_professional and not has_unprofessional,
            "expected": "Professional/academic language",
            "found": "Professional tone" if has_professional and not has_unprofessional else "Informal tone"
        }
        
        if has_professional and not has_unprofessional:
            validation_results["score"] += 10
        elif has_unprofessional:
            validation_results["issues"].append("Uses unprofessional language")
        
        return validation_results
    
    def assess_dimension_relevance(question_text: str, dimension: str, subdimension: str) -> Dict[str, Any]:
        """Assess how well the question relates to the specific dimension/subdimension"""
        relevance_results = {
            "is_relevant": True,
            "confidence": 0,
            "keywords_found": [],
            "detailed_analysis": {},
            "semantic_score": 0
        }
        
        # Define enhanced dimension-specific keywords with weights
        dimension_keywords = {
            "creativity": {
                "innovation_problem_solving": {
                    "primary": ["creative", "innovative", "original", "novel", "brainstorm", "invention"],
                    "secondary": ["solution", "problem", "idea", "approach", "method", "strategy"],
                    "context": ["thinking", "design", "development", "generation", "exploration"]
                },
                "algorithm_design": {
                    "primary": ["algorithm", "computational", "logic", "optimization", "efficiency"],
                    "secondary": ["design", "structure", "pattern", "sequence", "process"],
                    "context": ["programming", "coding", "development", "implementation", "analysis"]
                },
                "system_architecture": {
                    "primary": ["architecture", "system", "structure", "framework", "infrastructure"],
                    "secondary": ["design", "scalable", "maintainable", "modular", "organized"],
                    "context": ["planning", "engineering", "development", "integration", "management"]
                },
                "ux_design": {
                    "primary": ["user", "experience", "interface", "usability", "accessibility"],
                    "secondary": ["design", "intuitive", "interaction", "visual", "functional"],
                    "context": ["research", "testing", "prototyping", "feedback", "iteration"]
                }
            },
            "teamwork": {
                "communication_documentation": {
                    "primary": ["communicate", "document", "explain", "clarity", "articulate"],
                    "secondary": ["write", "share", "convey", "express", "present"],
                    "context": ["collaboration", "team", "project", "information", "knowledge"]
                },
                "code_review_collaboration": {
                    "primary": ["review", "feedback", "critique", "evaluate", "assess"],
                    "secondary": ["code", "quality", "standards", "practices", "improvement"],
                    "context": ["collaboration", "mentoring", "learning", "sharing", "discussion"]
                },
                "conflict_resolution": {
                    "primary": ["conflict", "resolution", "mediation", "negotiation", "consensus"],
                    "secondary": ["disagreement", "dispute", "balance", "compromise", "harmony"],
                    "context": ["team", "interpersonal", "communication", "leadership", "diplomacy"]
                },
                "leadership_mentoring": {
                    "primary": ["lead", "mentor", "guide", "coach", "influence"],
                    "secondary": ["support", "empower", "develop", "inspire", "motivate"],
                    "context": ["team", "growth", "development", "guidance", "responsibility"]
                },
                "agile_participation": {
                    "primary": ["agile", "scrum", "sprint", "iterative", "adaptive"],
                    "secondary": ["planning", "retrospective", "standup", "collaboration", "flexibility"],
                    "context": ["team", "process", "methodology", "improvement", "delivery"]
                }
            },
            "soft_skills": {
                "time_management": {
                    "primary": ["time", "schedule", "prioritize", "deadline", "organize"],
                    "secondary": ["manage", "plan", "efficient", "productive", "balance"],
                    "context": ["work", "tasks", "projects", "goals", "productivity"]
                },
                "critical_thinking": {
                    "primary": ["analyze", "evaluate", "reason", "logic", "assess"],
                    "secondary": ["think", "examine", "investigate", "question", "judge"],
                    "context": ["problem", "decision", "solution", "evidence", "conclusion"]
                },
                "adaptability_learning": {
                    "primary": ["adapt", "flexible", "adjust", "evolve", "grow"],
                    "secondary": ["learn", "change", "develop", "improve", "acquire"],
                    "context": ["new", "challenge", "skill", "knowledge", "environment"]
                },
                "presentation_communication": {
                    "primary": ["present", "communicate", "speak", "convey", "articulate"],
                    "secondary": ["audience", "message", "delivery", "engagement", "clarity"],
                    "context": ["public", "group", "formal", "professional", "effective"]
                }
            },
            "hard_skills": {
                "programming_languages": {
                    "primary": ["program", "code", "language", "syntax", "development"],
                    "secondary": ["implement", "software", "application", "algorithm", "function"],
                    "context": ["technical", "skill", "proficiency", "expertise", "competency"]
                },
                "database_management": {
                    "primary": ["database", "data", "SQL", "query", "schema"],
                    "secondary": ["storage", "retrieval", "integrity", "optimization", "design"],
                    "context": ["management", "administration", "analysis", "modeling", "security"]
                },
                "devops_deployment": {
                    "primary": ["deploy", "devops", "automation", "pipeline", "infrastructure"],
                    "secondary": ["environment", "configuration", "monitoring", "scaling", "maintenance"],
                    "context": ["operation", "production", "system", "process", "management"]
                },
                "testing_qa": {
                    "primary": ["test", "quality", "debug", "validate", "verify"],
                    "secondary": ["assurance", "bug", "error", "defect", "reliability"],
                    "context": ["software", "system", "application", "process", "standard"]
                }
            }
        }
        
        # Get relevant keywords for the dimension/subdimension
        keywords_data = {}
        if dimension in dimension_keywords:
            if subdimension in dimension_keywords[dimension]:
                keywords_data = dimension_keywords[dimension][subdimension]
            else:
                # For custom subdimensions, combine all keywords from the dimension
                combined_keywords = {"primary": [], "secondary": [], "context": []}
                for subdim_data in dimension_keywords[dimension].values():
                    for category, words in subdim_data.items():
                        combined_keywords[category].extend(words)
                keywords_data = combined_keywords
        
        # Analyze keyword matches with weights
        question_lower = question_text.lower()
        
        primary_matches = []
        secondary_matches = []
        context_matches = []
        
        if keywords_data:
            primary_matches = [kw for kw in keywords_data.get("primary", []) if kw in question_lower]
            secondary_matches = [kw for kw in keywords_data.get("secondary", []) if kw in question_lower]
            context_matches = [kw for kw in keywords_data.get("context", []) if kw in question_lower]
        
        # Calculate weighted relevance score
        primary_weight = 3.0
        secondary_weight = 2.0
        context_weight = 1.0
        
        primary_score = len(primary_matches) * primary_weight
        secondary_score = len(secondary_matches) * secondary_weight
        context_score = len(context_matches) * context_weight
        
        total_possible = len(keywords_data.get("primary", [])) * primary_weight + \
                        len(keywords_data.get("secondary", [])) * secondary_weight + \
                        len(keywords_data.get("context", [])) * context_weight
        
        if total_possible > 0:
            relevance_results["confidence"] = ((primary_score + secondary_score + context_score) / total_possible) * 100
        
        # Semantic analysis - check for dimension-specific concepts
        semantic_indicators = {
            "creativity": ["creative", "innovative", "original", "artistic", "imaginative", "inventive"],
            "teamwork": ["collaborate", "team", "group", "together", "shared", "collective"],
            "soft_skills": ["personal", "interpersonal", "professional", "skill", "ability", "competency"],
            "hard_skills": ["technical", "programming", "database", "system", "tool", "technology"]
        }
        
        semantic_matches = [indicator for indicator in semantic_indicators.get(dimension, []) if indicator in question_lower]
        relevance_results["semantic_score"] = (len(semantic_matches) / len(semantic_indicators.get(dimension, [1]))) * 100
        
        # Combine all found keywords
        all_keywords = primary_matches + secondary_matches + context_matches
        relevance_results["keywords_found"] = list(set(all_keywords))  # Remove duplicates
        
        # Detailed analysis
        relevance_results["detailed_analysis"] = {
            "primary_keywords": {"found": primary_matches, "score": primary_score},
            "secondary_keywords": {"found": secondary_matches, "score": secondary_score},
            "context_keywords": {"found": context_matches, "score": context_score},
            "semantic_indicators": {"found": semantic_matches, "score": relevance_results["semantic_score"]},
            "total_relevance_score": relevance_results["confidence"]
        }
        
        # Consider relevant if confidence > 20% OR semantic score > 30% OR has primary keywords
        relevance_results["is_relevant"] = (
            relevance_results["confidence"] > 20 or 
            relevance_results["semantic_score"] > 30 or 
            len(primary_matches) > 0
        )
        
        return relevance_results
    
    # PHASE 1: Setup - Get or create test resources
    print(f"\n📋 PHASE 1: SETUP")
    print("-" * 50)
    
    # Get existing quiz for testing
    quiz_id = None
    category_id = None
    
    try:
        response = requests.get("http://localhost:8000/quizzes/")
        if response.status_code == 200:
            quizzes = response.json()
            if quizzes:
                quiz_id = quizzes[0]['idQuiz']
                # Get the first category from the quiz
                if 'idCategory' in quizzes[0] and quizzes[0]['idCategory']:
                    category_id = quizzes[0]['idCategory'][0] if isinstance(quizzes[0]['idCategory'], list) else quizzes[0]['idCategory']
                log_test("Quiz Setup", True, f"Using existing quiz ID: {quiz_id}")
            else:
                log_test("Quiz Setup", False, "No existing quizzes found")
                return results
        else:
            log_test("Quiz Setup", False, f"Cannot get quizzes: {response.status_code}")
            return results
    except Exception as e:
        log_test("Quiz Setup", False, f"Error getting quizzes: {e}")
        return results
    
    # Get or create a category if needed
    if not category_id:
        try:
            response = requests.get("http://localhost:8000/categories/")
            if response.status_code == 200:
                categories = response.json()
                if categories:
                    category_id = categories[0]['idCategory']
                    log_test("Category Setup", True, f"Using existing category ID: {category_id}")
                else:
                    # Create a test category
                    category_payload = {
                        "island": "creativity", 
                        "subcategories": ["innovation_problem_solving", "artistic_expression"]
                    }
                    response = requests.post("http://localhost:8000/categories/", json=category_payload)
                    if response.status_code == 200:
                        test_category = response.json()
                        category_id = test_category['idCategory']
                        log_test("Category Creation", True, f"Created category ID: {category_id}")
                    else:
                        log_test("Category Creation", False, f"Status: {response.status_code}")
                        return results
            else:
                log_test("Category Setup", False, f"Cannot get categories: {response.status_code}")
                return results
        except Exception as e:
            log_test("Category Setup", False, f"Error with categories: {e}")
            return results
    
    # PHASE 2: Test each dimension with multiple subdimensions
    print(f"\n📋 PHASE 2: DIMENSION-SPECIFIC LLM OUTPUT TESTING")
    print("-" * 50)
    
    # Define comprehensive test scenarios for each dimension
    test_scenarios = [
        # CREATIVITY Dimension
        {
            "dimension": "creativity",
            "subdimension": "innovation_problem_solving", 
            "description": "Creative problem-solving and innovative thinking",
            "expected_themes": ["creative solutions", "innovative approaches", "problem-solving"]
        },
        {
            "dimension": "creativity",
            "subdimension": "algorithm_design",
            "description": "Creative algorithm design and optimization",
            "expected_themes": ["algorithm design", "optimization", "computational thinking"]
        },
        {
            "dimension": "creativity",
            "subdimension": "system_architecture",
            "description": "Creative system design and architecture",
            "expected_themes": ["system design", "architecture", "scalability"]
        },
        {
            "dimension": "creativity",
            "subdimension": "ux_design",
            "description": "User experience and interface design creativity",
            "expected_themes": ["user experience", "interface design", "usability"]
        },
        {
            "dimension": "creativity",
            "subdimension": "artistic_coding",  # Custom subdimension
            "description": "Custom: Creative coding and digital art",
            "expected_themes": ["creative expression", "artistic", "innovative"]
        },
        
        # TEAMWORK Dimension  
        {
            "dimension": "teamwork",
            "subdimension": "communication_documentation",
            "description": "Team communication and documentation skills",
            "expected_themes": ["communication", "documentation", "collaboration"]
        },
        {
            "dimension": "teamwork",
            "subdimension": "code_review_collaboration",
            "description": "Collaborative code review and feedback",
            "expected_themes": ["code review", "feedback", "collaboration"]
        },
        {
            "dimension": "teamwork",
            "subdimension": "conflict_resolution",
            "description": "Team conflict resolution and mediation",
            "expected_themes": ["conflict resolution", "mediation", "consensus"]
        },
        {
            "dimension": "teamwork",
            "subdimension": "leadership_mentoring",
            "description": "Team leadership and mentoring abilities",
            "expected_themes": ["leadership", "mentoring", "guidance"]
        },
        {
            "dimension": "teamwork",
            "subdimension": "remote_collaboration",  # Custom subdimension
            "description": "Custom: Remote team collaboration skills",
            "expected_themes": ["collaboration", "teamwork", "communication"]
        },
        
        # SOFT_SKILLS Dimension
        {
            "dimension": "soft_skills",
            "subdimension": "time_management",
            "description": "Personal time management and organization",
            "expected_themes": ["time management", "organization", "prioritization"]
        },
        {
            "dimension": "soft_skills",
            "subdimension": "critical_thinking",
            "description": "Analytical and critical thinking abilities",
            "expected_themes": ["critical thinking", "analysis", "reasoning"]
        },
        {
            "dimension": "soft_skills",
            "subdimension": "adaptability_learning",
            "description": "Learning agility and adaptability",
            "expected_themes": ["adaptability", "learning", "flexibility"]
        },
        {
            "dimension": "soft_skills",
            "subdimension": "presentation_communication",
            "description": "Presentation and communication skills",
            "expected_themes": ["presentation", "communication", "public speaking"]
        },
        {
            "dimension": "soft_skills",
            "subdimension": "emotional_intelligence",  # Custom subdimension
            "description": "Custom: Emotional intelligence and self-awareness",
            "expected_themes": ["emotional", "self-awareness", "interpersonal"]
        },
        
        # HARD_SKILLS Dimension
        {
            "dimension": "hard_skills",
            "subdimension": "programming_languages",
            "description": "Programming language proficiency",
            "expected_themes": ["programming", "coding", "languages"]
        },
        {
            "dimension": "hard_skills",
            "subdimension": "database_management",
            "description": "Database design and management",
            "expected_themes": ["database", "data management", "SQL"]
        },
        {
            "dimension": "hard_skills",
            "subdimension": "devops_deployment",
            "description": "DevOps and deployment automation",
            "expected_themes": ["devops", "deployment", "automation"]
        },
        {
            "dimension": "hard_skills",
            "subdimension": "testing_qa",
            "description": "Software testing and quality assurance",
            "expected_themes": ["testing", "quality assurance", "debugging"]
        },
        {
            "dimension": "hard_skills",
            "subdimension": "cybersecurity",  # Custom subdimension
            "description": "Custom: Cybersecurity and information security",
            "expected_themes": ["security", "protection", "technical"]
        }
    ]
    
    # Track results per dimension
    for dimension in ["creativity", "teamwork", "soft_skills", "hard_skills"]:
        results["dimension_results"][dimension] = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "questions_generated": [],
            "average_quality_score": 0,
            "average_relevance_score": 0
        }
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        dimension = scenario["dimension"]
        subdimension = scenario["subdimension"]
        
        print(f"\n🔸 Test {i}: {dimension.upper()} - {subdimension}")
        print(f"   Description: {scenario['description']}")
        
        # Test with different year levels
        for year_level in [1, 2, 3]:
            test_name = f"{dimension}_{subdimension}_year_{year_level}"
            
            payload = {
                "idQuiz": quiz_id,
                "idCategory": category_id,
                "subdimension": subdimension,
                "target_year_level": year_level
            }
            
            try:
                response = requests.post("http://localhost:8000/questions/generate", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    question_data = result["question"]
                    metadata = result["generation_metadata"]
                    question_text = question_data["content"]
                    
                    # Track in dimension results
                    results["dimension_results"][dimension]["total_tests"] += 1
                    results["dimension_results"][dimension]["questions_generated"].append({
                        "subdimension": subdimension,
                        "year_level": year_level,
                        "question": question_text,
                        "metadata": metadata
                    })
                    
                    # Validate Likert scale format
                    likert_validation = validate_likert_question(question_text)
                    if likert_validation["is_valid"]:
                        log_test(f"Likert Format - {test_name}", True, 
                                f"Score: {likert_validation['score']}/100")
                        results["dimension_results"][dimension]["passed"] += 1
                    else:
                        log_test(f"Likert Format - {test_name}", False, 
                                f"Issues: {', '.join(likert_validation['issues'])}")
                        results["dimension_results"][dimension]["failed"] += 1
                        
                        # Show detailed validation breakdown for failed questions
                        print(f"      🔍 DETAILED VALIDATION BREAKDOWN:")
                        for check_name, check_data in likert_validation["detailed_checks"].items():
                            status = "✅" if check_data["passed"] else "❌"
                            print(f"         {status} {check_name}: {check_data['found']} (Expected: {check_data['expected']})")
                    
                    # Validate dimension relevance
                    relevance = assess_dimension_relevance(question_text, dimension, subdimension)
                    if relevance["is_relevant"]:
                        log_test(f"Dimension Relevance - {test_name}", True,
                                f"Confidence: {relevance['confidence']:.1f}%, Semantic: {relevance['semantic_score']:.1f}%")
                    else:
                        log_test(f"Dimension Relevance - {test_name}", False,
                                f"Low relevance - Confidence: {relevance['confidence']:.1f}%, Semantic: {relevance['semantic_score']:.1f}%")
                        
                        # Show detailed relevance analysis for low-relevance questions
                        print(f"      🎯 DETAILED RELEVANCE ANALYSIS:")
                        analysis = relevance["detailed_analysis"]
                        print(f"         Primary keywords: {analysis['primary_keywords']['found']} (Score: {analysis['primary_keywords']['score']:.1f})")
                        print(f"         Secondary keywords: {analysis['secondary_keywords']['found']} (Score: {analysis['secondary_keywords']['score']:.1f})")
                        print(f"         Context keywords: {analysis['context_keywords']['found']} (Score: {analysis['context_keywords']['score']:.1f})")
                        print(f"         Semantic indicators: {analysis['semantic_indicators']['found']} (Score: {analysis['semantic_indicators']['score']:.1f}%)")
                    
                    print(f"      💬 FULL QUESTION: \"{question_text}\"")
                    print(f"      📏 Length: {len(question_text)} chars | 🎯 Likert: {likert_validation['score']}/100 | 🔍 Relevance: {relevance['confidence']:.1f}%")
                    if relevance['keywords_found']:
                        print(f"      🔑 Keywords Found: {', '.join(relevance['keywords_found'])}")
                    if not likert_validation["is_valid"] or not relevance["is_relevant"]:
                        print(f"      ⚠️  QUALITY ISSUES: {', '.join(likert_validation['issues']) if likert_validation['issues'] else 'Low relevance score'}")
                    
                    # Store comprehensive question data
                    results["generated_questions"].append({
                        "test_name": test_name,
                        "dimension": dimension,
                        "subdimension": subdimension,
                        "year_level": year_level,
                        "question": question_text,
                        "likert_validation": likert_validation,
                        "relevance_assessment": relevance,
                        "metadata": metadata
                    })
                    
                    # Update dimension averages
                    current_questions = results["dimension_results"][dimension]["questions_generated"]
                    if current_questions:
                        quality_scores = [validate_likert_question(q["question"])["score"] for q in current_questions]
                        relevance_scores = [assess_dimension_relevance(q["question"], dimension, q["subdimension"])["confidence"] for q in current_questions]
                        
                        results["dimension_results"][dimension]["average_quality_score"] = sum(quality_scores) / len(quality_scores)
                        results["dimension_results"][dimension]["average_relevance_score"] = sum(relevance_scores) / len(relevance_scores)
                    
                else:
                    log_test(f"Generation Failed - {test_name}", False,
                            f"Status: {response.status_code}, Error: {response.text}")
                    results["dimension_results"][dimension]["failed"] += 1
                    
            except Exception as e:
                log_test(f"Generation Error - {test_name}", False, f"Error: {e}")
                results["dimension_results"][dimension]["failed"] += 1
            
            # Small delay between requests
            time.sleep(0.5)
    
    # PHASE 3: Analyze dimension-specific results
    print(f"\n📋 PHASE 3: DIMENSION-SPECIFIC ANALYSIS")
    print("-" * 50)
    
    for dimension, dim_results in results["dimension_results"].items():
        print(f"\n🎯 {dimension.upper()} DIMENSION ANALYSIS:")
        print(f"   Total Tests: {dim_results['total_tests']}")
        print(f"   ✅ Passed: {dim_results['passed']}")
        print(f"   ❌ Failed: {dim_results['failed']}")
        if dim_results['total_tests'] > 0:
            success_rate = (dim_results['passed'] / dim_results['total_tests']) * 100
            print(f"   📊 Success Rate: {success_rate:.1f}%")
            print(f"   🎨 Avg Quality Score: {dim_results['average_quality_score']:.1f}/100")
            print(f"   🎯 Avg Relevance Score: {dim_results['average_relevance_score']:.1f}%")
            
            # Show best and worst questions for this dimension
            if dim_results['questions_generated']:
                questions_with_scores = []
                for q in dim_results['questions_generated']:
                    likert_score = validate_likert_question(q["question"])["score"]
                    relevance_score = assess_dimension_relevance(q["question"], dimension, q["subdimension"])["confidence"]
                    total_score = (likert_score + relevance_score) / 2
                    questions_with_scores.append((q, total_score))
                
                questions_with_scores.sort(key=lambda x: x[1], reverse=True)
                
                if questions_with_scores:
                    best_q = questions_with_scores[0][0]
                    worst_q = questions_with_scores[-1][0]
                    
                    print(f"   🏆 BEST QUESTION ({questions_with_scores[0][1]:.1f}/100):")
                    print(f"      📝 \"{best_q['question']}\"")
                    print(f"      📊 [{best_q['subdimension']} - Year {best_q['year_level']}]")
                    
                    # Show why it's the best
                    best_likert = validate_likert_question(best_q['question'])
                    best_relevance = assess_dimension_relevance(best_q['question'], dimension, best_q['subdimension'])
                    print(f"      ✨ Quality: Likert {best_likert['score']}/100, Relevance {best_relevance['confidence']:.1f}%")
                    print(f"      🔑 Keywords: {', '.join(best_relevance['keywords_found']) if best_relevance['keywords_found'] else 'None'}")
                    
                    if len(questions_with_scores) > 1:
                        print(f"   📉 NEEDS IMPROVEMENT ({questions_with_scores[-1][1]:.1f}/100):")
                        print(f"      📝 \"{worst_q['question']}\"")
                        print(f"      📊 [{worst_q['subdimension']} - Year {worst_q['year_level']}]")
                        
                        # Show what needs improvement
                        worst_likert = validate_likert_question(worst_q['question'])
                        worst_relevance = assess_dimension_relevance(worst_q['question'], dimension, worst_q['subdimension'])
                        print(f"      ⚠️  Issues: Likert {worst_likert['score']}/100, Relevance {worst_relevance['confidence']:.1f}%")
                        if worst_likert['issues']:
                            print(f"      🔧 Needs: {', '.join(worst_likert['issues'])}")
                    
                    # Show improvement statistics
                    score_range = questions_with_scores[0][1] - questions_with_scores[-1][1]
                    print(f"   📈 Quality Range: {score_range:.1f} points (Max: {questions_with_scores[0][1]:.1f}, Min: {questions_with_scores[-1][1]:.1f})")
                    
                    # Count questions by quality tier
                    excellent = sum(1 for _, score in questions_with_scores if score >= 80)
                    good = sum(1 for _, score in questions_with_scores if 60 <= score < 80)
                    needs_improvement = sum(1 for _, score in questions_with_scores if score < 60)
                    
                    print(f"   🎯 Quality Distribution: {excellent} Excellent (80+), {good} Good (60-79), {needs_improvement} Needs Work (<60)")
    
    # FINAL RESULTS SUMMARY
    print(f"\n📊 COMPREHENSIVE TEST RESULTS")
    print("="*80)
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"🎯 Overall Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
    
    # Dimension performance ranking
    dimension_performance = []
    for dimension, dim_results in results["dimension_results"].items():
        if dim_results['total_tests'] > 0:
            success_rate = (dim_results['passed'] / dim_results['total_tests']) * 100
            avg_quality = dim_results['average_quality_score']
            avg_relevance = dim_results['average_relevance_score']
            overall_score = (success_rate + avg_quality + avg_relevance) / 3
            dimension_performance.append((dimension, overall_score, success_rate, avg_quality, avg_relevance))
    
    dimension_performance.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 DIMENSION PERFORMANCE RANKING:")
    for i, (dimension, overall_score, success_rate, avg_quality, avg_relevance) in enumerate(dimension_performance, 1):
        print(f"   {i}. {dimension.upper()}")
        print(f"      Overall Score: {overall_score:.1f}/100")
        print(f"      Success Rate: {success_rate:.1f}% | Quality: {avg_quality:.1f}/100 | Relevance: {avg_relevance:.1f}%")
    
    # Show overall best and worst questions across all dimensions
    if results["generated_questions"]:
        print(f"\n🌟 OVERALL BEST & WORST QUESTIONS:")
        
        all_questions_with_scores = []
        for q_data in results["generated_questions"]:
            likert_score = q_data["likert_validation"]["score"]
            relevance_score = q_data["relevance_assessment"]["confidence"]
            total_score = (likert_score + relevance_score) / 2
            all_questions_with_scores.append((q_data, total_score))
        
        all_questions_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        if all_questions_with_scores:
            # Best overall question
            best_overall = all_questions_with_scores[0][0]
            print(f"\n🥇 BEST OVERALL QUESTION ({all_questions_with_scores[0][1]:.1f}/100):")
            print(f"   📝 \"{best_overall['question']}\"")
            print(f"   📊 {best_overall['dimension']} > {best_overall['subdimension']} (Year {best_overall['year_level']})")
            print(f"   ✨ Likert: {best_overall['likert_validation']['score']}/100, Relevance: {best_overall['relevance_assessment']['confidence']:.1f}%")
            
            # Worst overall question
            if len(all_questions_with_scores) > 1:
                worst_overall = all_questions_with_scores[-1][0]
                print(f"\n🔧 MOST NEEDS IMPROVEMENT ({all_questions_with_scores[-1][1]:.1f}/100):")
                print(f"   📝 \"{worst_overall['question']}\"")
                print(f"   📊 {worst_overall['dimension']} > {worst_overall['subdimension']} (Year {worst_overall['year_level']})")
                print(f"   ⚠️  Issues: Likert: {worst_overall['likert_validation']['score']}/100, Relevance: {worst_overall['relevance_assessment']['confidence']:.1f}%")
                if worst_overall['likert_validation']['issues']:
                    print(f"   🔧 Specific Issues: {', '.join(worst_overall['likert_validation']['issues'])}")
        
        # Quality distribution across all questions
        excellent_all = sum(1 for _, score in all_questions_with_scores if score >= 80)
        good_all = sum(1 for _, score in all_questions_with_scores if 60 <= score < 80)
        needs_work_all = sum(1 for _, score in all_questions_with_scores if score < 60)
        
        print(f"\n📊 OVERALL QUALITY DISTRIBUTION:")
        print(f"   🌟 Excellent (80+): {excellent_all}/{len(all_questions_with_scores)} ({(excellent_all/len(all_questions_with_scores)*100):.1f}%)")
        print(f"   👍 Good (60-79): {good_all}/{len(all_questions_with_scores)} ({(good_all/len(all_questions_with_scores)*100):.1f}%)")
        print(f"   🔧 Needs Work (<60): {needs_work_all}/{len(all_questions_with_scores)} ({(needs_work_all/len(all_questions_with_scores)*100):.1f}%)")
    
    if results['errors']:
        print(f"\n❌ DETAILED FAILURES ({len(results['errors'])}):")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"   • {error}")
        if len(results['errors']) > 10:
            print(f"   ... and {len(results['errors']) - 10} more errors")
    
    # Export detailed results
    export_data = {
        "test_summary": {
            "timestamp": datetime.now().isoformat(),
            "total_tests": results['total_tests'],
            "passed": results['passed'],
            "failed": results['failed'],
            "success_rate": (results['passed']/results['total_tests']*100) if results['total_tests'] > 0 else 0
        },
        "dimension_results": results["dimension_results"],
        "all_generated_questions": results["generated_questions"],
        "dimension_performance_ranking": [
            {
                "dimension": dim,
                "overall_score": score,
                "success_rate": sr,
                "quality_score": qual,
                "relevance_score": rel
            }
            for dim, score, sr, qual, rel in dimension_performance
        ]
    }
    
    # Save detailed results to file
    try:
        with open("llm_dimension_test_results.json", "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"\n💾 Detailed results exported to: llm_dimension_test_results.json")
    except Exception as e:
        print(f"\n⚠️  Could not export results: {e}")
    
    print(f"\n🎉 LLM DIMENSION TEST COMPLETED!")
    return results

if __name__ == "__main__":
    test_llm_dimensions()
