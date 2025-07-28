#!/usr/bin/env python3
"""
Dataset Statistics and Analysis Script
Provides comprehensive statistics about the All Questions.csv dataset
including issues, distribution, and quality metrics.
"""

import pandas as pd
import re
import os
from pathlib import Path
from collections import Counter, defaultdict
import csv

class DatasetAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.input_file = self.base_path / "All Questions.csv"
        
    def load_dataset(self):
        """Load the dataset with error handling"""
        print("Loading dataset...")
        
        try:
            # First, try standard loading
            df = pd.read_csv(self.input_file, encoding='utf-8')
            print(f"✅ Successfully loaded with pandas: {len(df)} rows")
            return df, "pandas"
        except Exception as e:
            print(f"❌ Pandas loading failed: {e}")
            
            try:
                # Try with different quoting
                df = pd.read_csv(self.input_file, encoding='utf-8', quoting=csv.QUOTE_NONE, error_bad_lines=False, warn_bad_lines=True)
                print(f"⚠️ Loaded with QUOTE_NONE: {len(df)} rows")
                return df, "quote_none"
            except Exception as e2:
                print(f"❌ Alternative loading failed: {e2}")
                return None, "failed"
    
    def analyze_file_structure(self):
        """Analyze the raw file structure line by line"""
        print("\n" + "="*60)
        print("FILE STRUCTURE ANALYSIS")
        print("="*60)
        
        if not self.input_file.exists():
            print("❌ File does not exist!")
            return
        
        total_lines = 0
        header_lines = 0
        empty_lines = 0
        comment_lines = 0
        data_lines = 0
        malformed_lines = 0
        valid_csv_lines = 0
        
        column_counts = Counter()
        line_issues = []
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                line = line.strip()
                
                if not line:
                    empty_lines += 1
                    continue
                
                if line.startswith('#'):
                    comment_lines += 1
                    continue
                
                if line_num <= 3 and 'question_id' in line:
                    header_lines += 1
                    continue
                
                # Count columns by splitting on comma
                parts = line.split(',')
                column_counts[len(parts)] += 1
                
                # Check if it's a valid CSV row (should have 6 columns)
                if len(parts) == 6:
                    valid_csv_lines += 1
                    # Check if it looks like a question row
                    if parts[0] and any(parts[0].startswith(prefix) for prefix in ['sa_', 'ss_', 'tw_', 'hs_']):
                        data_lines += 1
                else:
                    malformed_lines += 1
                    if len(line_issues) < 10:  # Store first 10 examples
                        line_issues.append({
                            'line_num': line_num,
                            'columns': len(parts),
                            'content': line[:100] + "..." if len(line) > 100 else line
                        })
        
        print(f"📊 Total lines: {total_lines}")
        print(f"📝 Header lines: {header_lines}")
        print(f"💬 Comment lines: {comment_lines}")
        print(f"⬜ Empty lines: {empty_lines}")
        print(f"✅ Valid data lines: {data_lines}")
        print(f"✅ Valid CSV structure: {valid_csv_lines}")
        print(f"❌ Malformed lines: {malformed_lines}")
        
        print(f"\n📊 Column distribution:")
        for col_count, frequency in sorted(column_counts.items()):
            print(f"  {col_count} columns: {frequency} lines")
        
        if line_issues:
            print(f"\n⚠️ Examples of malformed lines:")
            for issue in line_issues[:5]:
                print(f"  Line {issue['line_num']} ({issue['columns']} cols): {issue['content']}")
    
    def analyze_question_ids(self, df):
        """Analyze question ID patterns and issues"""
        print("\n" + "="*60)
        print("QUESTION ID ANALYSIS")
        print("="*60)
        
        if df is None or 'question_id' not in df.columns:
            print("❌ Cannot analyze - no question_id column")
            return
        
        question_ids = df['question_id'].dropna()
        
        # Pattern analysis
        patterns = defaultdict(int)
        prefixes = defaultdict(int)
        invalid_ids = []
        
        for qid in question_ids:
            if pd.isna(qid):
                continue
                
            qid_str = str(qid)
            
            # Check prefix patterns
            if '_' in qid_str:
                prefix = qid_str.split('_')[0]
                prefixes[prefix] += 1
                
                # Check if it matches expected pattern
                if re.match(r'^(sa|ss|tw|hs)_\d+$', qid_str):
                    patterns['valid'] += 1
                else:
                    patterns['invalid'] += 1
                    if len(invalid_ids) < 10:
                        invalid_ids.append(qid_str)
            else:
                patterns['no_underscore'] += 1
                if len(invalid_ids) < 10:
                    invalid_ids.append(qid_str)
        
        print(f"📊 Total question IDs: {len(question_ids)}")
        print(f"✅ Valid format (xx_###): {patterns['valid']}")
        print(f"❌ Invalid format: {patterns['invalid'] + patterns['no_underscore']}")
        
        print(f"\n📊 Prefix distribution:")
        for prefix, count in sorted(prefixes.items()):
            prefix_meaning = {
                'sa': 'creativity',
                'ss': 'soft_skills', 
                'tw': 'teamwork',
                'hs': 'hard_skills'
            }.get(prefix, 'unknown')
            print(f"  {prefix}_: {count} ({prefix_meaning})")
        
        if invalid_ids:
            print(f"\n⚠️ Examples of invalid IDs:")
            for invalid_id in invalid_ids[:5]:
                print(f"  {invalid_id}")
        
        # Check for duplicates
        duplicates = question_ids.duplicated().sum()
        if duplicates > 0:
            print(f"\n❌ Duplicate question IDs: {duplicates}")
    
    def analyze_dimensions(self, df):
        """Analyze dimension distribution and issues"""
        print("\n" + "="*60)
        print("DIMENSION ANALYSIS")
        print("="*60)
        
        if df is None or 'dimension' not in df.columns:
            print("❌ Cannot analyze - no dimension column")
            return
        
        dimensions = df['dimension'].dropna()
        dimension_counts = dimensions.value_counts()
        
        expected_dimensions = ['creativity', 'soft_skills', 'teamwork', 'hard_skills']
        
        print(f"📊 Total questions with dimensions: {len(dimensions)}")
        print(f"📊 Unique dimensions: {dimensions.nunique()}")
        
        print(f"\n📊 Distribution:")
        total = len(dimensions)
        for dim, count in dimension_counts.items():
            percentage = (count / total) * 100
            status = "✅" if dim in expected_dimensions else "❌"
            print(f"  {status} {dim}: {count} ({percentage:.1f}%)")
        
        # Check for unexpected dimensions
        unexpected = set(dimensions.unique()) - set(expected_dimensions)
        if unexpected:
            print(f"\n⚠️ Unexpected dimensions found: {list(unexpected)}")
        
        # Balance analysis
        if len(dimension_counts) > 1:
            max_count = dimension_counts.max()
            min_count = dimension_counts.min()
            imbalance_ratio = max_count / min_count
            print(f"\n⚖️ Balance analysis:")
            print(f"  Max: {max_count}, Min: {min_count}")
            print(f"  Imbalance ratio: {imbalance_ratio:.1f}:1")
            if imbalance_ratio > 3:
                print(f"  ❌ Severely imbalanced dataset!")
            elif imbalance_ratio > 2:
                print(f"  ⚠️ Moderately imbalanced dataset")
            else:
                print(f"  ✅ Well-balanced dataset")
    
    def analyze_subdimensions(self, df):
        """Analyze subdimension distribution"""
        print("\n" + "="*60)
        print("SUBDIMENSION ANALYSIS")
        print("="*60)
        
        if df is None or 'subdimension' not in df.columns:
            print("❌ Cannot analyze - no subdimension column")
            return
        
        subdims = df['subdimension'].dropna()
        print(f"📊 Total questions with subdimensions: {len(subdims)}")
        print(f"📊 Unique subdimensions: {subdims.nunique()}")
        
        # Group by dimension
        if 'dimension' in df.columns:
            print(f"\n📊 Subdimensions by dimension:")
            for dim in df['dimension'].unique():
                if pd.notna(dim):
                    dim_subdims = df[df['dimension'] == dim]['subdimension'].dropna().unique()
                    print(f"  {dim}: {len(dim_subdims)} subdimensions")
                    for subdim in sorted(dim_subdims)[:5]:  # Show first 5
                        count = len(df[(df['dimension'] == dim) & (df['subdimension'] == subdim)])
                        print(f"    - {subdim}: {count}")
                    if len(dim_subdims) > 5:
                        print(f"    ... and {len(dim_subdims) - 5} more")
    
    def analyze_questions(self, df):
        """Analyze question text quality and issues"""
        print("\n" + "="*60)
        print("QUESTION TEXT ANALYSIS")
        print("="*60)
        
        if df is None or 'question_text' not in df.columns:
            print("❌ Cannot analyze - no question_text column")
            return
        
        questions = df['question_text'].dropna()
        print(f"📊 Total questions with text: {len(questions)}")
        
        # Analyze question patterns
        patterns = {
            'how_confident': 0,
            'how_well': 0,
            'how_often': 0,
            'how_comfortable': 0,
            'how_effectively': 0,
            'i_am_confident': 0,
            'i_can': 0,
            'other': 0
        }
        
        grammar_issues = []
        malformed_questions = []
        
        for idx, question in enumerate(questions):
            if pd.isna(question):
                continue
                
            q_str = str(question).strip()
            q_lower = q_str.lower()
            
            # Pattern matching
            if q_lower.startswith('how confident'):
                patterns['how_confident'] += 1
            elif q_lower.startswith('how well'):
                patterns['how_well'] += 1
            elif q_lower.startswith('how often'):
                patterns['how_often'] += 1
            elif q_lower.startswith('how comfortable'):
                patterns['how_comfortable'] += 1
            elif q_lower.startswith('how effectively'):
                patterns['how_effectively'] += 1
            elif q_lower.startswith('i am confident'):
                patterns['i_am_confident'] += 1
            elif q_lower.startswith('i can'):
                patterns['i_can'] += 1
            else:
                patterns['other'] += 1
            
            # Check for grammar issues
            if 'how effectively can you ' in q_lower and ' perform ' not in q_lower:
                if len(grammar_issues) < 5:
                    grammar_issues.append(q_str)
            
            # Check for malformed questions (embedded data)
            if '""' in q_str or len(q_str.split(',')) > 2:
                if len(malformed_questions) < 5:
                    malformed_questions.append(q_str[:100] + "..." if len(q_str) > 100 else q_str)
        
        print(f"\n📊 Question patterns:")
        for pattern, count in patterns.items():
            if count > 0:
                percentage = (count / len(questions)) * 100
                print(f"  {pattern.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        if grammar_issues:
            print(f"\n⚠️ Grammar issues found ({len(grammar_issues)} examples):")
            for issue in grammar_issues:
                print(f"  - {issue}")
        
        if malformed_questions:
            print(f"\n❌ Malformed questions found ({len(malformed_questions)} examples):")
            for malformed in malformed_questions:
                print(f"  - {malformed}")
    
    def analyze_target_years(self, df):
        """Analyze target year level distribution"""
        print("\n" + "="*60)
        print("TARGET YEAR LEVEL ANALYSIS")
        print("="*60)
        
        if df is None or 'target_year_level' not in df.columns:
            print("❌ Cannot analyze - no target_year_level column")
            return
        
        years = df['target_year_level'].dropna()
        year_counts = years.value_counts()
        
        print(f"📊 Total questions with year levels: {len(years)}")
        print(f"📊 Distribution:")
        
        for year, count in sorted(year_counts.items()):
            percentage = (count / len(years)) * 100
            print(f"  Year {year}: {count} ({percentage:.1f}%)")
        
        # Check for invalid values
        expected_years = ['1', '2', '3', 1, 2, 3]
        invalid_years = [y for y in years.unique() if y not in expected_years]
        if invalid_years:
            print(f"\n⚠️ Invalid year levels found: {invalid_years}")
    
    def generate_summary_report(self, df):
        """Generate overall summary report"""
        print("\n" + "="*60)
        print("SUMMARY REPORT")
        print("="*60)
        
        if df is None:
            print("❌ Cannot generate summary - dataset failed to load properly")
            return
        
        total_rows = len(df)
        total_cols = len(df.columns)
        
        print(f"📊 Dataset Overview:")
        print(f"  Total rows: {total_rows}")
        print(f"  Total columns: {total_cols}")
        print(f"  Expected columns: 6")
        print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Data quality assessment
        issues = []
        
        if total_cols != 6:
            issues.append(f"Wrong number of columns ({total_cols} instead of 6)")
        
        # Check for missing values
        missing_data = df.isnull().sum()
        if missing_data.any():
            issues.append(f"Missing values found")
        
        # Check dimension balance
        if 'dimension' in df.columns:
            dim_counts = df['dimension'].value_counts()
            if len(dim_counts) > 1:
                imbalance_ratio = dim_counts.max() / dim_counts.min()
                if imbalance_ratio > 3:
                    issues.append(f"Severely imbalanced dimensions (ratio: {imbalance_ratio:.1f}:1)")
        
        print(f"\n🔍 Data Quality Assessment:")
        if not issues:
            print("  ✅ No major issues detected")
        else:
            for issue in issues:
                print(f"  ❌ {issue}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if total_rows < 500:
            print("  📈 Consider generating more questions for better model training")
        
        if 'dimension' in df.columns:
            dim_counts = df['dimension'].value_counts()
            if len(dim_counts) > 1 and dim_counts.max() / dim_counts.min() > 2:
                print("  ⚖️ Balance the dataset across dimensions")
        
        print("  🧹 Clean malformed CSV rows")
        print("  📝 Fix grammar issues in questions")
        print("  🔍 Remove duplicate questions")
    
    def run_analysis(self):
        """Run complete analysis"""
        print("🔍 DATASET ANALYSIS STARTING")
        print("="*60)
        
        # Load dataset
        df, load_method = self.load_dataset()
        
        # Analyze file structure
        self.analyze_file_structure()
        
        if df is not None:
            # Analyze data content
            self.analyze_question_ids(df)
            self.analyze_dimensions(df)
            self.analyze_subdimensions(df)
            self.analyze_questions(df)
            self.analyze_target_years(df)
            
            # Generate summary
            self.generate_summary_report(df)
        
        print("\n" + "="*60)
        print("🎯 ANALYSIS COMPLETE")
        print("="*60)

def main():
    analyzer = DatasetAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
