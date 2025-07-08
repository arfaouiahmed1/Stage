# Git Commands to Push Your Work

## Current Repository Structure:
```
Stage/
├── Datasets/
│   └── Soft skills questions generation/
│       ├── soft_skills_assessment.ipynb
│       ├── README.md
│       ├── .gitignore
│       ├── all_soft_skills_questions.csv
│       ├── communication_questions.csv
│       ├── leadership_questions.csv
│       ├── time_management_questions.csv
│       ├── analytical_questions.csv
│       ├── student_group_assignments.csv
│       └── complete_student_analysis.csv
├── Deployments/
└── Models/
```

## Commands to Execute:

### 1. Navigate to your repository
```bash
cd "C:\Users\MSI\OneDrive - ESPRIT\Bureau\4DS ESPRIT\StageESPRIT\Stage"
```

### 2. Check current branch (should be 'Siwar')
```bash
git branch
```

### 3. Add all changes to staging
```bash
git add .
```

### 4. Commit your changes
```bash
git commit -m "Add Soft Skills Questions Generation module

- Complete soft skills assessment and clustering system
- Adapted for Tunisian IT engineering students (moyenne 0-20)
- 4 clusters with groups of 5 students
- Question generation with templates and Hugging Face API
- Comprehensive CSV datasets and documentation
- Clean organized structure in Datasets folder"
```

### 5. Push to GitHub on Siwar branch
```bash
git push origin Siwar
```

## Verification Commands:

### Check what files will be committed:
```bash
git status
```

### Check differences:
```bash
git diff --cached
```

### Check remote repository:
```bash
git remote -v
```

## Important Notes:

✅ **Your Hugging Face token is safely in .gitignore**
✅ **All necessary files are organized in the correct folder**
✅ **Clean structure with only relevant files**
✅ **Comprehensive README documentation**

The .gitignore file will prevent your token from being pushed to GitHub while keeping it accessible locally for development.
