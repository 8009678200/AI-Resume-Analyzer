import streamlit as st
import pdfplumber
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Configure page
st.set_page_config(
    page_title="AI Resume Analyzer - Ultimate Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Enhanced Skills Database
SKILLS_DB = [
    "python", "machine learning", "deep learning", "sql", "tensorflow", "pytorch",
    "pandas", "numpy", "power bi", "excel", "tableau", "data analysis",
    "streamlit", "scikit-learn", "flask", "fastapi", "git", "github", "aws", "azure",
    "docker", "kubernetes", "c++", "java", "javascript", "html", "css", "react", "node.js",
    "spark", "hadoop", "nlp", "computer vision", "devops", "ci/cd", "linux", "agile",
    "scrum", "project management", "data science", "tableau", "powerbi", "communication"
]

# Helper functions
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

def extract_skills(text):
    found_skills = []
    for skill in SKILLS_DB:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill.title())
    return set(found_skills)

def extract_contact_info(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    email = emails[0] if emails else "Not Detected"
    phone = phones[0] if phones else "Not Detected"
    return email, phone

def predict_category(skills):
    skills_lower = {s.lower() for skill in skills for s in [skill]}

    categories = {
        "Data Scientist / ML Engineer": {"python", "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "nlp", "computer vision", "data science"},
        "Data Analyst / BI Developer": {"sql", "power bi", "tableau", "excel", "data analysis", "powerbi"},
        "Cloud & DevOps Engineer": {"aws", "azure", "docker", "kubernetes", "devops", "ci/cd", "linux"},
        "Full Stack Developer": {"javascript", "html", "css", "react", "node.js", "flask", "fastapi", "java", "c++"},
        "Product / Project Manager": {"agile", "scrum", "project management", "communication"}
    }

    best_match = "General IT Professional"
    max_intersection = 0

    for cat, cat_skills in categories.items():
        intersection = len(skills_lower.intersection(cat_skills))
        if intersection > max_intersection:
            max_intersection = intersection
            best_match = cat

    return best_match

# Custom Title & UI styling
st.title("🧠 Ultimate AI Resume Analyzer & Matcher Pro")
st.subheader("Compare and enrich your professional profiles with complete ATS reports")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📂 Upload Your Resume")
    uploaded_file = st.file_uploader("Drag & Drop or Browse your PDF resume", type=["pdf"])

with col2:
    st.markdown("### 💼 Target Job Description")
    jd_input = st.text_area("Paste the job description here to analyze compatibility", height=150, placeholder="Looking for a candidate with Python, AWS, and SQL expertise...")

# Execution logic when inputs are present
if uploaded_file and jd_input:
    # Extract text and skills
    raw_resume_text = extract_text_from_pdf(uploaded_file)
    resume_text_lower = raw_resume_text.lower()
    jd_text = jd_input.lower()

    resume_skills = extract_skills(resume_text_lower)
    jd_skills = extract_skills(jd_text)
    email, phone = extract_contact_info(raw_resume_text)
    predicted_cat = predict_category(resume_skills)

    # Analytical sets
    matched_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills.difference(resume_skills)
    additional_skills = resume_skills.difference(jd_skills)

    # Match Score Calculation
    total_target_skills = len(jd_skills)
    if total_target_skills > 0:
        match_score = int((len(matched_skills) / total_target_skills) * 100)
    else:
        match_score = 0

    st.markdown("--- ")
    st.header("🎯 Comprehensive ATS Review & Compliance Dashboard")

    # Quick Stats Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("ATS Score Match", f"{match_score}%")
    with c2:
        st.metric("Predicted Role Category", predicted_cat)
    with c3:
        st.metric("Email Detected", email)
    with c4:
        st.metric("Phone Detected", phone)

    st.progress(match_score / 100.0, text="**Overall ATS Overlap Progress Bar**")

    # Visualizations
    col_metric, col_chart = st.columns([1, 1])

    with col_metric:
        st.markdown("#### 📊 Skill Match Chart")
        chart_df = pd.DataFrame({
            'Analysis Category': ['Matched Skills', 'Missing Skills', 'Extra Skills'],
            'Skill Count': [len(matched_skills), len(missing_skills), len(additional_skills)]
        })
        fig_bar = px.bar(
            chart_df,
            x='Analysis Category',
            y='Skill Count',
            color='Analysis Category',
            color_discrete_map={'Matched Skills': '#2E8B57', 'Missing Skills': '#FF4B4B', 'Extra Skills': '#FFA500'},
            text_auto=True
        )
        fig_bar.update_layout(height=280, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart:
        st.markdown("#### 📉 Skill Gap Analysis (Target vs Current)")
        total_needed = max(1, len(jd_skills))
        percentage_match = int((len(matched_skills) / total_needed) * 100)
        fig_pie = px.pie(
            names=['Matched Skills %', 'Gap %'],
            values=[percentage_match, 100 - percentage_match],
            color_discrete_sequence=['#2E8B57', '#FF4B4B'],
            hole=0.4
        )
        fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Feature Sections inside tabs
    tab_review, tab_recommends, tab_prep, tab_bot, tab_download = st.tabs([
        "📝 AI Resume Review & Suggestions",
        "💡 Project & Cert Recommendations",
        "💼 Interview Prep & Cover Letter",
        "💬 AI Career Chat Bot",
        "📥 Download Report"
    ])

    with tab_review:
        st.subheader("🧠 AI-Generated Professional Summary")
        skills_phrase = ", ".join(list(resume_skills)[:5]) if resume_skills else "experienced technical framework"
        st.write(f"_\"Result-oriented and proactive professional specializing in {predicted_cat}. Demonstrated expertise in working with {skills_phrase}. Highly capable of translating requirements into highly optimized software and strategic business results.\"_")

        st.subheader("📢 Recruiter Feedback & Career Roadmaps")
        if match_score < 40:
            st.warning("⚠️ **Critical Alert:** Your resume has a low compatibility match with the target position. Consider reframing structural keywords to bypass automatic applicant filters.")
        elif match_score < 75:
            st.info("💡 **Good Progress:** You are close to matching this role. Filling the minor skill gap highlighted on the chart will dramatically increase your interview rate.")
        else:
            st.success("🔥 **Perfect Match:** Excellent job! Your resume closely reflects the requested technical requirements. Ready to apply.")

        st.subheader("🛠 Concrete Resume Improvement Suggestions")
        st.markdown("""
        - **Incorporate Action Verbs**: Use phrases like *Developed, Orchestrated, Analyzed, Integrated* to represent experiences.
        - **Structure Contact Block**: Ensure email, phone number, and professional socials are organized neatly at the top of page 1.
        - **Highlight Missing Keywords**: Insert the missing keywords shown below in context within your active bullet points.
        """)

        st.markdown("**Detailed Target Key Differences:**")
        col_match, col_miss = st.columns(2)
        with col_match:
            st.success(f"**Matched Keywords ({len(matched_skills)}):** " + (", ".join(matched_skills) if matched_skills else "None"))
        with col_miss:
            st.error(f"**Missing Keywords ({len(missing_skills)}):** " + (", ".join(missing_skills) if missing_skills else "None"))

    with tab_recommends:
        st.subheader("💡 Personalized Project Recommendations")
        if missing_skills:
            st.write("To cover your missing skills, build portfolio projects around these tech stacks:")
            for skill in list(missing_skills)[:3]:
                st.markdown(f"- **Project Idea: High Performance {skill} Service** - Develop an interactive app showcasing backend orchestration, testing, and deployment utilizing {skill}.")
        else:
            st.write("No skill gaps! Consider focusing on scalability optimization projects with current frameworks.")

        st.subheader("🏆 Certification Recommendations")
        cert_mapping = {
            "AWS": "AWS Certified Solutions Architect",
            "Azure": "Microsoft Certified: Azure Fundamentals",
            "Sql": "Google Advanced Data Analytics Certificate",
            "Python": "PCAP – Certified Associate in Python Programming",
            "Machine Learning": "TensorFlow Developer Certificate / DeepLearning.AI Specialization"
        }
        recommended_certs = []
        for skill in jd_skills:
            if skill in cert_mapping:
                recommended_certs.append(cert_mapping[skill])

        if recommended_certs:
            for cert in list(set(recommended_certs))[:3]:
                st.markdown(f"- **{cert}** (Highly valued in target job application sector)")
        else:
            st.write("Focus on industry standard engineering practices or standard agile product design specifications.")

    with tab_prep:
        st.subheader("❓ AI-Generated Custom Interview Questions")
        if matched_skills:
            st.write("Be prepared to answer these tailored interview questions based on your background:")
            for i, skill in enumerate(list(matched_skills)[:3]):
                st.markdown(f"**Q{i+1}:** Can you describe a complex production problem you solved using your expertise in `{skill}` and how you evaluated success metrics?")
        else:
            st.write("Prepare to discuss standard object-oriented methodologies, problem solving, and architecture design.")

        st.subheader("✉️ Auto-Generated Professional Cover Letter")
        skills_list_str = ", ".join(list(matched_skills)[:3]) if matched_skills else "diverse tech stacks"
        cover_letter = f"""Dear Hiring Team,

I am writing to express my strong interest in the opportunity advertised. With a background in {predicted_cat} and hands-on experience in building software products, I am confident in my ability to immediately add value.

My professional skill set aligns cleanly with the role, matching target tools like {skills_list_str}.

Thank you for your time and consideration. I look forward to speaking with you.

Sincerely,
Candidate"""
        st.text_area("Draft Cover Letter Copy", cover_letter, height=220)

    with tab_bot:
        st.subheader("💬 Personal AI Career Assistant")
        st.write("Ask any questions regarding interview preparation, salary negotiations, or general career path advice.")

        # Simple chat implementation using streamlit session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_question = st.text_input("Ask AI Bot:", placeholder="e.g. How can I improve my salary negotiating skills for this role?")
        if st.button("Send 🚀") and user_question:
            # Simple Rule-based AI bot agent simulation responding intelligently based on the parsed role category
            response = ""
            q_lower = user_question.lower()
            if "salary" in q_lower or "negotiate" in q_lower:
                response = f"For a '{predicted_cat}' role, standard salary ranges depend highly on expertise. Try highlighting your matched skills ({', '.join(list(matched_skills)[:2])}) to build leverage."
            elif "improve" in q_lower or "learn" in q_lower:
                response = f"I highly recommend taking certifications or projects focused on {', '.join(list(missing_skills)[:2]) if missing_skills else 'system design'} to gain an competitive edge."
            elif "interview" in q_lower or "prepare" in q_lower:
                response = f"Make sure you prepare your STAR method responses emphasizing your experience in {predicted_cat} applications."
            else:
                response = f"That's a great question! As a professional categorized under '{predicted_cat}', focusing on continuous integration of your core skill set will significantly help your career progression."

            st.session_state.chat_history.append(("You", user_question))
            st.session_state.chat_history.append(("AI Career Bot", response))

        for sender, msg in reversed(st.session_state.chat_history):
            if sender == "You":
                st.info(f"**👤 {sender}:** {msg}")
            else:
                st.success(f"**🤖 {sender}:** {msg}")

    with tab_download:
        st.subheader("📥 Generate & Download Comprehensive ATS Report")
        report_content = f"""AI Resume Analyzer - Ultimate ATS Evaluation Report
----------------------------------------------------
Role Category Match: {predicted_cat}
Email Detected: {email}
Phone Number: {phone}
ATS Match Score: {match_score}%

Matched Core Skills: {', '.join(matched_skills) if matched_skills else 'None'}
Missing Skills Found: {', '.join(missing_skills) if missing_skills else 'None'}
----------------------------------------------------
End of Report"""

        st.download_button(
            label="📥 Download Full Report as Text",
            data=report_content,
            file_name="ATS_Resume_Evaluation_Report.txt",
            mime="text/plain"
        )
