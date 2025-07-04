import json
from openai import OpenAI
import PyPDF2

# --- SETUP API CLIENT ---
client = OpenAI(
    api_key="sk-c4ab21567aaf41de8680eaec02220f0f",  # Replace with your actual key
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
You are an AI assistant that generates self-assessment questions for students.

The teacher has provided the following prompt:
"{teacher_prompt}"

Guidelines:
- Generate as many relevant **self-assessment** questions as needed based on the prompt.
- Each question should be clearly worded.
- Each question must have the same answer options: ["Bad", "Average", "Excellent"]
- Format the result as a JSON array, like this:

[
  {{
    "question": "How confident are you in applying basic cybersecurity principles?",
    "choices": ["Bad", "Average", "Excellent"]
  }},
  {{
    "question": "How well do you understand data encryption methods?",
    "choices": ["Bad", "Average", "Excellent"]
  }}
]

--- Reference Question Bank ---
{reference_text}
--- End Reference ---

Now, generate the questions:
"""

# --- MAIN EXECUTION LOOP ---
pdf_path = "/workspaces/Stage/Models/Question Generation/Evaluation_Question_Bank.pdf"
reference_text = extract_text_from_pdf(pdf_path)

print("=== AI Self-Assessment Question Generator ===")
print("Type 'exit' or press Enter without typing anything to quit.\n")

while True:
    teacher_prompt = input("Enter your evaluation request: ").strip()
    if teacher_prompt.lower() == "exit" or teacher_prompt == "":
        print("Exiting... Goodbye!")
        break

    final_prompt = build_prompt(reference_text, teacher_prompt)

    try:
        # Send prompt to DeepSeek AI
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates self-assessment questions."},
                {"role": "user", "content": final_prompt}
            ],
            stream=False
        )

        content = response.choices[0].message.content.strip()

        # Debug print raw content
        print("\nRaw AI Response:\n", content)

        # Try to parse response
        questions_list = json.loads(content)

        # Display results
        output = {
            "teacher_prompt": teacher_prompt,
            "generated_questions": questions_list
        }

        print("\nGenerated Self-Assessment Questions:\n")
        print(json.dumps(output, indent=2, ensure_ascii=False))

        # Save to file
        with open("self_assessment_questions.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            print("\n📁 Saved to self_assessment_questions.json\n")

    except json.JSONDecodeError:
        print("\n Error: Failed to parse JSON. Here's the raw output:\n")
        print(content)
        print("\nPlease check your prompt and try again.\n")

    except Exception as e:
        print(f"\n Unexpected Error: {e}")
        print("Please try again.\n")
