import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

def create_demo_data():
    """Create demonstration data with clear skill patterns"""
    np.random.seed(42)
    n_students = 12
    
    # Create students with clear complementary skill patterns
    data = {
        'student_id': [f"STU{i:03d}" for i in range(1, n_students+1)],
        'student_name': [f"Student {i}" for i in range(1, n_students+1)],
        'communication_score': [],
        'leadership_score': [],
        'time_management_score': [],
        'analytical_score': []
    }
    
    # Group 1: High communication, low leadership (3 students)
    for i in range(3):
        data['communication_score'].append(np.random.uniform(4.5, 5.0))
        data['leadership_score'].append(np.random.uniform(1.5, 2.0))
        data['time_management_score'].append(np.random.uniform(2.5, 3.5))
        data['analytical_score'].append(np.random.uniform(2.5, 3.5))
    
    # Group 2: High leadership, low communication (3 students)
    for i in range(3):
        data['communication_score'].append(np.random.uniform(1.5, 2.0))
        data['leadership_score'].append(np.random.uniform(4.5, 5.0))
        data['time_management_score'].append(np.random.uniform(2.5, 3.5))
        data['analytical_score'].append(np.random.uniform(2.5, 3.5))
    
    # Group 3: High analytical, low time management (3 students)
    for i in range(3):
        data['communication_score'].append(np.random.uniform(2.5, 3.5))
        data['leadership_score'].append(np.random.uniform(2.5, 3.5))
        data['time_management_score'].append(np.random.uniform(1.5, 2.0))
        data['analytical_score'].append(np.random.uniform(4.5, 5.0))
    
    # Group 4: High time management, low analytical (3 students)
    for i in range(3):
        data['communication_score'].append(np.random.uniform(2.5, 3.5))
        data['leadership_score'].append(np.random.uniform(2.5, 3.5))
        data['time_management_score'].append(np.random.uniform(4.5, 5.0))
        data['analytical_score'].append(np.random.uniform(1.5, 2.0))
    
    df = pd.DataFrame(data)
    df['overall_score'] = df[['communication_score', 'leadership_score', 
                            'time_management_score', 'analytical_score']].mean(axis=1)
    
    return df

def traditional_clustering(df):
    """Apply traditional clustering based on raw skill scores"""
    score_columns = ['communication_score', 'leadership_score', 
                   'time_management_score', 'analytical_score']
    
    X = df[score_columns].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df_traditional = df.copy()
    df_traditional['cluster'] = kmeans.fit_predict(X_scaled)
    
    return df_traditional, X_scaled

def enhanced_heterogeneous_clustering(df):
    """Apply enhanced heterogeneous clustering with complementarity"""
    score_columns = ['communication_score', 'leadership_score', 
                   'time_management_score', 'analytical_score']
    
    # Step 1: Create complementarity matrix
    n_students = len(df)
    complementarity_matrix = np.zeros((n_students, len(score_columns)))
    
    for i in range(n_students):
        for j, skill in enumerate(score_columns):
            student_skill = df.iloc[i][skill]
            avg_skill = df[skill].mean()
            complementarity_matrix[i, j] = abs(student_skill - avg_skill)
    
    # Step 2: Create enhanced feature matrix
    X_skills = df[score_columns].values
    X_complementarity = complementarity_matrix
    
    # Normalize complementarity scores
    X_complementarity_normalized = (X_complementarity - X_complementarity.mean(axis=0)) / (X_complementarity.std(axis=0) + 1e-8)
    
    # Create final feature matrix with higher weights for complementarity
    X = np.column_stack([X_skills, X_complementarity_normalized])
    
    # Apply weights to emphasize complementarity
    feature_weights = [1.0, 1.0, 1.0, 1.0,  # Original skills
                      2.0, 2.0, 2.0, 2.0]   # Complementarity (emphasized)
    
    for i, weight in enumerate(feature_weights):
        X[:, i] *= weight
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df_enhanced = df.copy()
    df_enhanced['cluster'] = kmeans.fit_predict(X_scaled)
    
    return df_enhanced, X_scaled

def analyze_grouping(df, method_name):
    """Analyze the quality of grouping"""
    print(f"\n{'='*60}")
    print(f"{method_name.upper()} CLUSTERING ANALYSIS")
    print(f"{'='*60}")
    
    skills = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
    skill_names = ['Communication', 'Leadership', 'Time Management', 'Analytical']
    
    total_skill_diversity = 0
    total_complementarity_score = 0
    
    for i in range(4):
        cluster_students = df[df['cluster'] == i]
        print(f"\nGroup {i+1} ({len(cluster_students)} students):")
        
        # Calculate skill diversity within this cluster
        group_skill_diversity = 0
        for skill, name in zip(skills, skill_names):
            skill_values = cluster_students[skill].values
            skill_std = np.std(skill_values)
            skill_range = np.max(skill_values) - np.min(skill_values)
            group_skill_diversity += skill_std
            
            print(f"  {name}: std={skill_std:.2f}, range={skill_range:.2f}")
        
        # Calculate complementarity score (higher is better for heterogeneous grouping)
        complementarity_score = group_skill_diversity / len(skills)
        total_skill_diversity += group_skill_diversity
        total_complementarity_score += complementarity_score
        
        print(f"  Group complementarity score: {complementarity_score:.2f}")
        
        # Show student profiles
        print("  Student profiles:")
        for _, student in cluster_students.iterrows():
            print(f"    {student['student_name']}: "
                  f"Comm={student['communication_score']:.1f}, "
                  f"Lead={student['leadership_score']:.1f}, "
                  f"Time={student['time_management_score']:.1f}, "
                  f"Anal={student['analytical_score']:.1f}")
    
    avg_complementarity = total_complementarity_score / 4
    print(f"\n📊 Overall Analysis:")
    print(f"  Average group complementarity score: {avg_complementarity:.2f}")
    print(f"  Total skill diversity across groups: {total_skill_diversity:.2f}")
    
    return avg_complementarity

