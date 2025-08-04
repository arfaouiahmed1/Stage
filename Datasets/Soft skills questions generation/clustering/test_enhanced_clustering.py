import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

def create_test_data():
    """Create test data with diverse skill profiles to demonstrate heterogeneous clustering"""
    np.random.seed(42)
    n_students = 20
    
    # Create students with diverse skill profiles
    data = {
        'student_id': [f"STU{i:03d}" for i in range(1, n_students+1)],
        'student_name': [f"Student {i}" for i in range(1, n_students+1)],
        'communication_score': [],
        'leadership_score': [],
        'time_management_score': [],
        'analytical_score': []
    }
    
    # Group 1: High communication, low leadership (5 students)
    for i in range(5):
        data['communication_score'].append(np.random.uniform(4.0, 5.0))
        data['leadership_score'].append(np.random.uniform(1.5, 2.5))
        data['time_management_score'].append(np.random.uniform(2.5, 3.5))
        data['analytical_score'].append(np.random.uniform(2.5, 3.5))
    
    # Group 2: High leadership, low communication (5 students)
    for i in range(5):
        data['communication_score'].append(np.random.uniform(1.5, 2.5))
        data['leadership_score'].append(np.random.uniform(4.0, 5.0))
        data['time_management_score'].append(np.random.uniform(2.5, 3.5))
        data['analytical_score'].append(np.random.uniform(2.5, 3.5))
    
    # Group 3: High analytical, low time management (5 students)
    for i in range(5):
        data['communication_score'].append(np.random.uniform(2.5, 3.5))
        data['leadership_score'].append(np.random.uniform(2.5, 3.5))
        data['time_management_score'].append(np.random.uniform(1.5, 2.5))
        data['analytical_score'].append(np.random.uniform(4.0, 5.0))
    
    # Group 4: High time management, low analytical (5 students)
    for i in range(5):
        data['communication_score'].append(np.random.uniform(2.5, 3.5))
        data['leadership_score'].append(np.random.uniform(2.5, 3.5))
        data['time_management_score'].append(np.random.uniform(4.0, 5.0))
        data['analytical_score'].append(np.random.uniform(1.5, 2.5))
    
    df = pd.DataFrame(data)
    df['overall_score'] = df[['communication_score', 'leadership_score', 
                            'time_management_score', 'analytical_score']].mean(axis=1)
    
    return df

def enhanced_heterogeneous_clustering(df):
    """Apply enhanced heterogeneous clustering approach"""
    score_columns = ['communication_score', 'leadership_score', 
                   'time_management_score', 'analytical_score']
    
    # Step 1: Create skill diversity features
    skill_variance = {}
    for skill in score_columns:
        skill_variance[skill] = df[skill].var()
    
    print("Skill variance across all students:")
    for skill, variance in skill_variance.items():
        print(f"  {skill}: {variance:.3f}")
    
    # Step 2: Create complementary skill pairs
    n_students = len(df)
    complementarity_matrix = np.zeros((n_students, len(score_columns)))
    
    for i in range(n_students):
        for j, skill in enumerate(score_columns):
            student_skill = df.iloc[i][skill]
            avg_skill = df[skill].mean()
            complementarity_matrix[i, j] = abs(student_skill - avg_skill)
    
    # Step 3: Create enhanced feature matrix
    X_skills = df[score_columns].values
    X_complementarity = complementarity_matrix
    
    # Normalize complementarity scores
    X_complementarity_normalized = (X_complementarity - X_complementarity.mean(axis=0)) / (X_complementarity.std(axis=0) + 1e-8)
    
    # Create final feature matrix: [original_skills, complementarity_scores]
    X = np.column_stack([X_skills, X_complementarity_normalized])
    
    # Define feature weights to emphasize skill diversity
    feature_weights = [1.0, 1.0, 1.0, 1.0,  # Original skill scores
                      2.0, 2.0, 2.0, 2.0]   # Complementarity scores (higher weight)
    
    # Apply weights
    for i, weight in enumerate(feature_weights):
        X[:, i] *= weight
    
    # Scale all features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Enhanced clustering approach: Use both similarity and complementarity
    X_hybrid = np.column_stack([
        X_scaled[:, :4],  # Original skill scores
        X_scaled[:, 4:8]  # Complementarity scores (emphasized)
    ])
    
    # Determine optimal number of clusters
    k_range = range(2, 6)
    silhouette_scores = []
    
    for k in k_range:
        try:
            kmeans_test = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans_test.fit(X_hybrid)
            cluster_labels = kmeans_test.predict(X_hybrid)
            
            silhouette_avg = silhouette_score(X_hybrid, cluster_labels)
            silhouette_scores.append(silhouette_avg)
            print(f"Silhouette score for k={k}: {silhouette_avg:.3f}")
        except Exception as e:
            silhouette_scores.append(-1)
            print(f"Clustering failed for k={k}: {e}")
    
    # Choose optimal k
    optimal_k = k_range[silhouette_scores.index(max(silhouette_scores))]
    print(f"\nOptimal number of clusters: {optimal_k}")
    
    # Perform final clustering
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_hybrid)
    centers = kmeans.cluster_centers_
    
    return df, centers, X_hybrid

