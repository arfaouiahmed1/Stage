import json
import re
from openai import OpenAI
import PyPDF2

# --- SETUP API CLIENT ---
client = OpenAI(
    api_key="sk-c4ab21567aaf41de8680eaec02220f0f",  # Replace with your key
    base_url="https://api.deepseek.com"
)

# --- FUNCTION: Extract text from reference PDF ---
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

# --- FUNCTION: Build prompt for AI generation ---
def build_prompt(reference_text, teacher_prompt):
    return f"""
You are an expert assistant helping teachers generate student evaluation questions.

Below is a categorized question bank used to evaluate students on a 1–5 scale:
(Hard Skills, Soft Skills, Team Spirit, and Creativity)

Use the style and structure from the reference to generate new evaluation questions based on the teacher’s request.

--- Reference Question Bank ---
{reference_text}
--- End Reference ---

Teacher's request:
"{teacher_prompt}"

Your task:
Generate 3–5 clear, measurable questions based on the request above.
Avoid repeating the reference questions. Use objective, formal wording.
"""

# --- MAIN EXECUTION LOOP ---
pdf_path = "C:/Users/EXTRA/Desktop/GameTeam/Evaluation_Question_Bank.pdf"  # Adjust this path if needed
reference_text = extract_text_from_pdf(pdf_path)

print("=== AI Student Evaluation Question Generator ===")
print("Type 'exit' or press Enter without typing anything to quit.\n")

while True:
    teacher_prompt = input("Enter your evaluation request: ").strip()
    if teacher_prompt.lower() == "exit" or teacher_prompt == "":
        print("Exiting... Goodbye!")
        break

    final_prompt = build_prompt(reference_text, teacher_prompt)

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates evaluation questions."},
                {"role": "user", "content": final_prompt}
            ],
            stream=False
        )

        # Extract and parse questions from response
        content = response.choices[0].message.content
        questions = re.findall(r"\d+\.\s*(.+)", content.strip())
        questions = [q.strip() for q in questions if q.strip()]

        # Build JSON structure
        json_output = {
            "teacher_prompt": teacher_prompt,
            "generated_questions": questions
        }

        # Print nicely
        print("\n Generated Questions in JSON format:\n")
        print(json.dumps(json_output, indent=2, ensure_ascii=False))

        # Save to file
        with open("generated_questions.json", "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)
            print(" Saved to generated_questions.json\n")

    except Exception as e:
        print(f" Error generating questions: {e}")
        print("Please check your API key, internet connection, or try again.\n")
