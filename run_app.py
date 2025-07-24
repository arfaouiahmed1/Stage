import streamlit as st
import os
import sys
import subprocess

st.title("Student Soft Skills Clustering App")

st.write("""
This application allows multiple students to take a soft skills assessment quiz and then 
groups them into heterogeneous learning teams based on their complementary skills.
""")

st.write("## Features:")
st.write("- 5-point Likert scale quiz to assess soft skills")
st.write("- Individual student skill profiles and recommendations")
st.write("- Clustering of students into heterogeneous learning groups")
st.write("- Visual representation of student clusters")
st.write("- Detailed group analysis and recommendations")

if st.button("Launch Application"):
    # Run the actual application
    st.info("Starting the Student Clustering App...")
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main application file
    app_path = os.path.join(current_dir, "student_quiz_clustering_app.py")
    
    # Run the application using the system's Python interpreter
    try:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", app_path])
        st.success("Application launched successfully!")
    except Exception as e:
        st.error(f"Failed to launch application: {e}")
        
    st.write("""
    If the application doesn't open automatically, you can run it manually:
    ```
    streamlit run student_quiz_clustering_app.py
    ```
    """)

st.write("---")
st.write("## Getting Started:")
st.write("""
1. Click the 'Launch Application' button above
2. Enter your name to begin the soft skills assessment
3. Complete the quiz to see your individual results
4. View the 'All Student Groups' section to see heterogeneous learning groups
""")
