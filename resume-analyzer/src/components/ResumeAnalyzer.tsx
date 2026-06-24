"use client";

import { useState, useRef } from "react";
import { Upload, FileText, CheckCircle, AlertCircle, XCircle, ArrowLeft, Download, Loader2 } from "lucide-react";

interface ParsedResume {
  name: string | null;
  email: string | null;
  phone: string | null;
  skills: Array<{ name: string; level?: string | null }>;
  education: string[];
  projects: string[];
  experience: string[];
}

interface ATSAnalysis {
  score: number;
  strengths: string[];
  weaknesses: string[];
  missingSections: string[];
  suggestions: string[];
}

export default function ResumeAnalyzer({ onBack }: { onBack: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null);
  const [atsAnalysis, setAtsAnalysis] = useState<ATSAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (selectedFile: File) => {
    if (selectedFile.type !== "application/pdf") {
      setError("Please upload a PDF file");
      return;
    }
    setFile(selectedFile);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const analyzeResume = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      // Extract text from PDF
      const text = await extractTextFromPDF(file);

      // Parse resume (simulated - in production, this would call an API)
      const parsed = parseResumeText(text);
      setParsedResume(parsed);

      // Generate ATS analysis (simulated - in production, this would call an AI API)
      const analysis = generateATSAnalysis(parsed);
      setAtsAnalysis(analysis);

    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze resume");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const extractTextFromPDF = async (file: File): Promise<string> => {
    // Simulated PDF extraction
    // In production, this would use pdfjs-dist or call a backend API
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`
          John Doe
          john.doe@email.com
          (555) 123-4567

          Skills:
          - Python (Advanced)
          - JavaScript (Intermediate)
          - React (Intermediate)
          - SQL (Beginner)
          - Git (Intermediate)

          Education:
          - Bachelor of Science in Computer Science, State University, 2020-2024
          - GPA: 3.8/4.0

          Projects:
          - E-commerce Website: Built a full-stack e-commerce platform using React and Node.js
          - Weather App: Created a weather application using Python and Flask
          - Portfolio Website: Developed personal portfolio using Next.js

          Experience:
          - Software Developer Intern, Tech Company, Summer 2023
          - Research Assistant, University Lab, 2022-2023
        `);
      }, 1500);
    });
  };

  const parseResumeText = (text: string): ParsedResume => {
    // Simulated parsing - in production, this would use AI
    return {
      name: "John Doe",
      email: "john.doe@email.com",
      phone: "(555) 123-4567",
      skills: [
        { name: "Python", level: "Advanced" },
        { name: "JavaScript", level: "Intermediate" },
        { name: "React", level: "Intermediate" },
        { name: "SQL", level: "Beginner" },
        { name: "Git", level: "Intermediate" },
      ],
      education: [
        "Bachelor of Science in Computer Science, State University, 2020-2024",
        "GPA: 3.8/4.0",
      ],
      projects: [
        "E-commerce Website: Built a full-stack e-commerce platform using React and Node.js",
        "Weather App: Created a weather application using Python and Flask",
        "Portfolio Website: Developed personal portfolio using Next.js",
      ],
      experience: [
        "Software Developer Intern, Tech Company, Summer 2023",
        "Research Assistant, University Lab, 2022-2023",
      ],
    };
  };

  const generateATSAnalysis = (resume: ParsedResume): ATSAnalysis => {
    // Simulated ATS analysis - in production, this would use AI
    const score = 78;
    return {
      score,
      strengths: [
        "Clear contact information provided",
        "Good mix of technical skills",
        "Relevant project experience",
        "Strong educational background",
        "Well-structured format",
      ],
      weaknesses: [
        "Could add more quantifiable achievements",
        "Consider adding certifications",
        "Skills could be more specific",
        "Missing summary/objective section",
      ],
      missingSections: [
        "Professional Summary",
        "Certifications",
        "Awards/Honors",
      ],
      suggestions: [
        "Add a professional summary at the top highlighting your key strengths",
        "Include specific metrics in your experience (e.g., 'Improved performance by 30%')",
        "List relevant certifications (AWS, Google Cloud, etc.)",
        "Add technical tools and frameworks to skills section",
        "Include links to GitHub, LinkedIn, or portfolio",
      ],
    };
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBackground = (score: number) => {
    if (score >= 80) return "bg-green-100";
    if (score >= 60) return "bg-yellow-100";
    return "bg-red-100";
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="max-w-6xl mx-auto mb-8">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Home
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Resume Analyzer
          </h1>
          <p className="text-gray-600">
            Upload your PDF resume to get instant ATS analysis and improvement suggestions
          </p>
        </div>

        {!parsedResume ? (
          /* Upload Section */
          <div className="max-w-2xl mx-auto">
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                file ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400 bg-white"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                className="hidden"
              />
              <div className="flex flex-col items-center">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
                  file ? "bg-blue-100" : "bg-gray-100"
                }`}>
                  {file ? (
                    <FileText className="w-8 h-8 text-blue-600" />
                  ) : (
                    <Upload className="w-8 h-8 text-gray-400" />
                  )}
                </div>
                {file ? (
                  <div>
                    <p className="font-semibold text-gray-900 mb-1">{file.name}</p>
                    <p className="text-sm text-gray-600">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="font-semibold text-gray-900 mb-2">
                      Drag and drop your resume here
                    </p>
                    <p className="text-gray-600 mb-4">or</p>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                    >
                      Browse Files
                    </button>
                    <p className="text-sm text-gray-500 mt-4">
                      Only PDF files are supported
                    </p>
                  </div>
                )}
              </div>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-red-700">{error}</p>
              </div>
            )}

            {file && (
              <div className="mt-6 flex gap-4">
                <button
                  onClick={analyzeResume}
                  disabled={isAnalyzing}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      Analyze Resume
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    setFile(null);
                    setError(null);
                  }}
                  className="px-6 py-3 rounded-xl font-semibold border-2 border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
              </div>
            )}
          </div>
        ) : (
          /* Results Section */
          <div className="max-w-6xl mx-auto space-y-6">
            {/* ATS Score Card */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">ATS Analysis Results</h2>
              <div className="flex items-center gap-8 mb-8">
                <div className={`w-32 h-32 rounded-full ${getScoreBackground(atsAnalysis!.score)} flex items-center justify-center`}>
                  <span className={`text-4xl font-bold ${getScoreColor(atsAnalysis!.score)}`}>
                    {atsAnalysis!.score}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Overall ATS Score
                  </h3>
                  <p className="text-gray-600">
                    {atsAnalysis!.score >= 80
                      ? "Your resume is well-optimized for ATS systems!"
                      : atsAnalysis!.score >= 60
                      ? "Your resume has good ATS compatibility with room for improvement."
                      : "Your resume needs significant optimization for ATS systems."}
                  </p>
                </div>
              </div>
            </div>

            {/* Parsed Resume */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Extracted Information</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Contact Information</h3>
                  <div className="space-y-2 text-gray-700">
                    <p><span className="font-medium">Name:</span> {parsedResume.name || "Not found"}</p>
                    <p><span className="font-medium">Email:</span> {parsedResume.email || "Not found"}</p>
                    <p><span className="font-medium">Phone:</span> {parsedResume.phone || "Not found"}</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {parsedResume.skills.map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      >
                        {skill.name} {skill.level && `(${skill.level})`}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-6 grid md:grid-cols-3 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Education</h3>
                  <ul className="space-y-2 text-gray-700 text-sm">
                    {parsedResume.education.map((edu, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                        {edu}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Projects</h3>
                  <ul className="space-y-2 text-gray-700 text-sm">
                    {parsedResume.projects.map((project, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                        {project}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Experience</h3>
                  <ul className="space-y-2 text-gray-700 text-sm">
                    {parsedResume.experience.map((exp, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                        {exp}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Analysis Details */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Strengths */}
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  Strengths
                </h2>
                <ul className="space-y-3">
                  {atsAnalysis!.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start gap-3 text-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Weaknesses */}
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <AlertCircle className="w-6 h-6 text-yellow-600" />
                  Areas for Improvement
                </h2>
                <ul className="space-y-3">
                  {atsAnalysis!.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start gap-3 text-gray-700">
                      <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      {weakness}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Missing Sections */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <XCircle className="w-6 h-6 text-red-600" />
                Missing Sections
              </h2>
              <div className="flex flex-wrap gap-3">
                {atsAnalysis!.missingSections.map((section, index) => (
                  <span
                    key={index}
                    className="px-4 py-2 bg-red-100 text-red-800 rounded-lg font-medium"
                  >
                    {section}
                  </span>
                ))}
              </div>
            </div>

            {/* Suggestions */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Download className="w-6 h-6 text-blue-600" />
                Improvement Suggestions
              </h2>
              <ul className="space-y-3">
                {atsAnalysis!.suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-3 text-gray-700">
                    <Download className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>

            {/* Analyze Another Button */}
            <div className="text-center pb-8">
              <button
                onClick={() => {
                  setFile(null);
                  setParsedResume(null);
                  setAtsAnalysis(null);
                  setError(null);
                }}
                className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
              >
                <Upload className="w-5 h-5" />
                Analyze Another Resume
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-8 mt-16">
          <div className="container mx-auto px-4 text-center">
            <div className="mb-4">
              <a
                href="https://digitalheroesco.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                Built for Digital Heroes
              </a>
            </div>
            <div className="text-gray-400 text-sm mb-2">
              <p className="font-semibold text-white">Jayesh Patil</p>
              <p>jayesh.patil@example.com</p>
            </div>
            <p className="text-gray-500 text-xs">
              Built with ❤️ using HireFlow AI Resume Analyzer
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}
