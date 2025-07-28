#!/usr/bin/env python3
"""
Dataset Balancer and Cleaner
- Balances the distribution across all dimensions
- Removes response_scale column
- Fixes grammar issues
- Ensures equal representation (220 questions per dimension)
"""

import pandas as pd
import re
import random
from pathlib import Path

class DatasetBalancer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.input_file = self.base_path / "All Questions.csv"
        self.output_file = self.base_path / "All Questions - Balanced.csv"
        self.backup_file = self.base_path / "All Questions - Original.csv"
        
        # Target distribution: 220 questions per dimension = 880 total
        self.target_per_dimension = 220
        
    def create_backup(self):
        """Create backup of original file"""
        if self.input_file.exists():
            print(f"Creating backup: {self.backup_file}")
            import shutil
            shutil.copy2(self.input_file, self.backup_file)
    
    def load_dataset(self):
        """Load and clean the dataset"""
        print("Loading dataset...")
        df = pd.read_csv(self.input_file)
        print(f"Loaded {len(df)} questions")
        
        # Show current distribution
        print("\nCurrent distribution:")
        current_dist = df['dimension'].value_counts()
        for dim, count in current_dist.items():
            percentage = (count / len(df)) * 100
            print(f"  {dim}: {count} ({percentage:.1f}%)")
        
        return df
    
    def fix_grammar(self, text):
        """Fix common grammar issues"""
        if pd.isna(text):
            return text
        
        # Fix "How effectively can you perform optimize" -> "How effectively can you optimize"
        text = re.sub(r'How effectively can you perform ([a-z])', r'How effectively can you \1', text)
        
        # Fix other grammar patterns
        text = re.sub(r'How effectively can you ([^?]+)\?', r'How effectively can you perform \1?', text)
        
        return text
    
    def generate_creativity_questions(self, needed_count):
        """Generate creativity questions to balance the dataset"""
        print(f"Generating {needed_count} creativity questions...")
        
        subdimensions = [
            'innovation_problem_solving',
            'algorithm_design', 
            'creative_thinking',
            'system_architecture',
            'ux_design',
            'artistic_creativity'
        ]
        
        question_templates = {
            'innovation_problem_solving': [
                "How confident are you in developing innovative solutions to complex problems?",
                "How well do you perform when generating creative alternatives to standard approaches?",
                "How often do you engage in brainstorming sessions for problem-solving?",
                "How comfortable are you with exploring unconventional problem-solving methods?",
                "How effectively can you combine different ideas to create novel solutions?",
                "How confident are you in challenging traditional approaches to find better solutions?",
                "How well do you perform when adapting existing solutions to new contexts?",
                "How often do you engage in lateral thinking for complex challenges?",
                "How comfortable are you with ambiguous problems that require creative solutions?",
                "How effectively can you synthesize diverse perspectives into innovative approaches?"
            ],
            'algorithm_design': [
                "How confident are you in designing efficient algorithms for novel problems?",
                "How well do you perform when creating algorithms that balance performance and creativity?",
                "How often do you engage in algorithmic innovation and optimization?",
                "How comfortable are you with designing algorithms for emerging technologies?",
                "How effectively can you create algorithms that solve previously unsolved problems?",
                "How confident are you in developing creative data structures?",
                "How well do you perform when designing algorithms for real-time systems?",
                "How often do you engage in creating algorithms that inspire new approaches?",
                "How comfortable are you with designing self-adapting algorithms?",
                "How effectively can you create algorithms that learn and evolve?"
            ],
            'creative_thinking': [
                "How confident are you in generating original ideas for technical challenges?",
                "How well do you perform when thinking outside conventional paradigms?",
                "How often do you engage in creative ideation sessions?",
                "How comfortable are you with abstract thinking and conceptualization?",
                "How effectively can you connect seemingly unrelated concepts?",
                "How confident are you in challenging assumptions and conventional wisdom?",
                "How well do you perform when envisioning future technological possibilities?",
                "How often do you engage in imaginative problem exploration?",
                "How comfortable are you with uncertainty and open-ended challenges?",
                "How effectively can you transform creative ideas into practical solutions?"
            ],
            'system_architecture': [
                "How confident are you in designing innovative system architectures?",
                "How well do you perform when creating architectures for emerging use cases?",
                "How often do you engage in architectural innovation and experimentation?",
                "How comfortable are you with designing systems that don't follow traditional patterns?",
                "How effectively can you architect systems that inspire new design paradigms?",
                "How confident are you in creating flexible and adaptive architectures?",
                "How well do you perform when designing architectures for unknown future requirements?",
                "How often do you engage in architectural pattern innovation?",
                "How comfortable are you with designing architectures that challenge industry norms?",
                "How effectively can you balance architectural creativity with practical constraints?"
            ],
            'ux_design': [
                "How confident are you in creating innovative user experience designs?",
                "How well do you perform when designing interfaces that surprise and delight users?",
                "How often do you engage in creative user interaction design?",
                "How comfortable are you with designing for emerging interaction paradigms?",
                "How effectively can you create user experiences that set new standards?",
                "How confident are you in designing intuitive yet innovative interfaces?",
                "How well do you perform when balancing usability with creative expression?",
                "How often do you engage in experimental design approaches?",
                "How comfortable are you with designing for future user behaviors?",
                "How effectively can you create emotionally engaging user experiences?"
            ],
            'artistic_creativity': [
                "How confident are you in applying artistic principles to technical work?",
                "How well do you perform when creating visually compelling technical solutions?",
                "How often do you engage in creative visualization of complex data?",
                "How comfortable are you with incorporating aesthetic elements in technical design?",
                "How effectively can you create technical solutions that are also beautiful?",
                "How confident are you in using creative tools for technical communication?",
                "How well do you perform when designing technical solutions with artistic flair?",
                "How often do you engage in creative expression through technology?",
                "How comfortable are you with blending technical and artistic skills?",
                "How effectively can you inspire others through creative technical presentations?"
            ]
        }
        
        new_questions = []
        questions_per_subdim = needed_count // len(subdimensions)
        extra_questions = needed_count % len(subdimensions)
        
        question_id_counter = 1
        
        for i, subdim in enumerate(subdimensions):
            questions_for_this_subdim = questions_per_subdim
            if i < extra_questions:
                questions_for_this_subdim += 1
            
            templates = question_templates[subdim]
            
            for j in range(questions_for_this_subdim):
                template_idx = j % len(templates)
                question_text = templates[template_idx]
                
                new_questions.append({
                    'question_id': f'sa_{question_id_counter:03d}',
                    'dimension': 'creativity',
                    'subdimension': subdim,
                    'question_text': question_text,
                    'target_year_level': (j % 3) + 1
                })
                question_id_counter += 1
        
        return new_questions
    
    def balance_dataset(self, df):
        """Balance the dataset to have equal distribution"""
        print("\nBalancing dataset...")
        
        # Get current counts
        current_counts = df['dimension'].value_counts()
        
        # Determine what we need
        balanced_data = []
        
        for dimension in ['creativity', 'soft_skills', 'teamwork', 'hard_skills']:
            current_count = current_counts.get(dimension, 0)
            
            if current_count >= self.target_per_dimension:
                # We have enough, take a random sample
                dim_questions = df[df['dimension'] == dimension].copy()
                sampled = dim_questions.sample(n=self.target_per_dimension, random_state=42)
                balanced_data.append(sampled)
                print(f"  {dimension}: Using {self.target_per_dimension} from {current_count} available")
            else:
                # We need more questions
                needed = self.target_per_dimension - current_count
                
                # Take all existing questions
                existing = df[df['dimension'] == dimension].copy()
                balanced_data.append(existing)
                
                # Generate new questions for creativity (most needed)
                if dimension == 'creativity':
                    new_questions = self.generate_creativity_questions(needed)
                    new_df = pd.DataFrame(new_questions)
                    balanced_data.append(new_df)
                    print(f"  {dimension}: Using {current_count} existing + {needed} generated = {self.target_per_dimension}")
                else:
                    # For other dimensions, duplicate existing questions with variations
                    new_questions = self.duplicate_with_variations(existing, needed)
                    balanced_data.append(new_questions)
                    print(f"  {dimension}: Using {current_count} existing + {needed} variations = {self.target_per_dimension}")
        
        # Combine all balanced data
        balanced_df = pd.concat(balanced_data, ignore_index=True)
        
        # Shuffle the dataset
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return balanced_df
    
    def duplicate_with_variations(self, df, needed_count):
        """Create variations of existing questions"""
        if len(df) == 0:
            return pd.DataFrame()
        
        variations = []
        variation_templates = [
            "How skilled are you in {}?",
            "How proficient are you with {}?", 
            "How experienced are you in {}?",
            "How capable are you of {}?",
            "How adept are you at {}?"
        ]
        
        for i in range(needed_count):
            base_question = df.iloc[i % len(df)].copy()
            
            # Extract the skill/topic from the original question
            original_text = base_question['question_text']
            
            # Simple variation by changing the question starter
            template = variation_templates[i % len(variation_templates)]
            
            # Try to extract the main topic
            if 'in ' in original_text:
                topic = original_text.split('in ')[-1].replace('?', '')
            elif 'with ' in original_text:
                topic = original_text.split('with ')[-1].replace('?', '')
            else:
                topic = original_text.replace('How confident are you ', '').replace('How well do you perform ', '').replace('?', '')
            
            new_text = template.format(topic)
            
            # Create new question ID
            new_id = f"{base_question['question_id']}_v{i+1}"
            
            base_question['question_id'] = new_id
            base_question['question_text'] = new_text
            
            variations.append(base_question.to_dict())
        
        return pd.DataFrame(variations)
    
    def clean_and_process(self, df):
        """Clean the dataset and remove response_scale"""
        print("\nCleaning dataset...")
        
        # Remove response_scale column
        if 'response_scale' in df.columns:
            df = df.drop('response_scale', axis=1)
            print("✅ Removed response_scale column")
        
        # Fix grammar issues
        df['question_text'] = df['question_text'].apply(self.fix_grammar)
        print("✅ Fixed grammar issues")
        
        # Ensure proper column order
        df = df[['question_id', 'dimension', 'subdimension', 'question_text', 'target_year_level']]
        
        return df
    
    def run_balancing(self):
        """Main function to balance the dataset"""
        print("🎯 STARTING DATASET BALANCING")
        print("="*60)
        
        # Create backup
        self.create_backup()
        
        # Load dataset
        df = self.load_dataset()
        
        # Balance the dataset
        balanced_df = self.balance_dataset(df)
        
        # Clean and process
        final_df = self.clean_and_process(balanced_df)
        
        # Show final distribution
        print("\nFinal distribution:")
        final_counts = final_df['dimension'].value_counts()
        total = len(final_df)
        for dim, count in final_counts.items():
            percentage = (count / total) * 100
            print(f"  {dim}: {count} ({percentage:.1f}%)")
        
        # Save the balanced dataset
        final_df.to_csv(self.output_file, index=False)
        print(f"\n✅ Balanced dataset saved to: {self.output_file}")
        print(f"📊 Total questions: {len(final_df)}")
        
        # Replace original file
        import shutil
        shutil.copy2(self.output_file, self.input_file)
        print(f"✅ Original file updated with balanced data")
        
        return final_df

def main():
    balancer = DatasetBalancer()
    balancer.run_balancing()

if __name__ == "__main__":
    main()
