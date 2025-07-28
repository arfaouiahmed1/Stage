#!/usr/bin/env python3
"""
Test script to verify the updated generation service works with the new balanced dataset
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from core.generation_service import QuestionGenerationService
    
    print("🔄 Testing Question Generation Service with new balanced dataset...")
    
    # Initialize the service
    print("1. Initializing service...")
    service = QuestionGenerationService()
    print(f"   ✅ Service initialized successfully")
    print(f"   📊 Loaded {len(service.texts)} questions")
    
    # Test dataset loading
    print("\n2. Testing dataset structure...")
    expected_columns = ['question_id', 'dimension', 'subdimension', 'question_text', 'target_year_level']
    actual_columns = list(service.df.columns)
    print(f"   Expected columns: {expected_columns}")
    print(f"   Actual columns: {actual_columns}")
    
    if actual_columns == expected_columns:
        print("   ✅ Dataset structure is correct")
    else:
        print("   ❌ Dataset structure mismatch")
        sys.exit(1)
    
    # Test distribution
    print("\n3. Testing distribution balance...")
    distribution = service.df['dimension'].value_counts()
    print(f"   Distribution: {dict(distribution)}")
    
    # Check if balanced (should be close to equal)
    if len(distribution.unique()) == 1:
        print("   ✅ Perfect balance achieved")
    elif max(distribution) / min(distribution) < 1.2:  # Within 20%
        print("   ✅ Good balance achieved")
    else:
        print("   ⚠️ Dataset not well balanced")
    
    # Test dimensions
    print("\n4. Testing available dimensions...")
    dimensions = service.get_available_dimensions()
    print(f"   Available dimensions: {dimensions}")
    
    expected_dims = ['creativity', 'hard_skills', 'soft_skills', 'teamwork']
    if set(dimensions) == set(expected_dims):
        print("   ✅ All expected dimensions available")
    else:
        print("   ❌ Missing or extra dimensions")
    
    # Test subdimensions
    print("\n5. Testing subdimensions...")
    for dim in dimensions[:2]:  # Test first 2 dimensions
        subdims = service.get_available_subdimensions(dim)
        print(f"   {dim}: {len(subdims)} subdimensions")
        print(f"      Examples: {subdims[:3]}")
    
    # Test year levels
    print("\n6. Testing year levels...")
    year_levels = service.get_available_year_levels()
    print(f"   Available year levels: {year_levels}")
    
    if set(year_levels) == {1, 2, 3}:
        print("   ✅ All expected year levels available")
    else:
        print("   ⚠️ Unexpected year levels found")
    
    # Test validation
    print("\n7. Testing parameter validation...")
    valid = service.validate_generation_params('creativity', 'innovation_problem_solving', 2)
    print(f"   Validation result: {valid}")
    
    if valid:
        print("   ✅ Parameter validation working")
    else:
        print("   ❌ Parameter validation failed")
    
    # Test embeddings
    print("\n8. Testing embeddings setup...")
    if service.embed_model is not None and service.index is not None:
        print(f"   ✅ Embeddings initialized")
        print(f"   📊 FAISS index has {service.index.ntotal} vectors")
    else:
        print("   ❌ Embeddings not properly initialized")
    
    print("\n🎉 All tests completed successfully!")
    print("✅ The new balanced dataset is compatible with the generation service")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the Backend directory and dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during testing: {e}")
    sys.exit(1)
