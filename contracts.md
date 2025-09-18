# SkillSync API Contracts & Integration Plan

## Backend Implementation Requirements

### 1. API Endpoints

#### POST /api/analyze-resume
- **Purpose**: Upload PDF resume, extract text, analyze with Gemini AI, and return recommendations
- **Input**: 
  - multipart/form-data with PDF file
- **Output**: 
```json
{
  "analysis": {
    "overall_rating": 7.5,
    "strengths": ["Strong in JavaScript", "Strong in React"],
    "weaknesses": ["Weak in backend", "Needs cloud experience"],
    "suggestions": ["Learn Node.js", "Gain AWS experience"],
    "raw_analysis": "Detailed analysis text..."
  },
  "recommendations": [
    {
      "id": 10,
      "title": "Frontend Developer Intern",
      "company": "PixelSoft",
      "location": "Pune, India",
      "skills_required": ["React", "TypeScript", "TailwindCSS", "REST APIs"],
      "score_range": [5, 7],
      "category": "Frontend Development",
      "description": "Work on responsive UI design...",
      "match_percentage": 85,
      "matched_skills": ["React", "REST APIs"]
    }
  ]
}
```

#### GET /api/internships
- **Purpose**: Get all available internships from thing.json
- **Output**: Array of internship objects

### 2. Current Mock Data to Replace

**Frontend Mock Functions in `/frontend/src/utils/mockData.js`:**
- `mockAnalyzeResume()` → Replace with real API call to `/api/analyze-resume`
- `mockInternships` → Replace with API call to `/api/internships`

**Mock Data Removal:**
- Remove mock analysis results generation
- Remove hardcoded internship filtering
- Remove setTimeout delays

### 3. Backend Dependencies to Install
```
pip install PyPDF2 python-multipart
```

### 4. Backend Implementation Details

#### PDF Text Extraction
- Use PyPDF2 library to extract text from uploaded PDF
- Handle multi-page PDFs
- Clean and normalize extracted text

#### Gemini AI Integration
- **API Key**: AIzaSyBpl2jIVgdaKfHM6Hzniwr_HTVhX2_bD5A
- **Endpoint**: https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}
- **Prompt**: Use exact prompt provided by user
- **Error Handling**: Fallback for API failures

#### Skills Matching Algorithm
- Parse skills from Gemini response
- Match against internship skills_required arrays
- Calculate match percentage
- Filter internships based on score range
- Sort by best match percentage

### 5. Frontend Integration Changes

#### Replace Mock Implementation in `/frontend/src/components/HomePage.jsx`:

**Current Mock Code:**
```javascript
const analysis = mockAnalyzeResume();
const matchedInternships = mockInternships.filter(internship => 
  analysis.score >= internship.score_range[0] && analysis.score <= internship.score_range[1]
).slice(0, 5);
```

**New API Integration:**
```javascript
const formData = new FormData();
formData.append('resume', selectedFile);

const response = await axios.post(`${API}/analyze-resume`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

const { analysis, recommendations } = response.data;
setAnalysisResult(analysis);
setRecommendations(recommendations);
```

### 6. Error Handling Requirements
- PDF extraction failures
- Gemini API rate limits/errors
- Invalid file formats
- Network timeouts
- Empty or corrupted PDFs

### 7. Environment Variables
```
GEMINI_API_KEY=AIzaSyBpl2jIVgdaKfHM6Hzniwr_HTVhX2_bD5A
```

### 8. Data Models

#### Resume Analysis Model
```python
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
```

This plan ensures seamless integration between frontend mock data and real backend implementation with proper PDF processing, AI analysis, and skill-based matching.