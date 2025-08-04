import pandas as pd
import numpy as np
from student_quiz_clustering_app import perform_clustering, load_student_data

def test_improved_complementarity():
    """Test the improved complementarity clustering"""
    print("🧩 TESTING IMPROVED COMPLEMENTARITY CLUSTERING")
    print("="*60)
    
    # Create test students with clear complementary profiles
    test_students = pd.DataFrame({
        'student_id': ['TEST001', 'TEST002', 'TEST003', 'TEST004', 'TEST005', 'TEST006'],
        'student_name': ['Low Comm Student', 'High Comm Student', 'Low Lead Student', 'High Lead Student', 'Low Time Student', 'High Time Student'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'age': [20, 22, 21, 23, 20, 24],
        'nationality': ['Tunisian', 'Moroccan', 'Algerian', 'Egyptian', 'Senegalese', 'Cameroonian'],
        'communication_score': [1.8, 4.8, 3.2, 3.1, 3.0, 3.2],  # Low, High, Medium, Medium, Medium, Medium
        'leadership_score': [3.1, 2.9, 1.6, 4.9, 3.0, 3.1],     # Medium, Medium, Low, High, Medium, Medium
        'time_management_score': [2.8, 3.0, 3.3, 2.7, 1.7, 4.8], # Medium, Medium, Medium, Medium, Low, High
        'analytical_score': [3.4, 3.2, 3.5, 3.0, 3.3, 3.1]      # Medium, Medium, Medium, Medium, Medium, Medium
    })
    test_students['overall_score'] = test_students[['communication_score', 'leadership_score', 
                                                  'time_management_score', 'analytical_score']].mean(axis=1)
    
    print("Test students created:")
    for _, student in test_students.iterrows():
        print(f"  {student['student_name']}: Comm={student['communication_score']:.1f}, "
              f"Lead={student['leadership_score']:.1f}, Time={student['time_management_score']:.1f}, "
              f"Anal={student['analytical_score']:.1f}")
    
    # Load existing data (should be empty for clean test)
    all_students_df = load_student_data()
    print(f"\nLoaded {len(all_students_df)} existing students")
    
    # Test clustering for each student
    for i, student in test_students.iterrows():
        print(f"\n--- Testing {student['student_name']} ---")
        student_df = pd.DataFrame([student])
        recommendations, _ = perform_clustering(student_df, all_students_df)
        
        print(f"Assigned to: {recommendations['cluster_name']}")
        print(f"Description: {recommendations['description']}")
        
        # Check if complementary skills are present
        if recommendations['strengths'] and recommendations['strengths'][0] != "Balanced skill levels":
            print("✅ Complementary skills found in group")
        else:
            print("⚠️ No specific complementary skills identified")
    
    print("\n" + "="*60)
    print("TESTING WITH MULTIPLE STUDENTS TOGETHER")
    print("="*60)
    
    # Test with multiple students at once
    recommendations, _ = perform_clustering(test_students, all_students_df)
    
    print(f"Group assignment: {recommendations['cluster_name']}")
    print(f"Description: {recommendations['description']}")
    
    if recommendations['strengths'] and recommendations['strengths'][0] != "Balanced skill levels":
        print("✅ Complementary skills identified:")
        for strength in recommendations['strengths']:
            print(f"  - {strength}")
    else:
        print("⚠️ No specific complementary skills identified")
    
    print("\n🎯 Expected Results:")
    print("  → Low communication students should be grouped with high communicators")
    print("  → Low leadership students should be grouped with natural leaders")
    print("  → Low time management students should be grouped with organized peers")
    print("  → Students with similar skill levels should NOT be grouped together")

def test_real_scenario():
    """Test with a more realistic scenario"""
    print("\n" + "="*60)
    print("TESTING REALISTIC SCENARIO")
    print("="*60)
    
    # Create realistic student profiles
    realistic_students = pd.DataFrame({
        'student_id': [f'STU{i:03d}' for i in range(1, 13)],
        'student_name': [f'Student {i}' for i in range(1, 13)],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'age': [20, 22, 21, 23, 20, 24, 25, 19, 26, 21, 23, 20],
        'nationality': ['Tunisian', 'Moroccan', 'Algerian', 'Egyptian', 'Senegalese', 'Cameroonian', 'Malian', 'Ivorian', 'Nigerian', 'Ghanaian', 'Ethiopian', 'Kenyan'],
        'communication_score': [1.5, 4.9, 2.1, 4.7, 3.2, 3.1, 1.8, 4.8, 3.0, 3.3, 2.2, 4.6],
        'leadership_score': [4.8, 2.1, 4.9, 1.9, 3.1, 3.2, 4.7, 2.0, 3.0, 3.1, 4.6, 1.8],
        'time_management_score': [3.2, 3.0, 3.1, 3.3, 1.6, 4.9, 3.0, 3.2, 1.7, 4.8, 3.1, 3.0],
        'analytical_score': [3.1, 3.2, 3.0, 3.1, 4.8, 1.7, 3.2, 3.0, 4.9, 1.6, 3.1, 3.2]
    })
    realistic_students['overall_score'] = realistic_students[['communication_score', 'leadership_score', 
                                                           'time_management_score', 'analytical_score']].mean(axis=1)
    
    print("Realistic student profiles created:")
    print("  High Communication (4.6-4.9): Students 2, 4, 8, 12")
    print("  Low Communication (1.5-2.2): Students 1, 3, 7, 11")
    print("  High Leadership (4.6-4.9): Students 1, 3, 7, 11")
    print("  Low Leadership (1.8-2.1): Students 2, 4, 8, 12")
    print("  High Time Management (4.8-4.9): Students 6, 10")
    print("  Low Time Management (1.6-1.7): Students 5, 9")
    print("  High Analytical (4.8-4.9): Students 5, 9")
    print("  Low Analytical (1.6-1.7): Students 6, 10")
    
    # Load existing data
    all_students_df = load_student_data()
    
    # Test clustering
    recommendations, _ = perform_clustering(realistic_students, all_students_df)
    
    print(f"\nClustering Results:")
    print(f"Group: {recommendations['cluster_name']}")
    print(f"Description: {recommendations['description']}")
    
    if recommendations['strengths'] and recommendations['strengths'][0] != "Balanced skill levels":
        print("✅ Complementary skills identified:")
        for strength in recommendations['strengths']:
            print(f"  - {strength}")
    else:
        print("⚠️ No specific complementary skills identified")
    
    print("\n🎯 Expected Outcome:")
    print("  → Students with opposite skill levels should be grouped together")
    print("  → High and low performers in the same skill should be in the same group")
    print("  → This creates optimal peer learning opportunities")

if __name__ == "__main__":
    test_improved_complementarity()
    test_real_scenario()
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
    print("Check the results above to verify that:")
    print("1. Students with low skills are grouped with high performers")
    print("2. Complementary skills are identified in each group")
    print("3. The clustering creates optimal peer learning opportunities") 