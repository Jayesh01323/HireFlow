# HireFlow AI

AI-powered career intelligence platform for freshers and entry-level software engineers.

## Features

- **Resume Upload** — Upload and store resumes
- **Resume Parsing** — Extract structured data using Gemini
- **Job Matching** — Match resumes to relevant job openings
- **Skill Gap Analysis** — Identify skills needed for target roles
- **Career Coach** — AI-guided career advice
- **Interview Preparation** — Practice questions and feedback
- **Analytics Dashboard** — Visualize career progress and insights

## Tech Stack

- Python 3.12
- Streamlit
- SQLite
- Gemini API
- PyMuPDF
- Pydantic
- Pandas
- Plotly

## Setup

1. Clone the repository and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy the environment file and add your API key:

   ```bash
   cp .env.example .env
   ```

3. Run the application:

   ```bash
   streamlit run app.py
   ```

## Project Structure

```
hireflow-ai/
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── data/                   # SQLite database and uploads
├── reports/                # Generated reports
├── pages/                  # Streamlit multi-page modules
└── src/                    # Core application logic
```
