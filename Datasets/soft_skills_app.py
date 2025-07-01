import streamlit as st
import pandas as pd
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

# Page setup
st.set_page_config(page_title="Soft Skills Question Selector", layout="wide")

# Title and description
st.title("Soft Skills Question Selector")
st.markdown("""
Select soft skill subcategories and specify how many questions you want from each.
""")

# Load the dataset
@st.cache_data
def load_data():
    try:
        # Try the downloads path first
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        file_path = os.path.join(downloads_path, 'soft_skills_questions.csv')
        df = pd.read_csv(file_path)
    except:
        # If that fails, try the current directory
        try:
            df = pd.read_csv('soft_skills_questions.csv')
        except:
            st.error("Could not find soft_skills_questions.csv in Downloads folder or current directory.")
            return None
    return df

# Function to create PDF with rating scales
def create_quiz_pdf(questions_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        spaceAfter=6
    )
    
    instruction_style = ParagraphStyle(
        'InstructionStyle',
        parent=styles['BodyText'],
        spaceAfter=12
    )
    
    question_style = styles['Normal']
    question_style.spaceAfter = 6
    
    # Build the PDF content
    content = []
    
    # Title
    content.append(Paragraph("Soft Skills Assessment Quiz", title_style))
    content.append(Spacer(1, 12))
    
    # Instructions
    content.append(Paragraph("Instructions", heading_style))
    content.append(Paragraph("For each question, indicate how much you agree by selecting one of the circles.", instruction_style))
    content.append(Spacer(1, 12))
    
    # Rating scale legend
    scale_data = [
        ['1', '2', '3', '4', '5'],
        ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree']
    ]
    
    legend_table = Table(scale_data, colWidths=[80, 80, 80, 80, 80])
    legend_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    content.append(legend_table)
    content.append(Spacer(1, 12))
    
    # Questions
    for i, (_, row) in enumerate(questions_data.iterrows(), 1):
        category = row['category'].capitalize()
        question = row['question_text']
        content.append(Paragraph(f"<b>Q{i}</b> ({category}): {question}", question_style))
        
        # Rating scale circles for each question
        circle_data = [[
            'O', 'O', 'O', 'O', 'O'
        ]]
        
        circle_table = Table(circle_data, colWidths=[80, 80, 80, 80, 80])
        circle_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        content.append(circle_table)
        content.append(Spacer(1, 15))
    
    # Build the PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

# Load the data
df = load_data()

