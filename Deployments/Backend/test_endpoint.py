#!/usr/bin/env python3
"""
Quick test script to verify that the clustering endpoints work correctly
and that the name corruption issue is fixed.
"""

import requests
import json
import pandas as pd
import io
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_CSV_PATH = "test_students.csv"

def create_test_csv():
    """Create a test CSV file with clean names"""
    test_data = {
        'first_name': ['Hiba', 'Ahmed', 'Amel', 'Zied', 'Ismail', 'Nadia', 'Sarah', 'Mohamed', 'Fatima', 'Ali'],
        'last_name': ['Haddad', 'Bouazizi', 'Slimani', 'Chebbi', 'Slimani', 'Berrada', 'Ben Ali', 'Khelifi', 'Turki', 'Mansour'],
        'hard_skills': [4.2, 3.8, 4.5, 3.2, 4.8, 3.9, 4.1, 3.6, 4.3, 3.7],
        'soft_skills': [3.8, 4.1, 3.9, 4.2, 3.5, 4.4, 4.0, 3.8, 4.2, 3.9],
        'creativity': [4.0, 3.7, 4.3, 3.8, 4.1, 4.2, 3.9, 4.0, 3.6, 4.4],
        'teamwork': [4.1, 4.0, 3.8, 4.3, 3.9, 4.1, 4.2, 3.7, 4.0, 3.8],
        'gender': ['F', 'M', 'F', 'M', 'M', 'F', 'F', 'M', 'F', 'M'],
        'nationality': ['Tunisian', 'Tunisian', 'Tunisian', 'Tunisian', 'Tunisian', 'Moroccan', 'Tunisian', 'Tunisian', 'Algerian', 'Tunisian'],
        'age': [22, 23, 21, 24, 22, 23, 21, 25, 22, 24],
        'class': ['CS3A', 'CS3A', 'CS3B', 'CS3A', 'CS3B', 'CS3A', 'CS3B', 'CS3A', 'CS3B', 'CS3A']
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv(TEST_CSV_PATH, index=False)
    print(f"✅ Created test CSV with {len(df)} students")
    print(f"Sample names: {df[['first_name', 'last_name']].head(3).to_dict('records')}")
    return TEST_CSV_PATH

def test_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_generate_clusters():
    """Test the main clustering endpoint"""
    print("\n🧪 Testing /generate-clusters endpoint...")
    
    csv_path = create_test_csv()
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('students.csv', f, 'text/csv')}
            data = {
                'group_name_prefix': 'Test Group',
                'collection_name': 'test_groups',
                'save_to_firebase': 'false'  # Disable Firebase saving for testing
            }
            
            response = requests.post(
                f"{BASE_URL}/generate-clusters",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Clustering successful!")
            
            # Check for name corruption
            print(f"📊 Generated {len(result['groups'])} groups")
            print(f"🤖 Best algorithm: {result['best_algorithm']}")
            
            # Examine first few students for name corruption
            print("\n👥 Sample student names from groups:")
            for i, group in enumerate(result['groups'][:2]):  # Check first 2 groups
                print(f"  Group {group['group']}:")
                for j, member in enumerate(group['members'][:3]):  # First 3 members
                    name = f"{member.get('first_name', 'N/A')} {member.get('last_name', 'N/A')}"
                    print(f"    {j+1}. {name}")
                    
                    # Check for corruption patterns
                    if '_' in name and any(char.isdigit() for char in name):
                        print(f"    ⚠️ WARNING: Possible name corruption detected: {name}")
                    else:
                        print(f"    ✅ Name looks clean")
            
            return True
            
        else:
            print(f"❌ Clustering failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing clustering: {e}")
        return False
    finally:
        # Clean up
        if Path(csv_path).exists():
            Path(csv_path).unlink()

def test_quick_clusters():
    """Test the quick clustering endpoint"""
    print("\n🧪 Testing /generate-clusters-quick endpoint...")
    
    csv_path = create_test_csv()
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('students.csv', f, 'text/csv')}
            
            response = requests.post(
                f"{BASE_URL}/generate-clusters-quick",
                files=files,
                timeout=15
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quick clustering successful!")
            print(f"📊 Generated {len(result['groups'])} groups")
            
            # Check names in first group
            if result['groups']:
                first_group = result['groups'][0]
                print(f"👥 First group sample names:")
                for member in first_group['members'][:2]:
                    name = f"{member.get('first_name', 'N/A')} {member.get('last_name', 'N/A')}"
                    print(f"  - {name}")
            
            return True
        else:
            print(f"❌ Quick clustering failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing quick clustering: {e}")
        return False
    finally:
        if Path(csv_path).exists():
            Path(csv_path).unlink()

def main():
    """Run all tests"""
    print("🚀 Starting endpoint tests...\n")
    
    # Test server health
    if not test_health():
        print("❌ Server is not running. Please start the server first with:")
        print("   cd 'c:\\Users\\ahmed\\Desktop\\Stage Esprit\\Stage\\Deployments\\Backend'")
        print("   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test main clustering endpoint
    success1 = test_generate_clusters()
    
    # Test quick clustering endpoint
    success2 = test_quick_clusters()
    
    # Summary
    print(f"\n📝 Test Summary:")
    print(f"   Main clustering: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Quick clustering: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! The name corruption issue should be fixed.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
