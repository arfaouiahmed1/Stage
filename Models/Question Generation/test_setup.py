import os
import sys
import pandas as pd
from pathlib import Path

def test_data_loading():
    """Test if CSV data can be loaded correctly"""
    print("🔍 Testing data loading...")
    
    data_folder = Path("../../Datasets/Quiz Generation")
    
    # Test questions.csv
    questions_file = data_folder / "questions.csv"
    if questions_file.exists():
        try:
            questions_df = pd.read_csv(questions_file)
            print(f"✅ questions.csv loaded: {len(questions_df)} rows")
        except Exception as e:
            print(f"❌ Error loading questions.csv: {e}")
            return False
    else:
        print(f"❌ questions.csv not found at {questions_file}")
        return False
    
    # Test taxonomy.csv
    taxonomy_file = data_folder / "taxonomy.csv"
    if taxonomy_file.exists():
        try:
            taxonomy_df = pd.read_csv(taxonomy_file)
            print(f"✅ taxonomy.csv loaded: {len(taxonomy_df)} rows")
        except Exception as e:
            print(f"❌ Error loading taxonomy.csv: {e}")
            return False
    else:
        print(f"❌ taxonomy.csv not found at {taxonomy_file}")
        return False
    
    # Test rubrics.csv
    rubrics_file = data_folder / "rubrics.csv"
    if rubrics_file.exists():
        try:
            rubrics_df = pd.read_csv(rubrics_file)
            print(f"✅ rubrics.csv loaded: {len(rubrics_df)} rows")
        except Exception as e:
            print(f"❌ Error loading rubrics.csv: {e}")
            return False
    else:
        print(f"❌ rubrics.csv not found at {rubrics_file}")
        return False
    
    return True

def test_dependencies():
    """Test if required packages are installed"""
    print("📦 Testing dependencies...")
    
    required_packages = [
        "pandas",
        "numpy", 
        "sentence_transformers",
        "faiss",
        "google.generativeai",
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "faiss":
                import faiss
            elif package == "google.generativeai":
                import google.generativeai
            elif package == "python-dotenv":
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_embedding_model():
    """Test if embedding model can be loaded"""
    print("🧠 Testing embedding model (this may take a moment)...")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test encoding
        test_texts = ["This is a test sentence", "Another test sentence"]
        embeddings = model.encode(test_texts)
        
        print(f"✅ Embedding model loaded successfully")
        print(f"   Model dimension: {embeddings.shape[1]}")
        print(f"   Test embeddings shape: {embeddings.shape}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading embedding model: {e}")
        return False

def test_vector_index():
    """Test FAISS vector index functionality"""
    print("🔢 Testing vector indexing...")
    
    try:
        import faiss
        import numpy as np
        
        # Create test embeddings
        dimension = 384
        test_embeddings = np.random.random((10, dimension)).astype('float32')
        
        # Create and test index
        index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(test_embeddings)
        index.add(test_embeddings)
        
        # Test search
        query = np.random.random((1, dimension)).astype('float32')
        faiss.normalize_L2(query)
        scores, indices = index.search(query, 3)
        
        print(f"✅ Vector index working correctly")
        print(f"   Index size: {index.ntotal}")
        print(f"   Search results: {len(indices[0])} items")
        return True
        
    except Exception as e:
        print(f"❌ Error with vector indexing: {e}")
        return False

def test_api_key_setup():
    """Test API key configuration"""
    print("🔑 Testing API key setup...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found - copy from .env.example")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not set in .env file")
        return False
    elif api_key == "your_google_api_key_here":
        print("⚠️  GOOGLE_API_KEY still has placeholder value")
        print("   Please set your actual Google API key in .env file")
        return False
    else:
        print("✅ GOOGLE_API_KEY is configured")
        return True

def main():
    """Run all tests"""
    print("🧪 Question Generation RAG System - Tests")
    print("=" * 50)
    
    tests = [
        ("Data Loading", test_data_loading),
        ("Dependencies", test_dependencies),
        ("Embedding Model", test_embedding_model),
        ("Vector Index", test_vector_index),
        ("API Key Setup", test_api_key_setup)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python question_generation_rag.py")
        print("2. Or start API: python api.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\nCommon solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Set API key in .env file")
        print("- Ensure CSV files are in correct location")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
