"""
This module contains utility functions for the AI Recruiter application,
including file parsing, NLP processing, and API interactions.
"""

import docx
import PyPDF2
import spacy
import google.generativeai as genai
import streamlit as st
from spacy.matcher import PhraseMatcher
import re
from typing import List, Dict, Any, Union

# --- Model Loading ---

@st.cache_resource
def load_spacy_model() -> spacy.language.Language:
    """
    Loads the spaCy 'en_core_web_sm' model.
    Prioritizes importing as a module for Streamlit Cloud compatibility.
    """
    try:
        import en_core_web_sm
        return en_core_web_sm.load()
    except ImportError:
        pass
    
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("Model 'en_core_web_sm' not found. Downloading...")
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# --- Predefined Skills ---

PREDEFINED_SKILLS: List[str] = [
    "Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "PyTorch", "TensorFlow",
    "Machine Learning", "Data Visualization", "Deep Learning", "Tableau", "Excel",
    "Git", "GitHub", "FastAPI", "Streamlit", "NLP", "AI", "Data Science"
]
skill_patterns = [nlp.make_doc(skill) for skill in PREDEFINED_SKILLS]

# --- API Interaction ---

def get_chatbot_response(question: str, context: str, api_key: str) -> str:
    """
    Calls the Google Gemini API to get a chatbot response based on a question and context.

    Args:
        question (str): The user's question.
        context (str): The context (resumes and job description) for the chatbot to use.
        api_key (str): The Google Gemini API key.

    Returns:
        str: The chatbot's response.
    """
    try:
        genai.configure(api_key=api_key)
        
        model_name = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_name = m.name
                break
        
        if not model_name:
            st.error("Could not find a suitable model that supports 'generateContent'.")
            return "Sorry, I can't generate a response right now."

        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are an expert AI recruiting assistant. Your task is to answer questions based ONLY on the context provided below. Do not make up information. If the answer is not in the context, say 'I could not find an answer in the provided documents.'

        **CONTEXT:**
        {context}

        **QUESTION:**
        {question}

        **ANSWER:**
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred with the Gemini API: {e}")
        return "Sorry, I encountered an error while trying to generate a response."

# --- File Parsers ---

def read_docx(file: Any) -> str:
    """
    Reads the text content from a DOCX file.

    Args:
        file (Any): The file-like object from Streamlit's file_uploader.

    Returns:
        str: The extracted text content.
    """
    try:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading DOCX file '{file.name}': {e}")
        return ""

def read_pdf(file: Any) -> str:
    """
    Reads the text content from a PDF file.

    Args:
        file (Any): The file-like object from Streamlit's file_uploader.

    Returns:
        str: The extracted text content.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    except PyPDF2.errors.PdfReadError:
        st.warning(f"Could not read '{file.name}'. The PDF may be corrupted or invalid. Skipping.")
        return ""
    except Exception as e:
        st.error(f"An unexpected error occurred while reading '{file.name}': {e}")
        return ""

# --- NLP and Data Extraction ---

def refined_extract_skills(text: str, skill_patterns: list) -> List[str]:
    """
    Extracts skills from text based on a list of skill patterns.

    Args:
        text (str): The text to extract skills from.
        skill_patterns (list): A list of spaCy Doc objects representing skill patterns.

    Returns:
        List[str]: A list of unique skills found in the text.
    """
    doc = nlp(text)
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("SKILL_MATCHER", skill_patterns)
    matches = matcher(doc)
    return list(set(doc[start:end].text.title() for _, start, end in matches))

def detailed_extract_experience(text: str) -> List[str]:
    """
    Extracts work experience (organizations) from text.

    Args:
        text (str): The text to extract experience from.

    Returns:
        List[str]: A list of extracted work experiences.
    """
    doc = nlp(text)
    experience = [f"Worked at: {ent.text}" for ent in doc.ents if ent.label_ == "ORG"]
    return experience if experience else ["Could not automatically extract experience."]

def detailed_extract_education(text: str) -> List[str]:
    """
    Extracts education institutions from text.

    Args:
        text (str): The text to extract education from.

    Returns:
        List[str]: A list of extracted education institutions.
    """
    doc = nlp(text)
    education_keywords = ["university", "college", "institute"]
    education = [f"Studied at: {ent.text}" for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"] and any(keyword in ent.text.lower() for keyword in education_keywords)]
    return education if education else ["Could not automatically extract education."]

def detailed_extract_projects(text: str) -> List[str]:
    """
    Extracts project sections from text using regex.

    Args:
        text (str): The text to extract projects from.

    Returns:
        List[str]: A list of extracted project descriptions.
    """
    project_sections = re.findall(r"(?:projects|portfolio|personal projects)\s*\n(.*?)(?:\n\n\s*(?:skills|experience|education)|$)", text, re.IGNORECASE | re.DOTALL)
    return [section.strip() for section in project_sections] if project_sections else ["No projects section found."]

# --- Candidate Analysis ---

def rank_candidates(job_skills: List[str], candidate_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks candidates based on the overlap between their skills and the job description skills.

    Args:
        job_skills (List[str]): A list of skills from the job description.
        candidate_data (List[Dict[str, Any]]): A list of dictionaries, where each dictionary represents a candidate.

    Returns:
        List[Dict[str, Any]]: The list of candidates, sorted by match percentage in descending order.
    """
    job_skills_set = set(job_skills)
    for candidate in candidate_data:
        match_score = len(job_skills_set.intersection(set(candidate['skills'])))
        candidate['match_score'] = match_score
        candidate['match_percentage'] = (match_score / len(job_skills_set)) * 100 if job_skills_set else 0
    
    candidate_data.sort(key=lambda x: x['match_percentage'], reverse=True)
    return candidate_data