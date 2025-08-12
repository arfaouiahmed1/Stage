#!/usr/bin/env python3
"""
Test script to verify all clustering dependencies are installed correctly.
"""

def test_imports():
    """Test that all required packages can be imported"""
    try:
        print("🧪 Testing core dependencies...")
        
        # FastAPI and server
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn: OK")
        
        # Firebase
        import firebase_admin
        print("✅ Firebase Admin: OK")
        
        # Data processing
        import pandas as pd
        import numpy as np
        print("✅ Pandas and NumPy: OK")
        
        # Core ML packages
        import sklearn
        from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering
        from sklearn.cluster import DBSCAN, SpectralClustering, GaussianMixture, MeanShift
        from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
        from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
        from sklearn.decomposition import PCA
        print("✅ Scikit-learn (all clustering algorithms): OK")
        
        # SOM
        from minisom import MiniSom
        print("✅ MiniSom: OK")
        
        # Distance calculations
        import gower
        print("✅ Gower distance: OK")
        
        # Utilities
        import scipy
        print("✅ SciPy: OK")
        
        print("\n🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
        print("\n📋 Package Versions:")
        print(f"   FastAPI: {fastapi.__version__}")
        print(f"   Pandas: {pd.__version__}")
        print(f"   NumPy: {np.__version__}")
        print(f"   Scikit-learn: {sklearn.__version__}")
        print(f"   SciPy: {scipy.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Please install missing packages with: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_clustering_functionality():
    """Test basic clustering functionality"""
    try:
        print("\n🧠 Testing clustering functionality...")
        
        # Create sample data
        import numpy as np
        from sklearn.cluster import KMeans
        
        # Generate sample student data
        np.random.seed(42)
        n_students = 20
        sample_data = np.random.rand(n_students, 7)  # 7 features like our system
        
        # Test KMeans clustering
        kmeans = KMeans(n_clusters=4, random_state=42)
        labels = kmeans.fit_predict(sample_data)
        
        print(f"✅ KMeans clustering test: Created {len(set(labels))} clusters from {n_students} students")
        
        # Test evaluation metrics
        from sklearn.metrics import silhouette_score
        sil_score = silhouette_score(sample_data, labels)
        print(f"✅ Evaluation metrics test: Silhouette score = {sil_score:.3f}")
        
        print("✅ Clustering functionality: OK")
        return True
        
    except Exception as e:
        print(f"❌ Clustering test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Clustering System Dependencies\n")
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test functionality
        functionality_ok = test_clustering_functionality()
        
        if functionality_ok:
            print("\n🎉 SYSTEM READY FOR CLUSTERING!")
            print("✅ You can now start the server with:")
            print("   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        else:
            print("\n⚠️ Dependencies installed but functionality test failed")
    else:
        print("\n❌ Please install missing dependencies first")

if __name__ == "__main__":
    main()
