#!/usr/bin/env python3

import pandas as pd
import requests
import json

def test_csv_upload():
    """Test CSV upload functionality"""
    print("Testing CSV upload...")
    
    # Read the sample CSV to check its format
    try:
        df = pd.read_csv('sample_datasets/quiz_based_sample.csv')
        print(f"CSV loaded successfully with {len(df)} rows and columns: {list(df.columns)}")
        print(f"First few rows:")
        print(df.head())
        
        # Test the upload
        url = 'http://localhost:8000/upload-csv'
        
        with open('sample_datasets/quiz_based_sample.csv', 'rb') as f:
            files = {'file': f}
            data = {
                'group_size': 4,
                'method': 'complementary',
                'n_clusters': 4
            }
            
            response = requests.post(url, files=files, data=data)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text[:500]}...")
            
    except Exception as e:
        print(f"Error in CSV upload test: {e}")

def test_health():
    """Test health endpoint"""
    print("\nTesting health endpoint...")
    try:
        response = requests.get('http://localhost:8000/api/v1/health')
        print(f"Health check status: {response.status_code}")
        print(f"Health response: {response.json()}")
    except Exception as e:
        print(f"Error in health test: {e}")

def test_students():
    """Test students endpoint"""
    print("\nTesting students endpoint...")
    try:
        response = requests.get('http://localhost:8000/api/v1/students')
        print(f"Students status: {response.status_code}")
        students = response.json()
        print(f"Number of students: {len(students)}")
        if students:
            print(f"First student: {students[0]}")
    except Exception as e:
        print(f"Error in students test: {e}")

if __name__ == "__main__":
    test_health()
    test_students()
    test_csv_upload()