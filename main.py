from fastapi import FastAPI
from pydantic import BaseModel
import re

# Initialize the FastAPI app
app = FastAPI()

# Define the data model for the request body
# This tells FastAPI what kind of data to expect
class ScoreRequest(BaseModel):
    resume: str
    job_description: str

# This is the core logic function
def calculate_score(resume: str, jd: str) -> float:
    """
    Calculates a simple match score based on keyword overlap.
    """
    # Sanitize text: lowercase and find all words
    resume_words = set(re.findall(r'\w+', resume.lower()))
    jd_words = set(re.findall(r'\w+', jd.lower()))

    if not jd_words:
        return 0.0

    # Find the intersection of words
    matching_words = resume_words.intersection(jd_words)

    # Calculate score as percentage of matched JD words
    score = len(matching_words) / len(jd_words)
    return score * 100

# Define the API endpoint
@app.post("/score")
def get_score(request: ScoreRequest):
    """
    This endpoint receives a resume and job description,
    calculates a match score, and returns it.
    """
    score = calculate_score(request.resume, request.job_description)
    return {"match_score_percent": f"{score:.2f}"}

# A simple root endpoint to check if the server is running
@app.get("/")
def read_root():
    return {"message": "AI Recruiter API is running."}
