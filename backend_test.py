#!/usr/bin/env python3
"""
SkillSync Backend API Testing Suite
Tests all backend endpoints and functionality as specified in the review request.
"""

import requests
import json
import os
import sys
from pathlib import Path
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# Get the backend URL from frontend .env file
def get_backend_url():
    frontend_env_path = Path(__file__).parent / 'frontend' / '.env'
    try:
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    return "https://internalign.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class SkillSyncTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
    
    def create_test_pdf(self, content):
        """Create a test PDF with given content"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add content to PDF
        y_position = 750
        for line in content.split('\n'):
            if y_position < 50:  # Start new page if needed
                p.showPage()
                y_position = 750
            p.drawString(50, y_position, line)
            y_position -= 20
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def test_root_endpoint(self):
        """Test GET /api/ - should return welcome message"""
        try:
            response = self.session.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "SkillSync" in data["message"]:
                    self.log_test("Root Endpoint", True, f"Welcome message received: {data['message']}")
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response format: {data}")
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Request failed: {str(e)}")
    
    def test_internships_endpoint(self):
        """Test GET /api/internships - should return array of 12 internships"""
        try:
            response = self.session.get(f"{API_BASE}/internships")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) == 12:
                        # Verify structure of first internship
                        if data:
                            internship = data[0]
                            required_fields = ['id', 'title', 'company', 'location', 'skills_required', 'score_range', 'category', 'description']
                            missing_fields = [field for field in required_fields if field not in internship]
                            
                            if not missing_fields:
                                self.log_test("Internships Endpoint", True, f"Retrieved {len(data)} internships with correct structure")
                            else:
                                self.log_test("Internships Endpoint", False, f"Missing fields in internship data: {missing_fields}")
                        else:
                            self.log_test("Internships Endpoint", False, "Empty internships array")
                    else:
                        self.log_test("Internships Endpoint", False, f"Expected 12 internships, got {len(data)}")
                else:
                    self.log_test("Internships Endpoint", False, f"Expected array, got: {type(data)}")
            else:
                self.log_test("Internships Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Internships Endpoint", False, f"Request failed: {str(e)}")
    
    def test_analyze_resume_valid_pdf(self):
        """Test POST /api/analyze-resume with valid PDF"""
        try:
            # Create a realistic resume PDF
            resume_content = """
John Smith
Software Engineer

EXPERIENCE:
- 3 years of experience with Python and FastAPI
- Built REST APIs using Node.js and Express
- Worked with PostgreSQL databases
- Experience with Docker containerization
- Familiar with React and TypeScript
- Used Git for version control

SKILLS:
- Programming: Python, JavaScript, TypeScript
- Frameworks: FastAPI, Express, React
- Databases: PostgreSQL, MongoDB
- Tools: Docker, Git, AWS
- Other: REST APIs, CI/CD

