import json
import streamlit as st
from openai import OpenAI
import PyPDF2

# ========== SETUP ==========
client = OpenAI(
    api_key="sk-c4ab21567aaf41de8680eaec02220f0f",  # Replace with your key
    base_url="https://api.deepseek.com"
)

@st.cache_data
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

def extract_json_from_text(text):
    """Extract JSON array from text, handling extra text around it."""
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1:
        json_str = text[start:end+1]
        return json.loads(json_str)
    else:
        raise ValueError("No JSON array found in the response.")

# ========== UI CONFIG ==========
st.set_page_config(page_title="AI Self-Assessment Generator", layout="wide")
st.title("🧠 AI Self-Assessment Question Generator")

# ========== CONFIG DATA ==========
categories = {
    "Hard Skills": ["Programming", "Data Analysis", "Cybersecurity", "Database Management"],
    "Soft Skills": ["Communication", "Time Management", "Adaptability", "Leadership"],
    "Creativity": ["Idea Generation", "Design Thinking", "Storytelling"],
    "Teamwork": ["Collaboration", "Conflict Resolution", "Peer Feedback"]
}

difficulty_levels = ["Beginner", "Intermediate", "Advanced"]

# ========== INPUT STEPS ==========
category = st.selectbox("📂 Choose a category", list(categories.keys()))
subcategory = st.selectbox("🧩 Choose a sub-category", categories[category])
difficulty = st.selectbox("🎯 Select level of difficulty", difficulty_levels)
num_questions = st.number_input("🔢  Number of questions", min_value=1, max_value=10, value=3, step=1)
prompt = st.text_area(
    "✏️  Write your custom prompt (optional)", 
    placeholder="e.g., Generate self-assessment questions on effective team collaboration"
)

if st.button("🚀  Generate Questions"):
    # Load reference question bank text once
    reference_text = extract_text_from_pdf("Models/Question Generation/Evaluation_Question_Bank.pdf")

    # Build the prompt dynamically
    full_prompt = f"""
You are an AI that generates self-assessment questions for students.

Context:
- Category: {category}
- Subcategory: {subcategory}
- Difficulty: {difficulty}
- Number of questions: {num_questions}
"""

    if prompt.strip():
        full_prompt += f'- Custom prompt: "{prompt.strip()}"\n'

    full_prompt += f"""
Instructions:
- Generate {num_questions} self-assessment questions on this topic.
- Each question must have answer options: ["Bad", "Average", "Excellent"]
- Format the output as a JSON array:

[
  {{
    "question": "...",
    "choices": ["Bad", "Average", "Excellent"]
  }},
  ...
]

Reference Question Bank:
{reference_text}
"""

    with st.spinner("🧠 Generating..."):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You generate editable self-assessment questions for teachers."},
                    {"role": "user", "content": full_prompt}
                ]
            )

            raw_output = response.choices[0].message.content.strip()

            try:
                questions = extract_json_from_text(raw_output)
                st.success("✅ Questions generated successfully!")

                st.markdown("### Edit Your Questions (optional)")
                updated_questions = []
                for idx, q in enumerate(questions):
                    edited = st.text_input(f"Q{idx + 1}", value=q["question"])
                    updated_questions.append({
                        "question": edited,
                        "choices": q["choices"]  # Keep fixed choices internally, no UI input
                    })

                final_output = {
                    "category": category,
                    "subcategory": subcategory,
                    "difficulty": difficulty,
                    "prompt": prompt,
                    "questions": updated_questions
                }

                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(final_output, indent=2, ensure_ascii=False),
                    file_name="self_assessment_questions.json",
                    mime="application/json"
                )

            except ValueError as e:
                st.error(f" Parsing error: {e}")
                st.code(raw_output)
            except json.JSONDecodeError:
                st.error(" JSON decode error. Raw output:")
                st.code(raw_output)

        except Exception as e:
            st.error(f" API Error: {e}")
