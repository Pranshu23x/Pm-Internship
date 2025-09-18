import React, { useState, useRef } from 'react';
import { Upload, FileText, Sparkles, Target, MapPin, Building2, Code, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const { toast } = useToast();

  const validateAndSetFile = (file) => {
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setAnalysisResult(null);
      setRecommendations([]);
      return true;
    } else {
      toast({
        title: "Invalid file type",
        description: "Please select a PDF file.",
        variant: "destructive"
      });
      return false;
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    validateAndSetFile(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (validateAndSetFile(file)) {
        // Update the file input to reflect the dropped file
        const dt = new DataTransfer();
        dt.items.add(file);
        if (fileInputRef.current) {
          fileInputRef.current.files = dt.files;
        }
      }
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast({
        title: "No file selected",
        description: "Please select a PDF resume first.",
        variant: "destructive"
      });
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('resume', selectedFile);

      const response = await axios.post(`${API}/analyze-resume`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000 // 60 second timeout
      });

      const { analysis, recommendations } = response.data;
      setAnalysisResult(analysis);
      setRecommendations(recommendations);
      
      toast({
        title: "Analysis complete!",
        description: "Your resume has been analyzed successfully.",
      });
    } catch (error) {
      console.error('Analysis error:', error);
      
      let errorMessage = "Something went wrong. Please try again.";
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = "Analysis took too long. Please try again.";
      } else if (!navigator.onLine) {
        errorMessage = "No internet connection. Please check your connection.";
      }
      
      toast({
        title: "Analysis failed",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedFile(null);
    setAnalysisResult(null);
    setRecommendations([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SkillSync</h1>
                <p className="text-sm text-gray-600">AI-Based Internship Recommendation Engine for PM Internship Scheme</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <Card className="mb-8">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2">
              <Sparkles className="w-6 h-6 text-blue-600" />
              <span>Upload Your Resume</span>
            </CardTitle>
            <CardDescription>
              Upload your PDF resume to get AI-powered analysis and personalized internship recommendations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col items-center space-y-4">
              <div className="w-full max-w-md">
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer ${
                    isDragOver 
                      ? 'border-blue-500 bg-blue-50 scale-102' 
                      : selectedFile 
                        ? 'border-green-400 bg-green-50' 
                        : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                  }`}
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <div className={`transition-all duration-200 ${isDragOver ? 'scale-110' : ''}`}>
                    <Upload className={`w-12 h-12 mx-auto mb-4 ${
                      isDragOver 
                        ? 'text-blue-500' 
                        : selectedFile 
                          ? 'text-green-500' 
                          : 'text-gray-400'
                    }`} />
                  </div>
                  <p className={`text-lg font-medium mb-2 ${
                    isDragOver 
                      ? 'text-blue-700' 
                      : selectedFile 
                        ? 'text-green-700' 
                        : 'text-gray-700'
                  }`}>
                    {isDragOver 
                      ? 'Drop your PDF here' 
                      : selectedFile 
                        ? selectedFile.name 
                        : 'Choose PDF file or drag & drop'
                    }
                  </p>
                  <p className={`text-sm ${
                    isDragOver 
                      ? 'text-blue-600' 
                      : selectedFile 
                        ? 'text-green-600' 
                        : 'text-gray-500'
                  }`}>
                    {isDragOver 
                      ? 'Release to upload' 
                      : selectedFile 
                        ? 'Ready to analyze' 
                        : 'Click to browse or drag and drop your resume'
                    }
                  </p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
              
              <div className="flex space-x-4">
                <Button 
                  onClick={handleAnalyze} 
                  disabled={!selectedFile || isAnalyzing}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4 mr-2" />
                      Analyze Resume
                    </>
                  )}
                </Button>
                
                {(analysisResult || selectedFile) && (
                  <Button variant="outline" onClick={resetAnalysis}>
                    Reset
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {analysisResult && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-green-600" />
                <span>Resume Analysis</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {analysisResult.overall_rating}/10
                  </div>
                  <p className="text-gray-600">Overall Score</p>
                </div>
                
                <div>
                  <h4 className="font-semibold text-green-700 mb-2">Strengths</h4>
                  <ul className="space-y-1">
                    {analysisResult.strengths.map((strength, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                        {strength.trim()}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold text-orange-700 mb-2">Areas to Improve</h4>
                  <ul className="space-y-1">
                    {analysisResult.weaknesses.map((weakness, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                        {weakness.trim()}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {analysisResult.suggestions && analysisResult.suggestions.length > 0 && (
                <div className="mt-6 pt-6 border-t">
                  <h4 className="font-semibold text-blue-700 mb-3">Suggestions for Improvement</h4>
                  <ul className="grid md:grid-cols-2 gap-2">
                    {analysisResult.suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                        {suggestion.trim()}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-blue-600" />
                <span>Recommended Internships ({recommendations.length})</span>
              </CardTitle>
              <CardDescription>
                Based on your skills and resume analysis, here are the best matching internships
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendations.map((internship) => (
                  <Card key={internship.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <Badge variant="secondary" className="mb-2">
                          {internship.category}
                        </Badge>
                        <div className="text-right">
                          <div className="text-sm font-medium text-blue-600">
                            {internship.match_percentage}% Match
                          </div>
                        </div>
                      </div>
                      <CardTitle className="text-lg">{internship.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        <div className="flex items-center text-sm text-gray-600">
                          <Building2 className="w-4 h-4 mr-2" />
                          {internship.company}
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="w-4 h-4 mr-2" />
                          {internship.location}
                        </div>
                        <p className="text-sm text-gray-700 line-clamp-3">
                          {internship.description}
                        </p>
                        
                        {internship.matched_skills.length > 0 && (
                          <div>
                            <div className="flex items-center text-sm font-medium text-green-700 mb-2">
                              <Code className="w-4 h-4 mr-2" />
                              Your Matching Skills
                            </div>
                            <div className="flex flex-wrap gap-1 mb-3">
                              {internship.matched_skills.map((skill, index) => (
                                <Badge key={index} variant="default" className="text-xs bg-green-100 text-green-800">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div>
                          <div className="flex items-center text-sm font-medium text-gray-700 mb-2">
                            <Code className="w-4 h-4 mr-2" />
                            All Required Skills
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {internship.skills_required.map((skill, index) => (
                              <Badge 
                                key={index} 
                                variant="outline" 
                                className={`text-xs ${
                                  internship.matched_skills.includes(skill) 
                                    ? 'border-green-500 text-green-700' 
                                    : 'border-gray-300 text-gray-600'
                                }`}
                              >
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Made with TeamWork by{' '}
              <a 
                href="https://credits-seven.vercel.app/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
              >
                CodexCrew
                <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;