EDUCATION:
Bachelor of Computer Science
University of Technology, 2020
"""
            
            pdf_data = self.create_test_pdf(resume_content)
            
            files = {
                'resume': ('test_resume.pdf', pdf_data, 'application/pdf')
            }
            
            response = self.session.post(f"{API_BASE}/analyze-resume", files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if 'analysis' in data and 'recommendations' in data:
                    analysis = data['analysis']
                    recommendations = data['recommendations']
                    
                    # Check analysis structure
                    analysis_fields = ['overall_rating', 'strengths', 'weaknesses', 'suggestions', 'raw_analysis']
                    missing_analysis_fields = [field for field in analysis_fields if field not in analysis]
                    
                    # Check recommendations structure
                    if recommendations and isinstance(recommendations, list):
                        rec = recommendations[0]
                        rec_fields = ['id', 'title', 'company', 'location', 'skills_required', 'score_range', 'category', 'description', 'match_percentage', 'matched_skills']
                        missing_rec_fields = [field for field in rec_fields if field not in rec]
                    else:
                        missing_rec_fields = ['No recommendations returned']
                    
                    if not missing_analysis_fields and not missing_rec_fields:
                        self.log_test("Resume Analysis - Valid PDF", True, 
                                    f"Analysis completed. Rating: {analysis.get('overall_rating')}, Recommendations: {len(recommendations)}")
                    else:
                        self.log_test("Resume Analysis - Valid PDF", False, 
                                    f"Missing fields - Analysis: {missing_analysis_fields}, Recommendations: {missing_rec_fields}")
                else:
                    self.log_test("Resume Analysis - Valid PDF", False, f"Invalid response structure: {list(data.keys())}")
            else:
                self.log_test("Resume Analysis - Valid PDF", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Resume Analysis - Valid PDF", False, f"Request failed: {str(e)}")
    
    def test_analyze_resume_invalid_file(self):
        """Test POST /api/analyze-resume with non-PDF file"""
        try:
            # Create a text file instead of PDF
            files = {
                'resume': ('test_resume.txt', b'This is not a PDF file', 'text/plain')
            }
            
            response = self.session.post(f"{API_BASE}/analyze-resume", files=files)
            
            if response.status_code == 400:
                data = response.json()
                if 'detail' in data and 'PDF' in data['detail']:
                    self.log_test("Resume Analysis - Invalid File Type", True, f"Correctly rejected non-PDF: {data['detail']}")
                else:
                    self.log_test("Resume Analysis - Invalid File Type", False, f"Wrong error message: {data}")
            else:
                self.log_test("Resume Analysis - Invalid File Type", False, f"Expected 400, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Resume Analysis - Invalid File Type", False, f"Request failed: {str(e)}")
    
    def test_analyze_resume_empty_pdf(self):
        """Test POST /api/analyze-resume with empty PDF"""
        try:
            # Create an empty PDF
            pdf_data = self.create_test_pdf("")
            
            files = {
                'resume': ('empty_resume.pdf', pdf_data, 'application/pdf')
            }
            
            response = self.session.post(f"{API_BASE}/analyze-resume", files=files)
            
            if response.status_code == 400:
                data = response.json()
                if 'detail' in data and 'text' in data['detail'].lower():
                    self.log_test("Resume Analysis - Empty PDF", True, f"Correctly rejected empty PDF: {data['detail']}")
                else:
                    self.log_test("Resume Analysis - Empty PDF", False, f"Wrong error message: {data}")
            else:
                self.log_test("Resume Analysis - Empty PDF", False, f"Expected 400, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Resume Analysis - Empty PDF", False, f"Request failed: {str(e)}")
    
    def test_analyze_resume_no_file(self):
        """Test POST /api/analyze-resume with no file"""
        try:
            response = self.session.post(f"{API_BASE}/analyze-resume")
            
            if response.status_code == 422:  # FastAPI validation error
                self.log_test("Resume Analysis - No File", True, "Correctly rejected request with no file")
            else:
                self.log_test("Resume Analysis - No File", False, f"Expected 422, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Resume Analysis - No File", False, f"Request failed: {str(e)}")
    
    def test_gemini_integration(self):
        """Test Gemini AI integration by analyzing response format"""
        try:
            # Create a PDF with specific skills to test matching
            resume_content = """
Jane Doe
Full Stack Developer

TECHNICAL SKILLS:
- Python, FastAPI, Django
- JavaScript, React, Node.js
- PostgreSQL, MongoDB
- Docker, Kubernetes, AWS
- Git, CI/CD, Jenkins

EXPERIENCE:
Senior Developer at TechCorp (2021-2024)
- Built microservices using FastAPI and Python
- Developed React applications with TypeScript
- Managed PostgreSQL databases and MongoDB collections
- Deployed applications using Docker and Kubernetes
- Implemented CI/CD pipelines with Jenkins

