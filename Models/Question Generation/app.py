import json
import streamlit as st
from openai import OpenAI
import PyPDF2

# --- SETUP API CLIENT ---
client = OpenAI(
    api_key="sk-c4ab21567aaf41de8680eaec02220f0f",  # Replace with your API key
    base_url="https://api.deepseek.com"
)

# --- FUNCTION: Extract text from reference PDF ---
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

# --- Load Reference Question Bank ---
pdf_path = "/workspaces/Stage/Models/Question Generation/Evaluation_Question_Bank.pdf"
reference_text = extract_text_from_pdf(pdf_path)

# --- Streamlit UI ---
st.title(" AI Self-Assessment Question Generator")
st.write("Generate self-evaluation questions like:")

teacher_prompt = st.text_area("✏️ Enter your prompt:", height=150, placeholder="e.g., Generate 3 self-assessment questions on communication skills")

if st.button(" Generate Questions"):
    if teacher_prompt.strip() == "":
        st.warning("Please enter a prompt before generating.")
    else:
        final_prompt = build_prompt(reference_text, teacher_prompt)

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates self-assessment questions."},
                    {"role": "user", "content": final_prompt}
                ],
                stream=False
            )

            content = response.choices[0].message.content.strip()

            try:
                questions_list = json.loads(content)
                st.success(" Questions generated successfully!")

                # Display Questions
                for idx, q in enumerate(questions_list, 1):
                    st.markdown(f"**Q{idx}:** {q['question']}")
                    st.markdown(f"Choices: {', '.join(q['choices'])}")

                # Download Button
                output = {
                    "teacher_prompt": teacher_prompt,
                    "generated_questions": questions_list
                }
                st.download_button(
                    label=" Download as JSON",
                    data=json.dumps(output, indent=2, ensure_ascii=False),
                    file_name="self_assessment_questions.json",
                    mime="application/json"
                )

            except json.JSONDecodeError:
                st.error("Failed to parse AI response. Here's the raw output:")
                st.code(content)

        except Exception as e:
            st.error(f" Error: {e}")
