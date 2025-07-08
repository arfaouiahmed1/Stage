import random
import csv

# === Configuration ===
NUM_STUDENTS = 40  # You can change this
CATEGORIES = ["Hard Skills", "Soft Skills", "Creativity", "Teamwork"]

# === Random name generator ===
first_names = ["Alice", "Bob", "Clara", "Daniel", "Eva", "Faris", "Grace", "Hassan", "Ines", "Jamal", "Khadija", "Leo", "Maya", "Nabil", "Omar", "Paul", "Quinn", "Rania", "Sara", "Tariq"]
last_names = ["Smith", "Johnson", "Lee", "Brown", "Jones", "Garcia", "Miller", "Davis", "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Lopez", "Ali", "Ben Ali", "Jouini", "Cherif", "Kacem"]

def generate_name():
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# === Generate student data ===
students = []
for _ in range(NUM_STUDENTS):
    name = generate_name()
    class_id = random.randint(1, 4)
    scores = {category: round(random.uniform(1.5, 5.0), 2) for category in CATEGORIES}
    students.append({
        "Name": name,
        "Class": class_id,
        **scores
    })

# === Save to CSV ===
output_file = "synthetic_students.csv"
with open(output_file, mode="w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Class"] + CATEGORIES)
    writer.writeheader()
    writer.writerows(students)

print(f"✅ Data saved to {output_file}")
