from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Define categories and sample questions
questions_by_category = {
    "Hard Skills": [
        "Demonstrates proficiency in technical tools required for tasks.",
        "Completes assignments with minimal errors.",
        "Applies learned concepts to solve real-world problems.",
        "Understands domain-specific terminology.",
        "Can work independently on complex tasks."
    ],
    "Soft Skills": [
        "Communicates ideas clearly and effectively.",
        "Accepts constructive feedback positively.",
        "Demonstrates adaptability in changing situations.",
        "Listens actively during group discussions.",
        "Manages time and priorities efficiently."
    ],
    "Team Spirit": [
        "Participates actively in team meetings.",
        "Respects diverse opinions and perspectives.",
        "Takes initiative in group tasks.",
        "Supports peers during challenging assignments.",
        "Shares responsibilities fairly within the group."
    ],
    "Creativity": [
        "Offers original solutions to problems.",
        "Thinks outside the box in brainstorming sessions.",
        "Brings new perspectives to traditional methods.",
        "Experiments with new tools and approaches.",
        "Shows curiosity and willingness to innovate."
    ]
}

# Create the PDF
pdf_path = "Evaluation_Question_Bank.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)
width, height = A4
y_position = height - 50

c.setFont("Helvetica-Bold", 16)
c.drawString(50, y_position, "Evaluation Question Bank (Scale 1-5 Reference)")
y_position -= 40

for category, questions in questions_by_category.items():
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, f"{category}")
    y_position -= 25

    c.setFont("Helvetica", 12)
    for i, question in enumerate(questions, 1):
        if y_position < 100:
            c.showPage()
            y_position = height - 50
        c.drawString(70, y_position, f"{i}. {question}")
        y_position -= 20

    y_position -= 10

c.save()
print(f"Reference PDF generated: {pdf_path}")
