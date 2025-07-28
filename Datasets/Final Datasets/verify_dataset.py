#!/usr/bin/env python3
"""
Quick verification script for the balanced dataset
"""
import pandas as pd
from pathlib import Path

def verify_dataset():
    """Verify the balanced dataset meets all requirements"""
    
    # Load the dataset
    csv_path = Path(__file__).parent / "All Questions.csv"
    
    if not csv_path.exists():
        print("❌ Dataset not found!")
        return False
    
    df = pd.read_csv(csv_path)
    
    print("🔍 DATASET VERIFICATION")
    print("=" * 50)
    
    # Basic info
    print(f"📊 Total questions: {len(df)}")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Check expected structure
    expected_cols = ['question_id', 'dimension', 'subdimension', 'question_text', 'target_year_level']
    if list(df.columns) == expected_cols:
        print("✅ Column structure correct")
    else:
        print("❌ Column structure incorrect")
        return False
    
    # Check balance
    print(f"\n📊 DISTRIBUTION:")
    distribution = df['dimension'].value_counts().sort_index()
    total = len(df)
    
    for dim, count in distribution.items():
        percentage = (count / total) * 100
        print(f"  {dim}: {count} ({percentage:.1f}%)")
    
    # Check if balanced
    if len(distribution.unique()) == 1:
        print("✅ Perfect balance achieved!")
    else:
        ratio = distribution.max() / distribution.min()
        if ratio <= 1.1:
            print("✅ Very good balance")
        elif ratio <= 1.2:
            print("⚠️ Acceptable balance")
        else:
            print("❌ Poor balance")
    
    # Check year levels
    print(f"\n🎓 YEAR LEVELS:")
    year_dist = df['target_year_level'].value_counts().sort_index()
    for year, count in year_dist.items():
        percentage = (count / total) * 100
        print(f"  Year {year}: {count} ({percentage:.1f}%)")
    
    # Check for missing values
    print(f"\n🔍 DATA QUALITY:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("✅ No missing values")
    else:
        print("❌ Missing values found:")
        for col, count in missing.items():
            if count > 0:
                print(f"  {col}: {count}")
    
    # Check duplicates
    duplicates = df.duplicated().sum()
    if duplicates == 0:
        print("✅ No duplicate rows")
    else:
        print(f"❌ {duplicates} duplicate rows found")
    
    # Sample questions
    print(f"\n📝 SAMPLE QUESTIONS:")
    for dim in df['dimension'].unique()[:2]:
        sample = df[df['dimension'] == dim].iloc[0]
        print(f"  {dim}: {sample['question_text']}")
    
    print(f"\n🎉 Dataset verification complete!")
    return True

if __name__ == "__main__":
    verify_dataset()
