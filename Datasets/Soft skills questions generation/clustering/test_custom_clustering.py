import pandas as pd
import numpy as np
from student_quiz_clustering_app import perform_clustering, load_student_data

def test_custom_heterogeneous_clustering():
    """Test the custom heterogeneous clustering algorithm"""
    print("🧩 TESTING CUSTOM HETEROGENEOUS CLUSTERING")
    print("="*60)
    
    # Create test students with clear high/low skill profiles
    test_students = pd.DataFrame({
        'student_id': ['HIGH_COMM_1', 'LOW_COMM_1', 'HIGH_LEAD_1', 'LOW_LEAD_1', 'HIGH_TIME_1', 'LOW_TIME_1'],
        'student_name': ['High Comm Student', 'Low Comm Student', 'High Lead Student', 'Low Lead Student', 'High Time Student', 'Low Time Student'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'age': [20, 22, 21, 23, 20, 24],
        'nationality': ['Tunisian', 'Moroccan', 'Algerian', 'Egyptian', 'Senegalese', 'Cameroonian'],
        'communication_score': [4.8, 1.8, 3.2, 3.1, 3.0, 3.2],  # High, Low, Medium, Medium, Medium, Medium
        'leadership_score': [3.1, 2.9, 4.8, 1.6, 3.0, 3.1],     # Medium, Medium, High, Low, Medium, Medium
        'time_management_score': [2.8, 3.0, 3.3, 2.7, 4.8, 1.7], # Medium, Medium, Medium, Medium, High, Low
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
    
    # Test clustering for each student individually
    print(f"\n" + "="*60)
    print("TESTING INDIVIDUAL STUDENT CLUSTERING")
    print("="*60)
    
    for i, student in test_students.iterrows():
        print(f"\n--- Testing {student['student_name']} ---")
        student_df = pd.DataFrame([student])
        recommendations, _ = perform_clustering(student_df, all_students_df)
        
        print(f"Assigned to: {recommendations['cluster_name']}")
        print(f"Description: {recommendations['description']}")
        
        # Check if complementary skills are present
        if recommendations['strengths'] and recommendations['strengths'][0] != "Balanced skill levels":
            print("✅ Complementary skills found in group")
            for strength in recommendations['strengths']:
                print(f"  - {strength}")
        else:
            print("⚠️ No specific complementary skills identified")
    
    # Test with all students together
    print(f"\n" + "="*60)
    print("TESTING ALL STUDENTS TOGETHER")
    print("="*60)
    
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

def test_real_scenario_with_diversity():
    """Test with a realistic scenario showing the diversity issue"""
    print("\n" + "="*60)
    print("TESTING REALISTIC SCENARIO - DIVERSITY ISSUE")
    print("="*60)
    
    # Create students that would normally be grouped together (similar communication scores)
    similar_students = pd.DataFrame({
        'student_id': [f'STU{i:03d}' for i in range(1, 9)],
        'student_name': [f'Student {i}' for i in range(1, 9)],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'age': [20, 22, 21, 23, 20, 24, 25, 19],
        'nationality': ['Tunisian', 'Moroccan', 'Algerian', 'Egyptian', 'Senegalese', 'Cameroonian', 'Malian', 'Ivorian'],
        'communication_score': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],  # ALL HIGH - This should be split up!
        'leadership_score': [2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7],      # Varying levels
        'time_management_score': [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2], # Varying levels
        'analytical_score': [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7]       # Varying levels
    })
    similar_students['overall_score'] = similar_students[['communication_score', 'leadership_score', 
                                                        'time_management_score', 'analytical_score']].mean(axis=1)
    
    print("Realistic scenario created:")
    print("  → All students have high communication scores (5.0)")
    print("  → This would normally be grouped together (WRONG!)")
    print("  → Our custom algorithm should split them into heterogeneous groups")
    
    # Load existing data
    all_students_df = load_student_data()
    
    # Test clustering
    recommendations, _ = perform_clustering(similar_students, all_students_df)
    
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
    print("  → Students should be split into groups with different skill profiles")
    print("  → Each group should have a mix of high and low performers")
    print("  → This creates optimal peer learning opportunities")

def test_perfect_complementarity():
    """Test with perfect complementary pairs"""
    print("\n" + "="*60)
    print("TESTING PERFECT COMPLEMENTARY PAIRS")
    print("="*60)
    
    # Create perfect complementary pairs
    complementary_students = pd.DataFrame({
        'student_id': ['PAIR1_HIGH', 'PAIR1_LOW', 'PAIR2_HIGH', 'PAIR2_LOW', 'PAIR3_HIGH', 'PAIR3_LOW'],
        'student_name': ['High Comm 1', 'Low Comm 1', 'High Lead 1', 'Low Lead 1', 'High Time 1', 'Low Time 1'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'age': [20, 22, 21, 23, 20, 24],
        'nationality': ['Tunisian', 'Moroccan', 'Algerian', 'Egyptian', 'Senegalese', 'Cameroonian'],
        'communication_score': [4.9, 1.5, 3.0, 3.0, 3.0, 3.0],  # High-Low pair, others medium
        'leadership_score': [3.0, 3.0, 4.9, 1.5, 3.0, 3.0],     # Medium, High-Low pair, others medium
        'time_management_score': [3.0, 3.0, 3.0, 3.0, 4.9, 1.5], # Medium, Medium, High-Low pair
        'analytical_score': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0]      # All medium
    })
    complementary_students['overall_score'] = complementary_students[['communication_score', 'leadership_score', 
                                                                   'time_management_score', 'analytical_score']].mean(axis=1)
    
    print("Perfect complementary pairs created:")
    print("  → Pair 1: High Comm (4.9) + Low Comm (1.5)")
    print("  → Pair 2: High Lead (4.9) + Low Lead (1.5)")
    print("  → Pair 3: High Time (4.9) + Low Time (1.5)")
    
    # Load existing data
    all_students_df = load_student_data()
    
    # Test clustering
    recommendations, _ = perform_clustering(complementary_students, all_students_df)
    
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
    print("  → High and low performers should be paired together")
    print("  → Each skill area should show high diversity within groups")
    print("  → Perfect peer learning opportunities created")

if __name__ == "__main__":
    test_custom_heterogeneous_clustering()
    test_real_scenario_with_diversity()
    test_perfect_complementarity()
    
    print("\n" + "="*60)
    print("CUSTOM CLUSTERING TEST COMPLETED")
    print("="*60)
    print("Check the results above to verify that:")
    print("1. Students with opposite skill levels are grouped together")
    print("2. High and low performers are paired for peer learning")
    print("3. The algorithm avoids grouping similar students together")
    print("4. Each group has diverse skill levels for optimal learning") 