if df is not None:
    # Initialize session state
    if 'question_counts' not in st.session_state:
        st.session_state.question_counts = {}
    
    if 'previewed_questions' not in st.session_state:
        st.session_state.previewed_questions = None
    
    # Sidebar - Category selection
    st.sidebar.header("Select Categories")
    
    # Get list of unique categories
    categories = sorted(df['category'].unique())
    
    # Category selection
    selected_categories = st.sidebar.multiselect(
        "Select subcategories:",
        options=categories
    )
    
    # Question count selection in sidebar
    if selected_categories:
        st.sidebar.header("Questions per Category")
        
        # Dictionary to store question counts
        quiz_counts = {}
        
        for category in selected_categories:
            # Get all questions for this category
            category_df = df[df['category'] == category]
            available = len(category_df)
            
            # Set default in session state if not already set
            if category not in st.session_state.question_counts:
                st.session_state.question_counts[category] = min(available, 3)  # Default to 3 or max available
            
            # Number input for this category
            count = st.sidebar.number_input(
                f"{category.capitalize()}",
                min_value=0,
                max_value=available,
                value=st.session_state.question_counts[category],
                key=f"sidebar_count_{category}"
            )
            
            # Store the selected count
            quiz_counts[category] = count
            st.session_state.question_counts[category] = count
        
        # Preview button
        if st.sidebar.button("Preview Questions", key="preview_questions_btn"):
            if sum(quiz_counts.values()) > 0:
                # Create a list to store selected questions
                preview_questions = []
                
                # Sample questions from each category based on user input
                for category, count in quiz_counts.items():
                    if count > 0:
                        category_df = df[df['category'] == category]
                        # Only sample if we have more questions than needed
                        if len(category_df) > count:
                            sampled = category_df.sample(n=count, random_state=42)
                        else:
                            sampled = category_df
                        preview_questions.append(sampled)
                
                # Combine all sampled questions
                if preview_questions:
                    quiz_df = pd.concat(preview_questions).reset_index(drop=True)
                    st.session_state.previewed_questions = quiz_df
            else:
                st.sidebar.warning("Please select at least one question to preview.")
                
        # Generate Quiz button in sidebar (only show if there are previewed questions)
        if st.session_state.previewed_questions is not None:
            if st.sidebar.button("Generate Quiz", key="sidebar_generate_quiz"):
                # Create PDF quiz for download
                pdf_buffer = create_quiz_pdf(st.session_state.previewed_questions)
                
                # Add download button for the quiz
                st.sidebar.download_button(
                    label="Download Quiz as PDF",
                    data=pdf_buffer,
                    file_name="soft_skills_quiz.pdf",
                    mime="application/pdf"
                )
                
                st.sidebar.success(f"Quiz with {len(st.session_state.previewed_questions)} questions successfully generated!")
    
    # Main content section
    if selected_categories:
        if st.session_state.previewed_questions is not None:
            # Display preview of generated quiz
            st.header("🎓 Quiz Preview")
            quiz_df = st.session_state.previewed_questions
            st.write(f"Total questions: {len(quiz_df)}")
            
            # Show breakdown by category
            category_counts = quiz_df['category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            st.write("### Questions per category")
            for _, row in category_counts.iterrows():
                category = row['Category'].capitalize()
                count = row['Count']
                st.write(f"- {category}: {count} questions")
            
            # Show rating scale legend
            st.write("### Rating Scale")
            cols = st.columns(5)
            with cols[0]:
                st.write("1: Strongly Disagree")
            with cols[1]:
                st.write("2: Disagree")
            with cols[2]:
                st.write("3: Neutral")
            with cols[3]:
                st.write("4: Agree")
            with cols[4]:
                st.write("5: Strongly Agree")
            
            # Show preview of questions with rating scales
            st.write("### Quiz Questions")
            for category in sorted(quiz_df['category'].unique()):
                st.write(f"#### {category.capitalize()}")
                cat_questions = quiz_df[quiz_df['category'] == category]
                
                for i, (_, row) in enumerate(cat_questions.iterrows(), 1):
                    st.write(f"**Q{i}** {row['question_text']}")
                    
                    # Create a horizontal rating scale for each question
                    rating_cols = st.columns(5)
                    for j in range(5):
                        with rating_cols[j]:
                            st.write(f"{j+1}", key=f"rating_{i}_{j}")
                            st.write("○")
                    
                    st.write("---")
        else:
            # Show all questions by category if no preview yet
            st.info("👈 Select the number of questions for each category and click 'Preview Questions' to see your quiz.")
            
            # Display total questions available
            st.write("### Available Questions by Category")
            for category in selected_categories:
                category_df = df[df['category'] == category]
                if not category_df.empty:
                    with st.expander(f"{category.capitalize()} - {len(category_df)} questions"):
                        for i, (_, row) in enumerate(category_df.iterrows(), 1):
                            st.write(f"{i}. {row['question_text']}")
    else:
        # No categories selected, show summary
        st.info("👈 Please select at least one subcategory from the sidebar.")
        
        # Display category distribution
        st.write("### Available Questions by Category")
        category_counts = df['category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        
        # Create columns for chart and stats
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create a bar chart
            st.bar_chart(category_counts.set_index('Category'))
        
        with col2:
            # Show statistics
            st.write("#### Dataset Statistics")
            st.write(f"Total questions: {len(df)}")
else:
    st.error("Failed to load the dataset. Please make sure the file exists.")