import csv
import random
import faker

# Initialize Faker for realistic first and last names
fake = faker.Faker()

# Some sample nationalities (expand as needed)
nationalities = [
    "Tunisian", "Moroccan", "Senegalese", "Cameroonian", "Algerian", "Egyptian", "Libyan", "Malian"
]

# Classes (just repeating some classes like '3B88', '1A100' for example)
classes = ["3B88", "1A100", "2C55", "4D20"]

# Gender distribution roughly balanced
genders = ["Male", "Female"]

def generate_student():
    first_name = fake.first_name()
    last_name = fake.last_name()
    gender = random.choice(genders)
    age = random.randint(18, 45)  # typical student age range
    
    nationality = random.choice(nationalities)
    
    # Skill scores between 0 and 5, some variation
    hard_skills = round(random.uniform(0, 5), 2)
    soft_skills = round(random.uniform(0, 5), 2)
    teamwork = round(random.uniform(0, 5), 2)
    creativity = round(random.uniform(0, 5), 2)
    
    # Class randomly assigned
    class_name = random.choice(classes)
    
    return [first_name, last_name, gender, age, nationality, hard_skills, soft_skills, teamwork, creativity, class_name]

# Write to CSV
with open("students_1500.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(["first_name", "last_name", "gender", "age", "nationality", "hard_skills", "soft_skills", "teamwork", "creativity", "class"])
    
    # Write 1500 students
    for _ in range(1500):
        writer.writerow(generate_student())

print("Generated students_1500.csv with 1500 students")
