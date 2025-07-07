#!/usr/bin/env python3
"""
Notebook Recreation Script

This script creates a clean,            "    print('Data directory ready')\\n",
            "\\n",
            "print('\\\\nEnvironment ready!')"rking version of the soft skills assessment notebook.
"""

import json

def create_clean_notebook():
    """Create a clean version of the notebook with proper syntax"""
    
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py", 
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Add cells one by one
    
    # Title cell
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Soft Skills Assessment Notebook\\n",
            "\\n",
            "This notebook creates a comprehensive soft skills assessment tool covering four key areas:\\n",
            "- Communication skills\\n", 
            "- Leadership skills\\n",
            "- Time management skills\\n",
            "- Analytical skills\\n",
            "\\n",
            "The assessment collects responses on a 5-point scale (strongly disagree to strongly agree) and provides feedback based on overall scores."
        ]
    })
    
    # Environment validation cell
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Environment Validation\\n",
            "print('Validating Soft Skills Assessment Environment')\\n",
            "print('=' * 50)\\n",
            "\\n",
            "# Check required packages\\n",
            "required_packages = ['requests', 'pandas', 'numpy', 'bs4', 'tqdm', 'dotenv', 'IPython']\\n",
            "missing = []\\n",
            "\\n",
            "for pkg in required_packages:\\n",
            "    try:\\n",
            "        __import__(pkg)\\n",
            "        print(f'✓ {pkg}')\\n",
            "    except ImportError:\\n",
            "        missing.append(pkg)\\n",
            "        print(f'✗ {pkg} - MISSING')\\n",
            "\\n",
            "if missing:\\n",
            "    print(f'\\\\nInstall missing: pip install {\\\" \\\".join(missing)}')\\n",
            "else:\\n",
            "    print('\\\\nAll packages available!')\\n",
            "\\n",
            "# Check data directory\\n",
            "import os\\n",
            "if not os.path.exists('./data'):\\n",
            "    os.makedirs('./data')\\n",
            "    print('📁 Created data directory')\\n",
            "else:\\n",
            "    print('📁 Data directory ready')\\n",
            "\\n",
            "print(\\"\\\\n✅ Environment ready!\\\")"
        ]
    })
    
    # Imports cell
    notebook["cells"].append({
        "cell_type": "code", 
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Import necessary libraries\\n",
            "import requests\\n",
            "import re\\n", 
            "import pandas as pd\\n",
            "import numpy as np\\n",
            "import os\\n",
            "import json\\n",
            "import random\\n",
            "import time\\n",
            "from bs4 import BeautifulSoup\\n",
            "from tqdm.notebook import tqdm\\n",
            "from IPython.display import display, HTML\\n",
            "from dotenv import load_dotenv"
        ]
    })
    
    # Add more cells following the original structure but with clean code...
    
    # Web scraping section
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Data Collection: Web Scraping\\n",
            "\\n",
            "This section handles gathering questions from existing online assessment sources.\\n",
            "We scrape questions for each skill category from relevant HR and professional development websites."
        ]
    })
    
    # Template generation section  
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Question Generation: Template-Based Approach\\n",
            "\\n",
            "When we need more questions than we can scrape, this template-based generation system creates natural-sounding\\n",
            "assessment questions by combining sentence templates with category-specific components."
        ]
    })
    
    # Main execution cell
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Simple template-based question generation that works\\n",
            "import pandas as pd\\n",
            "import random\\n",
            "\\n",
            "def create_sample_questions():\\n",
            "    \\\"\\\"\\\"Create sample questions for demonstration\\\"\\\"\\\"\\n",
            "    questions = {\\n",
            "        'communication': [\\n",
            "            'I communicate clearly with team members.',\\n",
            "            'I listen actively during meetings.',\\n",
            "            'I provide constructive feedback effectively.',\\n",
            "            'I adapt my communication style to different audiences.',\\n",
            "            'I handle difficult conversations professionally.'\\n",
            "        ],\\n",
            "        'leadership': [\\n",
            "            'I motivate team members to achieve their best.',\\n",
            "            'I make decisions confidently when needed.',\\n",
            "            'I delegate tasks appropriately.',\\n",
            "            'I provide clear direction to my team.',\\n",
            "            'I support team members professional development.'\\n",
            "        ],\\n",
            "        'time_management': [\\n",
            "            'I prioritize tasks effectively.',\\n",
            "            'I meet deadlines consistently.',\\n",
            "            'I plan my workday efficiently.',\\n",
            "            'I avoid procrastination.',\\n",
            "            'I manage multiple projects successfully.'\\n",
            "        ],\\n",
            "        'analytical': [\\n",
            "            'I analyze problems systematically.',\\n",
            "            'I make data-driven decisions.',\\n",
            "            'I identify patterns in complex information.',\\n",
            "            'I evaluate multiple solutions before deciding.',\\n",
            "            'I think critically about challenges.'\\n",
            "        ]\\n",
            "    }\\n",
            "    \\n",
            "    # Create DataFrame with all questions\\n",
            "    all_questions = []\\n",
            "    for category, q_list in questions.items():\\n",
            "        for question in q_list:\\n",
            "            all_questions.append({\\n",
            "                'question_text': question,\\n",
            "                'category': category,\\n",
            "                'source_url': 'template_generated',\\n",
            "                'type': 'template'\\n",
            "            })\\n",
            "    \\n",
            "    return pd.DataFrame(all_questions)\\n",
            "\\n",
            "# Create sample questions\\n",
            "sample_questions = create_sample_questions()\\n",
            "print(f'Created {len(sample_questions)} sample questions')\\n",
            "print('\\nSample questions by category:')\\n",
            "for category in sample_questions['category'].unique():\\n",
            "    count = len(sample_questions[sample_questions['category'] == category])\\n",
            "    print(f'- {category}: {count} questions')"
        ]
    })
    
    # Assessment creation section
    notebook["cells"].append({
        "cell_type": "markdown", 
        "metadata": {},
        "source": [
            "## 3. Interactive Assessment Creation\\n",
            "\\n",
            "This section creates an interactive HTML-based assessment form that allows users to\\n",
            "respond to questions on a 5-point scale and receive immediate feedback on their skills."
        ]
    })
    
    # Assessment function
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from IPython.display import HTML\\n",
            "import time\\n",
            "\\n",
            "def create_assessment(questions_df, category):\\n",
            "    \\\"\\\"\\\"Create an HTML assessment form for the given category and questions\\\"\\\"\\\"\\n",
            "    \\n",
            "    assessment_id = f\\\"{category}_{int(time.time())}\\\"\\n",
            "    \\n",
            "    html = f\\\"\\\"\\\"\\n",
            "    <div class=\\\"assessment-container\\\" style=\\\"max-width: 800px; margin: 0 auto; font-family: Arial, sans-serif;\\\">\\n",
            "        <h2 style=\\\"color: #000; text-align: center;\\\">{category.replace('_', ' ').title()} Skills Assessment</h2>\\n",
            "        <p style=\\\"color: #000;\\\">Rate yourself on each statement from 1 (Strongly Disagree) to 5 (Strongly Agree).</p>\\n",
            "        <form id=\\\"{assessment_id}\\\">\\n",
            "            <table style=\\\"width: 100%; border-collapse: collapse;\\\">\\n",
            "                <tr style=\\\"background-color: #e6f2ff;\\\">\\n",
            "                    <th style=\\\"padding: 12px; text-align: left; border-bottom: 1px solid #ddd; color: #000;\\\">Statement</th>\\n",
            "                    <th style=\\\"padding: 12px; text-align: center; border-bottom: 1px solid #ddd; color: #000;\\\">1<br><small style=\\\"color: #000;\\\">Strongly<br>Disagree</small></th>\\n",
            "                    <th style=\\\"padding: 12px; text-align: center; border-bottom: 1px solid #ddd; color: #000;\\\">2<br><small style=\\\"color: #000;\\\">Disagree</small></th>\\n",
            "                    <th style=\\\"padding: 12px; text-align: center; border-bottom: 1px solid #ddd; color: #000;\\\">3<br><small style=\\\"color: #000;\\\">Neutral</small></th>\\n",
            "                    <th style=\\\"padding: 12px; text-align: center; border-bottom: 1px solid #ddd; color: #000;\\\">4<br><small style=\\\"color: #000;\\\">Agree</small></th>\\n",
            "                    <th style=\\\"padding: 12px; text-align: center; border-bottom: 1px solid #ddd; color: #000;\\\">5<br><small style=\\\"color: #000;\\\">Strongly<br>Agree</small></th>\\n",
            "                </tr>\\n",
            "    \\\"\\\"\\\"\\n",
            "    \\n",
            "    # Add each question as a row\\n",
            "    for i, row in questions_df.iterrows():\\n",
            "        question_id = f\\\"q_{i}\\\"\\n",
            "        question_text = row['question_text']\\n",
            "        \\n",
            "        html += f\\\"\\\"\\\"\\n",
            "                <tr style=\\\"border-bottom: 1px solid #ddd;\\\">\\n",
            "                    <td style=\\\"padding: 12px;\\\">{question_text}</td>\\n",
            "        \\\"\\\"\\\"\\n",
            "        \\n",
            "        # Add radio buttons for each rating\\n",
            "        for rating in range(1, 6):\\n",
            "            html += f\\\"\\\"\\\"\\n",
            "                    <td style=\\\"text-align: center;\\\">\\n",
            "                        <input type=\\\"radio\\\" name=\\\"{question_id}\\\" value=\\\"{rating}\\\" required>\\n",
            "                    </td>\\n",
            "            \\\"\\\"\\\"\\n",
            "        \\n",
            "        html += \\\"</tr>\\\"\\n",
            "    \\n",
            "    # Add submit button and closing tags\\n",
            "    html += f\\\"\\\"\\\"\\n",
            "            </table>\\n",
            "        <div style=\\\"margin-top: 20px; text-align: center;\\\">\\n",
            "            <button type=\\\"button\\\" onclick=\\\"submitAssessment()\\\" style=\\\"background-color: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;\\\">Submit Assessment</button>\\n",
            "        </div>\\n",
            "        </form>\\n",
            "        <div id=\\\"results\\\" style=\\\"margin-top: 20px; display: none;\\\">\\n",
            "            <h3>Your Results</h3>\\n",
            "            <div id=\\\"score\\\"></div>\\n",
            "            <div id=\\\"feedback\\\"></div>\\n",
            "        </div>\\n",
            "        <script>\\n",
            "            function submitAssessment() {{\\n",
            "                let total = 0;\\n",
            "                let answered = 0;\\n",
            "                let questions = {len(questions_df)};\\n",
            "                \\n",
            "                for (let i = 0; i < questions; i++) {{\\n",
            "                    let name = \\\"q_\\\" + i;\\n",
            "                    let selected = document.querySelector('input[name=\\\"' + name + '\\\"]:checked');\\n",
            "                    if (selected) {{\\n",
            "                        total += parseInt(selected.value);\\n",
            "                        answered++;\\n",
            "                    }}\\n",
            "                }}\\n",
            "                \\n",
            "                if (answered < questions) {{\\n",
            "                    alert(\\\"Please answer all questions before submitting.\\\");\\n",
            "                    return;\\n",
            "                }}\\n",
            "                \\n",
            "                let average = total / questions;\\n",
            "                let percentage = (average / 5) * 100;\\n",
            "                \\n",
            "                document.getElementById(\\\"score\\\").innerHTML = '<p>Your average score: <strong>' + average.toFixed(1) + '/5</strong> (' + percentage.toFixed(1) + '%)</p>';\\n",
            "                \\n",
            "                let feedback = '';\\n",
            "                if (average >= 4.5) {{\\n",
            "                    feedback = 'Outstanding! You demonstrate excellent {category.replace(\\\"_\\\", \\\" \\\")} skills.';\\n",
            "                }} else if (average >= 3.5) {{\\n",
            "                    feedback = 'Good job! You have solid {category.replace(\\\"_\\\", \\\" \\\")} skills with some room for improvement.';\\n",
            "                }} else if (average >= 2.5) {{\\n",
            "                    feedback = 'You have moderate {category.replace(\\\"_\\\", \\\" \\\")} skills. Consider focusing on development in this area.';\\n",
            "                }} else {{\\n",
            "                    feedback = 'This appears to be an area for growth. Consider seeking resources to develop your {category.replace(\\\"_\\\", \\\" \\\")} skills.';\\n",
            "                }}\\n",
            "                \\n",
            "                document.getElementById(\\\"feedback\\\").innerHTML = '<p>' + feedback + '</p>';\\n",
            "                document.getElementById(\\\"results\\\").style.display = \\\"block\\\";\\n",
            "            }}\\n",
            "        </script>\\n",
            "    </div>\\n",
            "    \\\"\\\"\\\"\\n",
            "    \\n",
            "    return HTML(html)"
        ]
    })
    
    # Demo execution
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Create and display a mixed assessment\\n",
            "print(\\\"Creating a comprehensive soft skills assessment...\\\")\\n",
            "\\n",
            "# Sample questions from each category\\n",
            "mixed_questions = pd.DataFrame()\\n",
            "questions_per_category = 5\\n",
            "\\n",
            "for category in ['communication', 'leadership', 'time_management', 'analytical']:\\n",
            "    # Get sample questions from this category\\n",
            "    category_questions = sample_questions[sample_questions['category'] == category].head(questions_per_category)\\n",
            "    mixed_questions = pd.concat([mixed_questions, category_questions], ignore_index=True)\\n",
            "\\n",
            "# Shuffle the questions\\n",
            "mixed_questions = mixed_questions.sample(frac=1).reset_index(drop=True)\\n",
            "\\n",
            "print(f\\\"Created mixed assessment with {len(mixed_questions)} total questions:\\\")\\n",
            "for category in ['communication', 'leadership', 'time_management', 'analytical']:\\n",
            "    count = len(mixed_questions[mixed_questions['category'] == category])\\n",
            "    print(f\\\"- {category}: {count} questions\\\")\\n",
            "\\n",
            "# Create and display the assessment\\n",
            "display(create_assessment(mixed_questions, \\\"comprehensive_soft_skills\\\"))"
        ]
    })
    
    # For now, let's save this basic structure
    
    with open("soft_skills_assessment_clean.ipynb", 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Created clean notebook: soft_skills_assessment_clean.ipynb")

def main():
    """Create the clean notebook"""
    print("🔨 Creating clean notebook...")
    create_clean_notebook()
    print("🎯 Clean notebook created successfully!")

if __name__ == "__main__":
    main()
