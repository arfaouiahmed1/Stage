import streamlit as st
import json
import os
import uuid
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from openai import OpenAI
import PyPDF2

# ========== CONFIGURATION ==========
QUIZ_STORAGE_FILE = "quizzes.json"
RESPONSES_STORAGE_FILE = "responses.json"

# === SETUP OPENAI CLIENT ===
client = OpenAI(
    api_key="sk-c4ab21567aaf41de8680eaec02220f0f",
    base_url="https://api.deepseek.com"
)

# ========== STATE MANAGEMENT ==========
def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if "quizzes" not in st.session_state:
    st.session_state.quizzes = load_data(QUIZ_STORAGE_FILE)

if "responses" not in st.session_state:
    st.session_state.responses = load_data(RESPONSES_STORAGE_FILE)

if "generated_questions" not in st.session_state:
    st.session_state.generated_questions = []

# ========== UTILITY FUNCTIONS ==========
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
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1:
        json_str = text[start:end+1]
        return json.loads(json_str)
    else:
        raise ValueError("No JSON array found in the response.")

def generate_quiz_id():
    return str(uuid.uuid4())[:8]

def generate_pdf(name, style, responses):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Personality Report - {name}", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Dominant Style: {style}", ln=True)
    pdf.ln(5)

    for i, (q, score) in enumerate(zip(questions, responses)):
        pdf.multi_cell(0, 10, f"Q{i+1}: {q}\nScore: {score}/3")
        pdf.ln(1)

    pdf.output("report.pdf")
    with open("report.pdf", "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="{name}_report.pdf">📄 Download PDF Report</a>'
    return href

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="AI Quiz Platform", layout="wide")
mode = st.sidebar.selectbox("Select Interface", ["Teacher", "Student"])

