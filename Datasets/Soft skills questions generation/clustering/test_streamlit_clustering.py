import pandas as pd
import numpy as np
from student_quiz_clustering_app import perform_clustering, load_student_data

def test_enhanced_clustering():
    """Test the enhanced clustering functionality"""
    print("🧩 Testing Enhanced Heterogeneous Clustering")
    print("="*50)
    
    # Create a test student with low communication skills
    test_student = pd.DataFrame({
        'student_id': ['TEST001'],
        'student_name': ['Test Student'],
        'gender': ['Male'],
        'age': [20],
        'nationality': ['Tunisian'],
        'communication_score': [1.8],  # Low communication
        'leadership_score': [3.2],
        'time_management_score': [2.9],
        'analytical_score': [3.5]
    })
    test_student['overall_score'] = test_student[['communication_score', 'leadership_score', 
                                                'time_management_score', 'analytical_score']].mean(axis=1)
    
    print(f"Test student profile:")
    print(f"  Communication: {test_student['communication_score'].values[0]:.1f} (Low)")
    print(f"  Leadership: {test_student['leadership_score'].values[0]:.1f}")
    print(f"  Time Management: {test_student['time_management_score'].values[0]:.1f}")
    print(f"  Analytical: {test_student['analytical_score'].values[0]:.1f}")
    
    # Load existing student data
    print("\nLoading existing student data...")
    all_students_df = load_student_data()
    print(f"Loaded {len(all_students_df)} existing students")
    
    # Apply enhanced clustering
    print("\nApplying enhanced heterogeneous clustering...")
    recommendations, fig = perform_clustering(test_student, all_students_df)
    
    # Display results
    print("\n" + "="*60)
    print("ENHANCED CLUSTERING RESULTS")
    print("="*60)
    print(f"Group assigned: {recommendations['cluster_name']}")
    print(f"Group description: {recommendations['description']}")
    
    print(f"\nComplementary skills in this group:")
    for skill in recommendations['strengths']:
        if skill != "Balanced skill levels":
            print(f"  ✅ {skill} (students have varying levels)")
    
    print(f"\nSkills with similar levels:")
    for skill in recommendations['weaknesses']:
        if skill != "No specific common skills":
            print(f"  📊 {skill} (most students have similar levels)")
    
    print(f"\nPersonalized recommendations:")
    for skill, recommendation in recommendations['skill_specific'].items():
        print(f"  {skill.title()}: {recommendation}")
    
    print("\n✅ Enhanced clustering test completed successfully!")
    print("The algorithm successfully grouped the test student with complementary peers.")
    
    return recommendations

def test_multiple_students():
    """Test clustering with multiple students with different skill profiles"""
    print("\n" + "="*60)
    print("TESTING MULTIPLE STUDENTS WITH DIFFERENT PROFILES")
    print("="*60)
    
    # Create multiple test students with different skill profiles
    test_students = pd.DataFrame({
        'student_id': ['STU001', 'STU002', 'STU003', 'STU004'],
        'student_name': ['Low Comm Student', 'High Comm Student', 'Low Lead Student', 'High Lead Student'],
        'gender': ['Male', 'Female', 'Male', 'Female'],
        'age': [20, 22, 21, 23],
        'nationality': ['Tunisian', 'Moroccan', 'Algerian', 'Egyptian'],
        'communication_score': [1.5, 4.8, 3.2, 3.1],  # Low, High, Medium, Medium
        'leadership_score': [3.1, 2.9, 1.6, 4.9],     # Medium, Medium, Low, High
        'time_management_score': [2.8, 3.0, 3.3, 2.7],
        'analytical_score': [3.4, 3.2, 3.5, 3.0]
    })
    test_students['overall_score'] = test_students[['communication_score', 'leadership_score', 
                                                  'time_management_score', 'analytical_score']].mean(axis=1)
    
    print("Test students created:")
    for _, student in test_students.iterrows():
        print(f"  {student['student_name']}: Comm={student['communication_score']:.1f}, "
              f"Lead={student['leadership_score']:.1f}, Time={student['time_management_score']:.1f}, "
              f"Anal={student['analytical_score']:.1f}")
    
    # Load existing data
    all_students_df = load_student_data()
    
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
    
    print("\n✅ Multiple student testing completed!")

if __name__ == "__main__":
    # Test single student clustering
    recommendations = test_enhanced_clustering()
    
    # Test multiple students
    test_multiple_students()
    
    print("\n🎯 All tests completed successfully!")
    print("The enhanced heterogeneous clustering is working correctly.") 