def visualize_comparison(df_traditional, df_enhanced, X_traditional, X_enhanced):
    """Create comparison visualization"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Traditional clustering visualization
    pca_traditional = PCA(n_components=2)
    X_pca_traditional = pca_traditional.fit_transform(X_traditional)
    
    for i in range(4):
        mask = df_traditional['cluster'] == i
        if sum(mask) > 0:
            ax1.scatter(X_pca_traditional[mask, 0], X_pca_traditional[mask, 1], 
                       alpha=0.7, s=100, label=f'Group {i+1}')
    
    ax1.set_title('Traditional Clustering (Similar Skills)', fontsize=14)
    ax1.set_xlabel('Principal Component 1')
    ax1.set_ylabel('Principal Component 2')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Enhanced clustering visualization
    pca_enhanced = PCA(n_components=2)
    X_pca_enhanced = pca_enhanced.fit_transform(X_enhanced)
    
    for i in range(4):
        mask = df_enhanced['cluster'] == i
        if sum(mask) > 0:
            ax2.scatter(X_pca_enhanced[mask, 0], X_pca_enhanced[mask, 1], 
                       alpha=0.7, s=100, label=f'Group {i+1}')
    
    ax2.set_title('Enhanced Heterogeneous Clustering (Complementary Skills)', fontsize=14)
    ax2.set_xlabel('Principal Component 1')
    ax2.set_ylabel('Principal Component 2')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Skill distribution comparison
    skills = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
    skill_names = ['Communication', 'Leadership', 'Time Management', 'Analytical']
    
    # Traditional clustering skill variance
    traditional_variance = []
    for skill in skills:
        variances = []
        for i in range(4):
            cluster_students = df_traditional[df_traditional['cluster'] == i]
            if len(cluster_students) > 0:
                variances.append(cluster_students[skill].var())
        traditional_variance.append(np.mean(variances))
    
    # Enhanced clustering skill variance
    enhanced_variance = []
    for skill in skills:
        variances = []
        for i in range(4):
            cluster_students = df_enhanced[df_enhanced['cluster'] == i]
            if len(cluster_students) > 0:
                variances.append(cluster_students[skill].var())
        enhanced_variance.append(np.mean(variances))
    
    x = np.arange(len(skill_names))
    width = 0.35
    
    ax3.bar(x - width/2, traditional_variance, width, label='Traditional', alpha=0.7)
    ax3.bar(x + width/2, enhanced_variance, width, label='Enhanced', alpha=0.7)
    ax3.set_xlabel('Skills')
    ax3.set_ylabel('Average Variance Within Groups')
    ax3.set_title('Skill Diversity Comparison')
    ax3.set_xticks(x)
    ax3.set_xticklabels(skill_names, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Overall comparison
    methods = ['Traditional', 'Enhanced']
    scores = [np.mean(traditional_variance), np.mean(enhanced_variance)]
    colors = ['lightcoral', 'lightblue']
    
    bars = ax4.bar(methods, scores, color=colors, alpha=0.7)
    ax4.set_ylabel('Average Skill Diversity Score')
    ax4.set_title('Overall Clustering Quality Comparison')
    ax4.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()
    
    return fig

def main():
    """Main demonstration function"""
    print("🧩 Clustering Comparison Demo")
    print("="*50)
    
    # Create demo data
    print("\n1. Creating demonstration data...")
    df = create_demo_data()
    print(f"Created {len(df)} students with complementary skill patterns")
    
    # Apply traditional clustering
    print("\n2. Applying traditional clustering...")
    df_traditional, X_traditional = traditional_clustering(df)
    
    # Apply enhanced clustering
    print("\n3. Applying enhanced heterogeneous clustering...")
    df_enhanced, X_enhanced = enhanced_heterogeneous_clustering(df)
    
    # Analyze results
    print("\n4. Analyzing clustering results...")
    traditional_score = analyze_grouping(df_traditional, "Traditional")
    enhanced_score = analyze_grouping(df_enhanced, "Enhanced")
    
    # Create visualization
    print("\n5. Creating comparison visualization...")
    fig = visualize_comparison(df_traditional, df_enhanced, X_traditional, X_enhanced)
    
    # Show comparison summary
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"Traditional clustering average diversity: {traditional_score:.3f}")
    print(f"Enhanced clustering average diversity: {enhanced_score:.3f}")
    print(f"Improvement: {((enhanced_score - traditional_score) / traditional_score * 100):.1f}%")
    
    if enhanced_score > traditional_score:
        print("\n✅ Enhanced clustering successfully creates more diverse groups!")
        print("This leads to better peer learning opportunities.")
    else:
        print("\n⚠️ Traditional clustering performed better in this case.")
        print("This might be due to the specific data patterns.")
    
    print("\n🎓 Educational Impact:")
    print("- Traditional: Groups students with similar skills")
    print("- Enhanced: Groups students with complementary skills")
    print("- Result: Better peer learning and mentorship opportunities")

if __name__ == "__main__":
    main() 