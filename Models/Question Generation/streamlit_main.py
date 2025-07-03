import streamlit as st
import requests
import subprocess
import webbrowser

st.set_page_config(
    page_title="Quiz System Hub", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check if services are running
def check_service_status():
    services = {
        "API Server": "http://localhost:8000/health",
        "Teacher UI": "http://localhost:8501",
        "Student UI": "http://localhost:8502"
    }
    
    status = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code in [200, 405]:  # 405 for Streamlit health checks
                status[name] = {"status": "🟢 Running", "accessible": True}
            else:
                status[name] = {"status": f"🔴 Error ({response.status_code})", "accessible": False}
        except requests.exceptions.ConnectionError:
            status[name] = {"status": "🔴 Offline", "accessible": False}
        except requests.exceptions.Timeout:
            status[name] = {"status": "� Slow", "accessible": True}
        except Exception as e:
            status[name] = {"status": f"🔴 Error", "accessible": False}
    
    return status

st.title("🎓 Question Generation System Hub")
st.markdown("### Central control panel for the quiz system")

# Service status in sidebar with auto-refresh
st.sidebar.header("🔧 System Status")
if st.sidebar.button("🔄 Refresh Status"):
    st.rerun()

status = check_service_status()
all_running = all(s["accessible"] for s in status.values())

for service, info in status.items():
    st.sidebar.write(f"{service}: {info['status']}")

if all_running:
    st.sidebar.success("✅ All services running!")
else:
    st.sidebar.error("⚠️ Some services are offline")
    offline_services = [name for name, info in status.items() if not info["accessible"]]
    st.sidebar.write(f"Offline: {', '.join(offline_services)}")
    
    if st.sidebar.button("🚀 Restart Services"):
        st.sidebar.info("Please run: ./run_robust.sh")

# Add troubleshooting section
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛟 Troubleshooting")
if not all_running:
    st.sidebar.markdown("""
    **If services are offline:**
    1. Stop current processes: `Ctrl+C`
    2. Run: `./run_robust.sh`
    3. Wait for all services to start
    4. Refresh this page
    """)
else:
    st.sidebar.markdown("All systems operational! 🎉")

# Navigation
st.markdown("## 🧭 Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 👩‍🏫 Teacher Interface
    **Create and manage quizzes**
    - Generate AI-powered questions
    - Edit and customize quizzes  
    - View student responses
    - Download analytics
    """)
    
    # Check if teacher interface is accessible
    teacher_accessible = status.get("Teacher UI", {}).get("accessible", False)
    teacher_url = "http://localhost:8501"
    
    if teacher_accessible:
        st.markdown(f'<a href="{teacher_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #FF6B6B; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">🚀 Open Teacher Interface</button></a>', unsafe_allow_html=True)
        st.markdown(f"**Status:** ✅ Ready")
    else:
        st.markdown(f'<button style="background-color: #cccccc; color: #666666; padding: 10px 20px; border: none; border-radius: 5px; width: 100%; cursor: not-allowed;">🚫 Teacher Interface Offline</button>', unsafe_allow_html=True)
        st.markdown(f"**Status:** ❌ Not accessible")
    
    st.markdown(f"**Direct link:** [{teacher_url}]({teacher_url})")

with col2:
    st.markdown("""
    ### 🎯 Student Interface  
    **Take assessments**
    - Browse available quizzes
    - Complete self-assessments
    - View your results
    - Download your scores
    """)
    
    # Check if student interface is accessible
    student_accessible = status.get("Student UI", {}).get("accessible", False)
    student_url = "http://localhost:8502"
    
    if student_accessible:
        st.markdown(f'<a href="{student_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #4ECDC4; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">🚀 Open Student Interface</button></a>', unsafe_allow_html=True)
        st.markdown(f"**Status:** ✅ Ready")
    else:
        st.markdown(f'<button style="background-color: #cccccc; color: #666666; padding: 10px 20px; border: none; border-radius: 5px; width: 100%; cursor: not-allowed;">🚫 Student Interface Offline</button>', unsafe_allow_html=True)
        st.markdown(f"**Status:** ❌ Not accessible")
    
    st.markdown(f"**Direct link:** [{student_url}]({student_url})")

with col3:
    st.markdown("""
    ### 🔧 API Documentation
    **Developer resources**
    - REST API endpoints
    - Interactive testing
    - Schema documentation
    - Example requests
    """)
    
    # Check if API is accessible
    api_accessible = status.get("API Server", {}).get("accessible", False)
    api_url = "http://localhost:8000/docs"
    
    if api_accessible:
        st.markdown(f'<a href="{api_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #95E1D3; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">🚀 Open API Docs</button></a>', unsafe_allow_html=True)
        st.markdown(f"**Status:** ✅ Ready")
    else:
        st.markdown(f'<button style="background-color: #cccccc; color: #666666; padding: 10px 20px; border: none; border-radius: 5px; width: 100%; cursor: not-allowed;">🚫 API Offline</button>', unsafe_allow_html=True)
        st.markdown(f"**Status:** ❌ Not accessible")
    
    st.markdown(f"**Direct link:** [{api_url}]({api_url})")

st.divider()

# Quick links
st.markdown("### 🔗 Quick Access Links")
col1, col2, col3 = st.columns(3)

with col1:
    st.link_button("👩‍🏫 Teacher Portal", "http://localhost:8501", use_container_width=True)

with col2:
    st.link_button("🎯 Student Portal", "http://localhost:8502", use_container_width=True)

with col3:
    st.link_button("📚 API Documentation", "http://localhost:8000/docs", use_container_width=True)

# Status check
st.divider()
st.markdown("### 📊 System Status")

import requests
import time

def check_service(url, name):
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return f"✅ {name} - Running"
        else:
            return f"⚠️ {name} - Error ({response.status_code})"
    except:
        return f"❌ {name} - Not responding"

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    api_status = check_service("http://localhost:8000/docs", "API Server")
    st.write(api_status)

with status_col2:
    teacher_status = check_service("http://localhost:8501", "Teacher UI")
    st.write(teacher_status)

with status_col3:
    student_status = check_service("http://localhost:8502", "Student UI")
    st.write(student_status)

# Instructions
st.divider()
st.markdown("### 📝 How to Use")

with st.expander("🚀 Getting Started"):
    st.markdown("""
    1. **Start the system**: Run `./run.sh` to start all services
    2. **Teacher workflow**:
       - Open Teacher Interface (port 8501)
       - Generate questions using AI
       - Save quizzes for students
       - Monitor student responses
    
    3. **Student workflow**:
       - Open Student Interface (port 8502)
       - Select a quiz from the sidebar
       - Complete the assessment
       - View your results and download them
    
    4. **All interfaces run simultaneously** - just switch between browser tabs!
    """)

with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    - **Services not starting?** Check that ports 8000, 8501, 8502 are available
    - **API errors?** Ensure your Google API key is set in `.env` file
    - **Can't save quizzes?** Check file permissions in the `quiz_storage` directory
    - **Students can't see quizzes?** Make sure teacher saved the quiz (not just downloaded)
    """)
