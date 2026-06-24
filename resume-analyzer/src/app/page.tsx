"use client";

import { useState } from "react";
import { Upload, FileText, CheckCircle, AlertCircle, XCircle, Download, ArrowRight } from "lucide-react";
import ResumeAnalyzer from "@/components/ResumeAnalyzer";

export default function Home() {
  const [showAnalyzer, setShowAnalyzer] = useState(false);

  if (showAnalyzer) {
    return <ResumeAnalyzer onBack={() => setShowAnalyzer(false)} />;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl mb-6 shadow-lg">
              <FileText className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              HireFlow Resume Analyzer
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              AI-powered resume analysis that evaluates ATS readiness, identifies missing skills, 
              and provides actionable career improvement suggestions.
            </p>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <Upload className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Easy Upload</h3>
              <p className="text-gray-600 text-sm">
                Simply drag and drop your PDF resume for instant analysis
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">ATS Analysis</h3>
              <p className="text-gray-600 text-sm">
                Get detailed ATS score with strengths and weaknesses
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <AlertCircle className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Smart Suggestions</h3>
              <p className="text-gray-600 text-sm">
                Receive personalized improvement recommendations
              </p>
            </div>
          </div>

          {/* CTA Button */}
          <button
            onClick={() => setShowAnalyzer(true)}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            Analyze Your Resume
            <ArrowRight className="w-5 h-5" />
          </button>

          {/* Info */}
          <p className="text-gray-500 mt-6 text-sm">
            Free to use • No account required • Your data stays private
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-auto">
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
    </main>
  );
}