# ========== TEACHER INTERFACE ==========
if mode == "Teacher":
    st.title("👩‍🏫 Teacher Interface")

    st.header("📘 Create a New Quiz")

    categories = {
        "Hard Skills": ["Programming", "Data Analysis", "Cybersecurity", "Database Management"],
        "Soft Skills": ["Communication", "Time Management", "Adaptability", "Leadership"],
        "Creativity": ["Idea Generation", "Design Thinking", "Storytelling"],
        "Teamwork": ["Collaboration", "Conflict Resolution", "Peer Feedback"]
    }
    difficulty_levels = ["Beginner", "Intermediate", "Advanced"]

    # Category and Subcategory outside the form for dynamic update
    category = st.selectbox("📂 Choose Category", list(categories.keys()), key="cat")
    subcategory = st.selectbox("🧩 Choose Subcategory", categories[category], key="sub")

    # Rest of inputs inside the form
    with st.form("generate_quiz_form"):
        quiz_title = st.text_input("📝 Quiz Name", placeholder="Ex: Teamwork Assessment")
        difficulty = st.selectbox("🎯 Difficulty Level", difficulty_levels, key="difficulty")
        num_questions = st.slider("🔢 Number of Questions", 1, 10, 3)
        prompt = st.text_area("✏️ Custom prompt (optional)")
        submit_gen = st.form_submit_button("🚀 Generate Questions")

    if submit_gen:
        reference_text = extract_text_from_pdf("Models/Question Generation/Evaluation_Question_Bank.pdf")

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
- Generate {num_questions} self-assessment questions.
- Each question must have answer options: ["Bad", "Average", "Excellent"]
- Format output as JSON array:
[
  {{
    "question": "...",
    "choices": ["Bad", "Average", "Excellent"]
  }},
  ...
]
Reference:
{reference_text}
"""
        with st.spinner("Generating questions..."):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You generate editable self-assessment questions for teachers."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                raw_output = response.choices[0].message.content.strip()
                questions = extract_json_from_text(raw_output)
                st.session_state.generated_questions = questions
                st.success("✅ Questions generated!")

            except Exception as e:
                st.error(f"❌ Error: {e}")

    if st.session_state.generated_questions:
        st.subheader("✏️ Edit and Save Quiz")
        with st.form("save_quiz_form"):
            updated = []
            for idx, q in enumerate(st.session_state.generated_questions):
                new_q = st.text_input(f"Q{idx+1}", q["question"], key=f"edit_q_{idx}")
                updated.append({"question": new_q, "choices": q["choices"]})
            save_btn = st.form_submit_button("💾 Save Quiz")

        if save_btn:
            quiz_id = generate_quiz_id()
            st.session_state.quizzes[quiz_id] = {
                "title": quiz_title,
                "category": category,
                "subcategory": subcategory,
                "difficulty": difficulty,
                "prompt": prompt,
                "questions": updated
            }
            save_data(st.session_state.quizzes, QUIZ_STORAGE_FILE)
            st.success(f"✅ Quiz '{quiz_title}' saved!")
            st.session_state.generated_questions = []  # clear after save

    # === Monitor Submissions ===
    st.header("📊 Student Submissions")
    if not st.session_state.quizzes:
        st.info("No quizzes saved yet.")
    else:
        for qid, quiz in st.session_state.quizzes.items():
            st.subheader(f"📘 {quiz['title']}")
            responses = st.session_state.responses.get(qid, [])
            if not responses:
                st.write("No student submissions yet.")
            else:
                for resp in responses:
                    st.markdown(f"👤 **{resp['student']}** — Score: **{resp['score']}** / {len(quiz['questions']) * 3}")
                    with st.expander("View Answers"):
                        for idx, ans in enumerate(resp['answers']):
                            st.write(f"Q{idx+1}: {quiz['questions'][idx]['question']}")
                            st.write(f"Answer: {ans}")

# ========== STUDENT INTERFACE ==========
elif mode == "Student":
    st.title("🧠 Student Quiz Portal")
    student_name = st.text_input("👤 Your Name", placeholder="Enter your full name")

    available_quizzes = {qid: quiz["title"] for qid, quiz in st.session_state.quizzes.items()}

    if student_name and available_quizzes:
        selected_quiz_id = st.selectbox("📝 Choose Quiz", list(available_quizzes.keys()), format_func=lambda x: available_quizzes[x])
        quiz = st.session_state.quizzes[selected_quiz_id]

        st.subheader(f"📘 {quiz['title']} — {quiz['category']} / {quiz['subcategory']}")

        answers = []
        total_score = 0

        for idx, q in enumerate(quiz["questions"]):
            slider_val = st.slider(q["question"], 1, 3, 2, format="%d", key=f"slider_{idx}")
            answers.append(["Bad", "Average", "Excellent"][slider_val - 1])
            total_score += slider_val

        if st.button("🎯 Submit Quiz"):
            result = {
                "student": student_name,
                "score": total_score,
                "answers": answers
            }
            if selected_quiz_id not in st.session_state.responses:
                st.session_state.responses[selected_quiz_id] = []
            st.session_state.responses[selected_quiz_id].append(result)
            save_data(st.session_state.responses, RESPONSES_STORAGE_FILE)
            st.success(f"✅ Your score is {total_score} / {len(quiz['questions']) * 3}")

            # Calculate average score per question
            avg_score = total_score / len(quiz['questions'])

            # Map average score to personality style
            if avg_score <= 1.5:
                personality = "Reflective Thinker"
                description = "You tend to be thoughtful and introspective, carefully analyzing situations."
            elif avg_score <= 2.5:
                personality = "Balanced Achiever"
                description = "You have a balanced approach, combining effort and adaptability to succeed."
            else:
                personality = "Dynamic Leader"
                description = "You are confident, energetic, and often take charge in challenging situations."

            # Show personality result
            st.subheader("🧩 Your Personality Character")
            st.markdown(f"### **{personality}**")
            st.write(description)

    elif student_name and not available_quizzes:
        st.warning("⚠️ No quizzes available yet.")
    else:
        st.info("✍️ Please enter your name to begin.")
