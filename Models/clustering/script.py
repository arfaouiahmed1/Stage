import pandas as pd

# Load the full dataset
df = pd.read_csv('students_dataset.csv')

# Filter students who are in class '3B88'
students_3B88 = df[df['class'] == '3B88']

# Show the first few rows (optional)
print(students_3B88.head())

# Save the filtered data to a new CSV (optional)
students_3B88.to_csv('students_3B88.csv', index=False)

print(f"{len(students_3B88)} students found in class 3B88.")
# Save the filtered data to a new CSV file
students_3B88.to_csv('students_3B88.csv', index=False)

print(f"Saved {len(students_3B88)} students from class 3B88 to 'students_3B88.csv'")
