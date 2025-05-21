import streamlit as st
from pdfminer.high_level import extract_text
import json
import os
import spacy
import re
from fpdf import FPDF
import io
from PIL import Image

# ----------------- Page Config -----------------
st.set_page_config(page_title="AI Resume Screener", layout="centered")
logo = Image.open("C:\\Users\\Divyam Sahu\\OneDrive\\Documents\\resume_screener\\logo.png")
st.image(logo, width=80)  
# ----------------- UI Header -----------------
st.title("📄 AI Resume Screener")
st.write("Upload your resume, select a job role, and get your match score instantly.")

# ----------------- Resume Upload -----------------
uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

resume_text = ""
if uploaded_file is not None:
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.read())
    resume_text = extract_text("temp_resume.pdf")
    os.remove("temp_resume.pdf")

# ----------------- Load Job Descriptions -----------------
with open("C:\\Users\\Divyam Sahu\\OneDrive\\Documents\\resume_screener\\job_description.json", "r") as file:
    job_data = json.load(file)

# ----------------- Select Company -----------------
st.subheader("🏢 Select the Company You Want to Apply For")
selected_company = st.selectbox("Choose a company:", list(job_data.keys()))

# ----------------- NLP & Skills Setup -----------------
nlp = spacy.load("en_core_web_sm")

SKILL_DB = [
    "python", "java", "c++", "html", "css", "javascript", "react", "node.js",
    "sql", "spring", "rest api", "machine learning", "data structures", "algorithms", "microservices"
]

LEARNING_LINKS = {
    "python": "https://www.learnpython.org/",
    "java": "https://www.learnjavaonline.org/",
    "html": "https://www.w3schools.com/html/",
    "css": "https://www.w3schools.com/css/",
    "javascript": "https://www.javascript.com/learn",
    "react": "https://reactjs.org/tutorial/tutorial.html",
    "node.js": "https://nodejs.dev/en/learn/",
    "sql": "https://www.w3schools.com/sql/",
    "spring": "https://spring.io/guides",
    "rest api": "https://restfulapi.net/",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "data structures": "https://www.geeksforgeeks.org/data-structures/",
    "algorithms": "https://www.khanacademy.org/computing/computer-science/algorithms",
    "microservices": "https://microservices.io/"
}

# ----------------- Extraction Functions -----------------
def extract_skills(text):
    text = text.lower()
    return list(set([skill for skill in SKILL_DB if skill in text]))

def extract_experience(text):
    match = re.search(r'(\d+)\+?\s*(years|yrs)', text.lower())
    return int(match.group(1)) if match else 0

# ----------------- PDF Report Generation -----------------
def create_pdf_report(company, job_info, resume_experience, final_score, matched_skills, missing_skills, learning_links):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Resume Match Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    pdf.cell(0, 10, f"Company: {company}", ln=True)
    pdf.cell(0, 10, f"Job Role: {job_info['title']}", ln=True)
    pdf.cell(0, 10, f"Required Experience: {job_info['experience_required']}", ln=True)
    pdf.cell(0, 10, f"Your Experience: {resume_experience} years", ln=True)
    pdf.cell(0, 10, f"Match Score: {final_score}%", ln=True)
    pdf.ln(10)

    pdf.cell(0, 10, "Matched Skills:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, ", ".join(matched_skills) if matched_skills else "None")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Missing Skills:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, ", ".join(missing_skills) if missing_skills else "None")
    pdf.ln(5)

    if missing_skills:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Suggested Learning Resources:", ln=True)
        pdf.set_font("Arial", '', 12)
        for skill in missing_skills:
            link = learning_links.get(skill.lower())
            if link:
                pdf.cell(0, 10, f"- {skill.title()}: {link}", ln=True)

    # Fix: output to string, then encode and wrap in BytesIO
    pdf_output = pdf.output(dest='S').encode('latin-1')
    buffer = io.BytesIO(pdf_output)
    return buffer

# ----------------- Resume Analysis -----------------
if uploaded_file and selected_company:
    job_info = job_data[selected_company]
    required_skills = job_info['required_skills']
    required_exp = int(re.findall(r'\d+', job_info['experience_required'])[0])

    resume_skills = extract_skills(resume_text)
    resume_experience = extract_experience(resume_text)

    matched_skills = list(set(resume_skills) & set(required_skills))
    missing_skills = list(set(required_skills) - set(resume_skills))

    exp_score = min(resume_experience / required_exp, 1.0) * 100
    skill_score = (len(matched_skills) / len(required_skills)) * 100
    final_score = int((exp_score + skill_score) / 2)

    st.subheader("📊 Match Analysis")
    st.write(f"✅ **Matched Skills:** {', '.join(matched_skills) if matched_skills else 'None'}")
    st.write(f"❌ **Missing Skills:** {', '.join(missing_skills) if missing_skills else 'None'}")
    st.write(f"🧠 **Resume Experience:** {resume_experience} years")
    st.write(f"📈 **Experience Required:** {required_exp} years")
    st.write(f"🏆 **Match Score:** `{final_score}%`")

    if missing_skills:
        st.subheader("📚 Suggested Learning Resources")
        for skill in missing_skills:
            link = LEARNING_LINKS.get(skill.lower())
            if link:
                st.markdown(f"- [{skill.title()}]({link})")

    # Downloadable PDF report
    pdf_buffer = create_pdf_report(
        selected_company,
        job_info,
        resume_experience,
        final_score,
        matched_skills,
        missing_skills,
        LEARNING_LINKS
    )

    st.download_button(
        label="📥 Download Match Report as PDF",
        data=pdf_buffer,
        file_name=f"{selected_company}_resume_match_report.pdf",
        mime="application/pdf"
    )

