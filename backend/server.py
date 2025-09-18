from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import requests
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime
import PyPDF2
import io
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Gemini API configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Load internships data
def load_internships():
    try:
        internships_path = ROOT_DIR.parent / 'frontend' / 'public' / 'thing.json'
        with open(internships_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading internships: {e}")
        return []

INTERNSHIPS_DATA = load_internships()

# Define Models
class ResumeAnalysis(BaseModel):
    overall_rating: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    raw_analysis: str

class InternshipRecommendation(BaseModel):
    id: int
    title: str
    company: str
    location: str
    skills_required: List[str]
    score_range: List[int]
    category: str
    description: str
    match_percentage: int
    matched_skills: List[str]

class AnalyzeResponse(BaseModel):
    analysis: ResumeAnalysis
    recommendations: List[InternshipRecommendation]

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Helper Functions
def extract_text_from_pdf(pdf_file: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting PDF text: {e}")
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF")

async def analyze_with_gemini(resume_text: str) -> dict:
    prompt = """You are a professional resume expert.  
Analyze the following resume carefully and respond with a JSON object ONLY (no additional commentary or text).  

The JSON must strictly follow this structure:  

{
  "overall_rating": number,         // 0–10 (can be decimal, e.g., 7.5)

  "strengths": [
    " Strong in <skill/area>",
    " Strong in <another skill>"
  ],
  "weaknesses": [
    " Weak in <skill/area>",
    " Needs improvement in <another skill>"
  ],

  "suggestions": [
    " Suggest adding <thing>",
    " Suggest improving <thing>"
  ],

  "raw_analysis": "Provide a detailed plain-text analysis here if needed."
}

Rules:  
- Do NOT output anything outside the JSON object.  
- Each bullet point in strengths, weaknesses, and suggestions MUST start with two leading spaces (e.g., " Strong in JavaScript").  
- Ensure clean spacing between strengths, weaknesses, and suggestions blocks (two blank lines).  
- "raw_analysis" should be a plain, unformatted text (no bullet points, no special characters).  
- Based on the resume, recommend any of the 4 skills from these as suggestions: Node.js, Express, PostgreSQL, Docker, React, TypeScript, TailwindCSS, REST APIs, MERN Stack, GitHub Actions, Git, AWS, Kubernetes, CI/CD, Jenkins, Linux, Flutter, Firebase, Dart, Python, NLP, Transformers, FastAPI, OpenCV, TensorFlow, Deep Learning, SQL, ETL, Apache Spark, SIEM Tools, Threat Analysis, Networking, Burp Suite, OWASP, Solidity, Ethereum, Web3.js, Smart Contracts

Resume:
""" + resume_text

    try:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = requests.post(
            GEMINI_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logging.error(f"Gemini API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="AI analysis service unavailable")
        
        data = response.json()
        ai_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not ai_text:
            raise HTTPException(status_code=500, detail="No response from AI analysis")
        
        # Try to parse JSON from response
        try:
            # Clean the response - remove markdown formatting if present
            clean_text = ai_text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            
            analysis_data = json.loads(clean_text)
            return analysis_data
            
        except json.JSONDecodeError:
            # Try to extract JSON from text using regex
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                try:
                    analysis_data = json.loads(json_match.group())
                    return analysis_data
                except json.JSONDecodeError:
                    pass
            
            # Fallback response if JSON parsing fails
            logging.warning("Failed to parse Gemini response as JSON, using fallback")
            return {
                "overall_rating": 6.0,
                "strengths": [" Good technical foundation", " Shows learning ability"],
                "weaknesses": [" Limited professional experience", " Could improve technical depth"],
                "suggestions": [" Gain more hands-on experience", " Learn modern frameworks"],
                "raw_analysis": ai_text[:500] + "..." if len(ai_text) > 500 else ai_text
            }
            
    except requests.RequestException as e:
        logging.error(f"Error calling Gemini API: {e}")
        raise HTTPException(status_code=500, detail="AI analysis service unavailable")

def calculate_skill_matches(resume_text: str, internship: dict) -> tuple:
    resume_lower = resume_text.lower()
    skills_required = internship.get('skills_required', [])
    matched_skills = []
    
    for skill in skills_required:
        if isinstance(skill, str) and skill.lower() in resume_lower:
            matched_skills.append(skill)
    
    match_percentage = int((len(matched_skills) / len(skills_required)) * 100) if skills_required else 0
    return matched_skills, match_percentage

def recommend_internships(analysis: dict, resume_text: str) -> List[InternshipRecommendation]:
    overall_rating = analysis.get('overall_rating', 6.0)
    recommendations = []
    
    for internship in INTERNSHIPS_DATA:
        score_range = internship.get('score_range', [5, 10])
        
        # Check if the overall rating falls within the internship's score range (with some flexibility)
        if (overall_rating >= score_range[0] - 1) and (overall_rating <= score_range[1] + 1):
            matched_skills, match_percentage = calculate_skill_matches(resume_text, internship)
            
            # Only include internships with at least some skill match or within perfect score range
            if match_percentage > 0 or (overall_rating >= score_range[0] and overall_rating <= score_range[1]):
                recommendation = InternshipRecommendation(
                    id=internship['id'],
                    title=internship['title'],
                    company=internship['company'],
                    location=internship['location'],
                    skills_required=internship['skills_required'],
                    score_range=internship['score_range'],
                    category=internship['category'],
                    description=internship['description'],
                    match_percentage=max(match_percentage, 10),  # Minimum 10% for score-based matches
                    matched_skills=matched_skills
                )
                recommendations.append(recommendation)
    
    # Sort by match percentage (descending) and then by score compatibility
    recommendations.sort(key=lambda x: (x.match_percentage, -abs(overall_rating - sum(x.score_range)/2)), reverse=True)
    
    # Return top 6 recommendations
    return recommendations[:6]

# API Routes
@api_router.get("/")
async def root():
    return {"message": "SkillSync API - AI-Based Internship Recommendation Engine"}

@api_router.get("/internships")
async def get_internships():
    return INTERNSHIPS_DATA

@api_router.post("/analyze-resume", response_model=AnalyzeResponse)
async def analyze_resume(resume: UploadFile = File(...)):
    # Validate file type
    if not resume.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read and extract text from PDF
        pdf_content = await resume.read()
        resume_text = extract_text_from_pdf(pdf_content)
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Analyze with Gemini AI
        analysis_data = await analyze_with_gemini(resume_text)
        
        # Create analysis object
        analysis = ResumeAnalysis(**analysis_data)
        
        # Get internship recommendations
        recommendations = recommend_internships(analysis_data, resume_text)
        
        # Store analysis in database (optional)
        analysis_record = {
            "filename": resume.filename,
            "analysis": analysis_data,
            "recommendations_count": len(recommendations),
            "timestamp": datetime.utcnow()
        }
        await db.resume_analyses.insert_one(analysis_record)
        
        return AnalyzeResponse(
            analysis=analysis,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error analyzing resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume")

# Legacy routes for compatibility
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)