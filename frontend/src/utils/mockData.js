// Mock data for testing frontend functionality before backend integration

export const mockInternships = [
  {
    "id": 9,
    "title": "Backend Developer Intern",
    "company": "CodeCrafters",
    "location": "Remote",
    "skills_required": ["Node.js", "Express", "PostgreSQL", "Docker"],
    "score_range": [6, 8],
    "category": "Backend Development",
    "description": "Develop scalable backend services and work with APIs and database optimization."
  },
  {
    "id": 10,
    "title": "Frontend Developer Intern",
    "company": "PixelSoft",
    "location": "Pune, India",
    "skills_required": ["React", "TypeScript", "TailwindCSS", "REST APIs"],
    "score_range": [5, 7],
    "category": "Frontend Development",
    "description": "Work on responsive UI design and integrate APIs for a modern web experience."
  },
  {
    "id": 11,
    "title": "Cloud Engineering Intern",
    "company": "Nimbus Systems",
    "location": "Remote",
    "skills_required": ["AWS", "Docker", "Kubernetes", "CI/CD"],
    "score_range": [7, 9],
    "category": "Cloud / DevOps",
    "description": "Assist in deploying cloud-native applications and managing CI/CD pipelines."
  },
  {
    "id": 12,
    "title": "Mobile App Developer Intern",
    "company": "AppWorks",
    "location": "Hyderabad, India",
    "skills_required": ["Flutter", "Firebase", "Dart", "Git"],
    "score_range": [5, 7],
    "category": "Mobile Development",
    "description": "Develop cross-platform mobile apps and integrate backend APIs."
  },
  {
    "id": 13,
    "title": "AI Chatbot Intern",
    "company": "DialogFlow Labs",
    "location": "Bangalore, India",
    "skills_required": ["Python", "NLP", "Transformers", "FastAPI"],
    "score_range": [7, 9],
    "category": "AI / ML / NLP",
    "description": "Build and optimize conversational AI chatbots using NLP techniques."
  },
  {
    "id": 14,
    "title": "Data Engineering Intern",
    "company": "DataForge",
    "location": "Remote",
    "skills_required": ["SQL", "ETL", "Python", "Apache Spark"],
    "score_range": [6, 8],
    "category": "Data Engineering",
    "description": "Build and maintain data pipelines and support analytics teams."
  },
  {
    "id": 15,
    "title": "Cybersecurity Analyst Intern",
    "company": "FortShield",
    "location": "Mumbai, India",
    "skills_required": ["SIEM Tools", "Threat Analysis", "Python", "Networking"],
    "score_range": [6, 8],
    "category": "Cybersecurity / InfoSec",
    "description": "Assist in monitoring systems, analyzing threats, and drafting reports."
  },
  {
    "id": 16,
    "title": "Blockchain Developer Intern",
    "company": "ChainTech",
    "location": "Remote",
    "skills_required": ["Solidity", "Ethereum", "Web3.js", "Smart Contracts"],
    "score_range": [7, 9],
    "category": "Blockchain",
    "description": "Design and implement smart contracts and decentralized applications."
  },
  {
    "id": 17,
    "title": "Fullstack Intern",
    "company": "NextGen Coders",
    "location": "Delhi, India",
    "skills_required": ["MERN Stack", "REST APIs", "GitHub Actions"],
    "score_range": [6, 8],
    "category": "Fullstack Development",
    "description": "Contribute to fullstack projects with focus on performance and testing."
  },
  {
    "id": 18,
    "title": "AI Vision Intern",
    "company": "VisionX Labs",
    "location": "Remote",
    "skills_required": ["OpenCV", "TensorFlow", "Deep Learning", "Python"],
    "score_range": [7, 9],
    "category": "AI / Computer Vision",
    "description": "Work on computer vision models for object detection and recognition."
  },
  {
    "id": 19,
    "title": "DevOps Intern",
    "company": "Pipeline.io",
    "location": "Chennai, India",
    "skills_required": ["Jenkins", "Docker", "Kubernetes", "Linux"],
    "score_range": [6, 8],
    "category": "DevOps / SRE",
    "description": "Manage CI/CD pipelines, automate deployments, and support developers."
  },
  {
    "id": 20,
    "title": "Penetration Testing Intern",
    "company": "HackLabs",
    "location": "Remote",
    "skills_required": ["Burp Suite", "OWASP", "Python", "Networking"],
    "score_range": [7, 9],
    "category": "Cybersecurity / Ethical Hacking",
    "description": "Perform penetration tests, exploit simulations, and vulnerability reports."
  }
];

export const mockAnalyzeResume = () => {
  // Simulate different analysis results
  const mockResults = [
    {
      score: 7.5,
      strengths: [
        "Strong programming fundamentals in JavaScript and Python",
        "Good experience with React framework",
        "Solid understanding of database concepts",
        "Active GitHub profile with multiple projects"
      ],
      weaknesses: [
        "Limited experience with cloud platforms",
        "Could improve system design knowledge",
        "Lacks experience with containerization tools"
      ],
      suggestions: [
        "Consider learning Docker and Kubernetes",
        "Gain experience with AWS or other cloud platforms",
        "Work on larger scale projects to improve system design skills"
      ]
    },
    {
      score: 6.2,
      strengths: [
        "Good foundation in computer science concepts",
        "Experience with web development technologies",
        "Strong problem-solving skills demonstrated through projects"
      ],
      weaknesses: [
        "Limited professional experience",
        "Could strengthen knowledge of modern frameworks",
        "Needs more experience with version control"
      ],
      suggestions: [
        "Contribute to open source projects",
        "Learn modern development frameworks like React or Angular",
        "Practice with Git and collaborative development"
      ]
    }
  ];
  
  return mockResults[Math.floor(Math.random() * mockResults.length)];
};