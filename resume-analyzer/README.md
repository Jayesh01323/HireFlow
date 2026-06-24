# HireFlow Resume Analyzer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8)

An AI-powered resume analysis tool that extracts resume information, evaluates ATS readiness, identifies missing skills, and provides actionable career improvement suggestions.

## 🚀 Features

- **Easy Upload**: Drag and drop PDF resumes for instant analysis
- **ATS Analysis**: Get detailed ATS score (0-100) with strengths and weaknesses
- **Smart Extraction**: Automatically extract name, email, phone, skills, education, projects, and experience
- **Improvement Suggestions**: Receive personalized recommendations to enhance your resume
- **Modern UI**: Clean, responsive design that works on all devices
- **Free to Use**: No account required, completely free

## 📸 Screenshots

### Homepage
![Homepage](screenshots/homepage.png)

### Upload Interface
![Upload](screenshots/upload.png)

### Analysis Results
![Results](screenshots/results.png)

## 🛠️ Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **PDF Processing**: PDF.js
- **Deployment**: Vercel

## 📦 Installation

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Steps

1. Clone the repository:
```bash
git clone https://github.com/Jayesh01323/hireflow-resume-analyzer.git
cd hireflow-resume-analyzer
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## 🚀 Deployment

### Deploy to Vercel

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and sign up
3. Click "New Project"
4. Import your GitHub repository
5. Click "Deploy"

Vercel will automatically detect Next.js and configure everything for you.

### Manual Deployment

1. Build the project:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

## 📖 Usage

1. Open the application in your browser
2. Click "Analyze Your Resume" or drag and drop your PDF resume
3. Wait for the analysis to complete
4. Review your ATS score and improvement suggestions
5. Apply the recommendations to improve your resume

## 🔧 Configuration

The application uses simulated AI parsing for demonstration. To integrate with real AI services:

1. Add your API keys to environment variables
2. Update the `extractTextFromPDF` function to use PDF.js
3. Update the `parseResumeText` function to call your AI API
4. Update the `generateATSAnalysis` function to use AI-powered analysis

## 📝 Environment Variables

Create a `.env.local` file in the root directory:

```env
# Add your API keys here
NEXT_PUBLIC_API_KEY=your_api_key_here
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Jayesh Patil**
- Email: jayesh.patil@example.com
- GitHub: [@Jayesh01323](https://github.com/Jayesh01323)

## 🙏 Acknowledgments

- Built for [Digital Heroes](https://digitalheroesco.com) Developer Trial
- Inspired by the need for accessible resume analysis tools
- Built with modern web technologies

## 📞 Support

If you have any questions or need help, please open an issue on GitHub or contact the author.

---

**Built with ❤️ using HireFlow AI Resume Analyzer**
