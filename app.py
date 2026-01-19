import streamlit as st
import pandas as pd
import os
from src.utils import (
    read_docx,
    read_pdf,
    get_chatbot_response,
    refined_extract_skills,
    detailed_extract_experience,
    detailed_extract_education,
    detailed_extract_projects,
    rank_candidates,
    skill_patterns
)

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="AI Recruiter")

# --- Main UI ---
st.title("🚀 AI Recruiter")
st.markdown("An intelligent system for local resume analysis with a fast, API-powered chatbot.")

# --- Session State Initialization ---
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar for File Uploads ---
with st.sidebar:
    st.header("Upload Files")
    job_description_file = st.file_uploader("1. Upload Job Description", type=["docx", "pdf"])
    resume_files = st.file_uploader("2. Upload Resumes", type=["docx", "pdf"], accept_multiple_files=True)
    analyze_button = st.button("Analyze Candidates", type="primary")

# --- Core Application Logic ---
if analyze_button and job_description_file and resume_files:
    st.session_state.chat_history = []
    st.session_state.analysis_done = True
    
    with st.spinner("🚀 Analyzing documents locally..."):
        # Read job description
        jd_content = read_docx(job_description_file) if "wordprocessingml" in job_description_file.type else read_pdf(job_description_file)
        job_skills = refined_extract_skills(jd_content, skill_patterns)

        candidate_data = []
        full_qa_context = f"**JOB DESCRIPTION:**\n{jd_content}"

        # Process each resume
        for resume_file in resume_files:
            content = read_docx(resume_file) if "wordprocessingml" in resume_file.type else read_pdf(resume_file)
            if content:
                candidate_details = {
                    "name": resume_file.name,
                    "skills": refined_extract_skills(content, skill_patterns),
                    "experience": detailed_extract_experience(content),
                    "education": detailed_extract_education(content),
                    "projects": detailed_extract_projects(content)
                }
                candidate_data.append(candidate_details)
                full_qa_context += f"\n\n--- RESUME: {resume_file.name} ---\n{content}"
        
        st.session_state.qa_context = full_qa_context
        st.session_state.ranked_candidates = rank_candidates(job_skills, candidate_data)

# --- Display Results ---
if st.session_state.analysis_done:
    st.header("Analysis Results")
    
    # Display dataframe with specified column order
    df = pd.DataFrame(st.session_state.ranked_candidates)
    display_columns = ['name', 'skills', 'match_percentage', 'match_score', 'experience', 'projects', 'education']
    st.dataframe(df[display_columns], width='stretch')

    st.subheader("Detailed Candidate Profiles")
    for candidate in st.session_state.ranked_candidates:
        with st.expander(f"{candidate['name']} - Match: {candidate['match_percentage']:.2f}%"):
            st.markdown(f"**Skills:** {', '.join(candidate['skills'])}")
            st.markdown("**Experience Highlights:**")
            for exp in candidate['experience']: st.write(f"- {exp}")
            st.markdown("**Education Highlights:**")
            for edu in candidate['education']: st.write(f"- {edu}")
            st.markdown("**Project Highlights:**")
            for proj in candidate['projects']: st.write(f"- {proj}")

    # --- Conversational AI Section ---
    st.markdown("---")
    st.header("Chat about the Documents")

    # API Key Handling
    try:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
        if not gemini_api_key or gemini_api_key == "YOUR_TOKEN_HERE":
            st.error("Gemini API key is not configured. Please add it to your Streamlit secrets.")
            st.stop()
    except KeyError:
        st.error("Gemini API key is not configured. Please add it to your Streamlit secrets.")
        st.stop()

    # Chat History and Input
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_question := st.chat_input("Ask a question..."):
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = get_chatbot_response(user_question, st.session_state.qa_context, gemini_api_key)
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
else:
    st.info("Please upload documents and click 'Analyze Candidates' to begin.")