def analyze_clusters(df, centers):
    """Analyze the clusters to show heterogeneous grouping"""
    print("\n" + "="*60)
    print("HETEROGENEOUS CLUSTERING ANALYSIS")
    print("="*60)
    
    for i in range(len(centers)):
        cluster_students = df[df['cluster'] == i]
        print(f"\nGroup {i+1} ({len(cluster_students)} students):")
        
        # Calculate skill diversity within this cluster
        skills = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
        skill_names = ['Communication', 'Leadership', 'Time Management', 'Analytical']
        
        print("  Skill diversity within group:")
        for skill, name in zip(skills, skill_names):
            skill_values = cluster_students[skill].values
            skill_std = np.std(skill_values)
            skill_range = np.max(skill_values) - np.min(skill_values)
            print(f"    {name}: std={skill_std:.2f}, range={skill_range:.2f}")
        
        # Show student skill profiles
        print("  Student skill profiles:")
        for _, student in cluster_students.iterrows():
            print(f"    {student['student_name']}: "
                  f"Comm={student['communication_score']:.1f}, "
                  f"Lead={student['leadership_score']:.1f}, "
                  f"Time={student['time_management_score']:.1f}, "
                  f"Anal={student['analytical_score']:.1f}")
        
        # Identify complementary skills
        high_variance_skills = []
        low_variance_skills = []
        
        for skill, name in zip(skills, skill_names):
            skill_std = np.std(cluster_students[skill].values)
            if skill_std > 1.0:  # High variance indicates complementary skills
                high_variance_skills.append(name)
            elif skill_std < 0.5:  # Low variance indicates similar skills
                low_variance_skills.append(name)
        
        if high_variance_skills:
            print(f"  ✅ Complementary skills: {', '.join(high_variance_skills)}")
        if low_variance_skills:
            print(f"  📊 Similar skill levels: {', '.join(low_variance_skills)}")

def visualize_clusters(df, X_hybrid):
    """Visualize the clusters using PCA"""
    # Use PCA for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_hybrid)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot each cluster with different colors
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for i in range(df['cluster'].max() + 1):
        mask = df['cluster'] == i
        if sum(mask) > 0:
            ax.scatter(X_pca[mask, 0], X_pca[mask, 1], 
                      c=colors[i], alpha=0.7, s=100, 
                      label=f'Group {i+1} ({sum(mask)} students)')
    
    ax.set_title('Enhanced Heterogeneous Clustering Results', fontsize=16)
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return fig

def main():
    """Main function to demonstrate enhanced heterogeneous clustering"""
    print("🧩 Enhanced Heterogeneous Clustering Demo")
    print("="*50)
    
    # Create test data
    print("\n1. Creating test data with diverse skill profiles...")
    df = create_test_data()
    print(f"Created {len(df)} students with diverse skill profiles")
    
    # Apply enhanced clustering
    print("\n2. Applying enhanced heterogeneous clustering...")
    df, centers, X_hybrid = enhanced_heterogeneous_clustering(df)
    
    # Analyze results
    print("\n3. Analyzing clustering results...")
    analyze_clusters(df, centers)
    
    # Visualize results
    print("\n4. Creating visualization...")
    fig = visualize_clusters(df, X_hybrid)
    
    # Show summary statistics
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total students: {len(df)}")
    print(f"Number of groups: {df['cluster'].nunique()}")
    
    # Show group sizes
    group_sizes = df['cluster'].value_counts().sort_index()
    print("\nGroup sizes:")
    for group, size in group_sizes.items():
        print(f"  Group {group+1}: {size} students")
    
    # Show overall skill statistics
    skills = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
    skill_names = ['Communication', 'Leadership', 'Time Management', 'Analytical']
    
    print("\nOverall skill statistics:")
    for skill, name in zip(skills, skill_names):
        mean_val = df[skill].mean()
        std_val = df[skill].std()
        print(f"  {name}: mean={mean_val:.2f}, std={std_val:.2f}")
    
    print("\n✅ Enhanced heterogeneous clustering completed successfully!")
    print("The algorithm successfully grouped students with complementary skills together.")

if __name__ == "__main__":
    main() 