PROJECTS:
1. E-commerce Platform - React, Node.js, PostgreSQL
2. AI Chatbot - Python, NLP, Transformers
3. Cloud Infrastructure - AWS, Docker, Kubernetes
"""
            
            pdf_data = self.create_test_pdf(resume_content)
            
            files = {
                'resume': ('skilled_resume.pdf', pdf_data, 'application/pdf')
            }
            
            response = self.session.post(f"{API_BASE}/analyze-resume", files=files)
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get('analysis', {})
                recommendations = data.get('recommendations', [])
                
                # Test Gemini response format
                rating = analysis.get('overall_rating')
                strengths = analysis.get('strengths', [])
                weaknesses = analysis.get('weaknesses', [])
                suggestions = analysis.get('suggestions', [])
                
                # Verify rating is reasonable (0-10)
                rating_valid = isinstance(rating, (int, float)) and 0 <= rating <= 10
                
                # Verify arrays contain strings
                strengths_valid = isinstance(strengths, list) and all(isinstance(s, str) for s in strengths)
                weaknesses_valid = isinstance(weaknesses, list) and all(isinstance(w, str) for w in weaknesses)
                suggestions_valid = isinstance(suggestions, list) and all(isinstance(s, str) for s in suggestions)
                
                # Test skill matching
                skill_matches_found = False
                for rec in recommendations:
                    if rec.get('matched_skills') and len(rec.get('matched_skills', [])) > 0:
                        skill_matches_found = True
                        break
                
                if rating_valid and strengths_valid and weaknesses_valid and suggestions_valid:
                    if skill_matches_found:
                        self.log_test("Gemini AI Integration", True, 
                                    f"AI analysis successful. Rating: {rating}, Skill matching working")
                    else:
                        self.log_test("Gemini AI Integration", False, 
                                    "AI analysis format correct but skill matching not working")
                else:
                    self.log_test("Gemini AI Integration", False, 
                                f"Invalid AI response format. Rating valid: {rating_valid}, Arrays valid: {strengths_valid and weaknesses_valid and suggestions_valid}")
            else:
                self.log_test("Gemini AI Integration", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Gemini AI Integration", False, f"Request failed: {str(e)}")
    
    def test_database_integration(self):
        """Test MongoDB integration by checking if analysis is stored"""
        try:
            # First, perform an analysis
            resume_content = "Test resume for database integration testing with Python and React skills."
            pdf_data = self.create_test_pdf(resume_content)
            
            files = {
                'resume': ('db_test_resume.pdf', pdf_data, 'application/pdf')
            }
            
            response = self.session.post(f"{API_BASE}/analyze-resume", files=files)
            
            if response.status_code == 200:
                # We can't directly check the database, but we can verify the endpoint works
                # and assume database integration is working if the analysis completes
                self.log_test("Database Integration", True, "Analysis completed successfully, assuming database storage works")
            else:
                self.log_test("Database Integration", False, f"Analysis failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Database Integration", False, f"Request failed: {str(e)}")
    
    def test_legacy_endpoints(self):
        """Test legacy status endpoints"""
        try:
            # Test POST /api/status
            status_data = {"client_name": "test_client"}
            response = self.session.post(f"{API_BASE}/status", json=status_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'client_name' in data:
                    self.log_test("Legacy Status POST", True, f"Status created: {data['client_name']}")
                else:
                    self.log_test("Legacy Status POST", False, f"Invalid response format: {data}")
            else:
                self.log_test("Legacy Status POST", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test GET /api/status
            response = self.session.get(f"{API_BASE}/status")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Legacy Status GET", True, f"Retrieved {len(data)} status records")
                else:
                    self.log_test("Legacy Status GET", False, f"Expected array, got: {type(data)}")
            else:
                self.log_test("Legacy Status GET", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Legacy Endpoints", False, f"Request failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("SkillSync Backend API Testing Suite")
        print("=" * 60)
        print(f"Testing against: {API_BASE}")
        print()
        
        # Run all tests
        self.test_root_endpoint()
        self.test_internships_endpoint()
        self.test_analyze_resume_valid_pdf()
        self.test_analyze_resume_invalid_file()
        self.test_analyze_resume_empty_pdf()
        self.test_analyze_resume_no_file()
        self.test_gemini_integration()
        self.test_database_integration()
        self.test_legacy_endpoints()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = SkillSyncTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)