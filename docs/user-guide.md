# HireFlow AI - User Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Resume Parser](#resume-parser)
- [Job Discovery](#job-discovery)
- [Job Matcher](#job-matcher)
- [Skill Gap Analysis](#skill-gap-analysis)
- [Career Coach](#career-coach)
- [Career Copilot](#career-copilot)
- [Application Tracker](#application-tracker)
- [Analytics Dashboard](#analytics-dashboard)
- [Learning Roadmap](#learning-roadmap)
- [Career Fit](#career-fit)
- [Interview Preparation](#interview-preparation)
- [Tips & Best Practices](#tips--best-practices)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### First-Time Setup

1. **Launch the Application**
   ```bash
   streamlit run app.py
   ```
   The application will open in your browser at `http://localhost:8501`

2. **Navigate the Interface**
   - Use the sidebar to navigate between features
   - Each feature is organized as a separate page
   - The main page provides an overview of all features

3. **Configure Your Profile**
   - Upload your resume first
   - Set your job preferences
   - Configure alert settings

---

## Resume Parser

### Overview

The Resume Parser uses AI to extract structured data from your PDF resume, including skills, experience, education, and projects.

### How to Use

1. **Navigate to Resume Parser**
   - Click "Resume Parser" in the sidebar

2. **Upload Your Resume**
   - Click "Upload Resume" button
   - Select your PDF resume file
   - Wait for upload to complete

3. **Review Parsed Data**
   - Check extracted personal information
   - Verify skills are correctly identified
   - Review experience and education
   - Examine project details

4. **Edit if Needed**
   - Click "Edit" to correct any errors
   - Update incorrect information
   - Add missing skills or projects

5. **Save to Database**
   - Click "Save" to store parsed resume
   - Resume will be available for other features

### Best Practices

- **Use Clean PDFs**: Ensure your resume is a clean, text-based PDF
- **Standard Format**: Use standard resume formats for better parsing
- **Clear Sections**: Clearly label sections (Skills, Experience, Education)
- **Complete Information**: Include all relevant details for better analysis
- **Multiple Resumes**: Upload different versions for different roles

### Troubleshooting

**Issue**: Resume not parsing correctly
- **Solution**: Ensure PDF is text-based, not scanned images
- **Solution**: Check that sections are clearly labeled
- **Solution**: Try converting PDF to text and re-creating

**Issue**: Skills not extracted
- **Solution**: List skills in a dedicated skills section
- **Solution**: Use standard skill names
- **Solution**: Include proficiency levels if possible

---

## Job Discovery

### Overview

Job Discovery aggregates job listings from multiple platforms (LinkedIn, Internshala, Naukri, Glassdoor, Wellfound) and provides advanced filtering and search capabilities.

### How to Use

1. **Navigate to Job Discovery**
   - Click "Job Discovery" in the sidebar

2. **Search for Jobs**
   - Enter job title or keywords in search box
   - Add location preference
   - Click "Search" button

3. **Apply Filters**
   - **Remote**: Filter for remote positions
   - **Salary Range**: Set minimum and maximum salary
   - **Experience Level**: Filter by experience required
   - **Work Mode**: Full-time, Part-time, Contract, Internship
   - **Source**: Filter by job platform

4. **Review Results**
   - Browse job listings
   - View job details by clicking on cards
   - Check company information and requirements

5. **Save Interesting Jobs**
   - Click "Save" on jobs you're interested in
   - Add notes for each saved job
   - Saved jobs appear in Application Tracker

### Advanced Features

- **Deduplication**: Automatically removes duplicate job postings
- **Freshness Indicator**: Shows how recently the job was posted
- **Salary Normalization**: Standardizes salary formats
- **Skill Extraction**: Identifies required skills from job descriptions

### Best Practices

- **Broad Searches**: Start with broad searches, then narrow down
- **Multiple Keywords**: Try different keyword combinations
- **Location Flexibility**: Consider multiple locations
- **Regular Updates**: Check for new jobs regularly
- **Save Promising Jobs**: Save jobs even if not applying immediately

### Troubleshooting

**Issue**: No jobs found
- **Solution**: Try broader search terms
- **Solution**: Remove some filters
- **Solution**: Check different locations
- **Solution**: Try different job sources

**Issue**: Jobs not loading
- **Solution**: Check internet connection
- **Solution**: Refresh the page
- **Solution**: Check if job sources are accessible

---

## Job Matcher

### Overview

Job Matcher compares your resume skills against job requirements using intelligent weighted scoring, providing detailed match analysis and skill gap recommendations.

### How to Use

1. **Navigate to Job Matcher**
   - Click "Job Matcher" in the sidebar

2. **Select Your Resume**
   - Choose from your uploaded resumes
   - If no resumes, upload one first in Resume Parser

3. **Paste Job Description**
   - Copy job description from job posting
   - Paste into the job description text area
   - Ensure full description is included

4. **Analyze Match**
   - Click "Analyze Match" button
   - Wait for analysis to complete
   - Review detailed results

5. **Review Match Results**
   - **Overall Match**: Weighted match percentage
   - **Technical Match**: Technical skills match
   - **Soft Skill Match**: Soft skills match
   - **Priority Breakdown**: High/Medium/Low priority matches

6. **Examine Skill Analysis**
   - **Matched Skills**: Skills you have that match requirements
   - **Missing Skills**: Skills you need to acquire
   - **Priority Indicators**: HIGH/MED/LOW priority for missing skills

7. **Review Recommendations**
   - **Top Priority Skills**: Most important skills to learn
   - **Learning Recommendations**: Specific learning resources
   - **Career Direction**: Suggested career path
   - **Category Insights**: Breakdown by skill categories

8. **View Visual Analytics**
   - **Skill Categories**: Pie chart of your skill distribution
   - **Match Distribution**: Bar chart of category matches
   - **Gap Analysis**: Visual representation of skill gaps

### Understanding Scores

- **70%+**: Strong match - Good fit for the role
- **50-70%**: Moderate match - Some gaps to address
- **<50%**: Weak match - Significant skill gaps

### Priority Levels

- **HIGH**: Critical skills required for the role
- **MEDIUM**: Important skills that enhance candidacy
- **LOW**: Nice-to-have skills

### Best Practices

- **Complete Job Descriptions**: Use full job descriptions for accurate analysis
- **Multiple Comparisons**: Compare your resume against multiple jobs
- **Focus on High Priority**: Prioritize learning HIGH priority skills
- **Track Progress**: Monitor improvement over time
- **Use Insights**: Apply recommendations to improve your profile

### Troubleshooting

**Issue**: Low match score
- **Solution**: Ensure job description is complete
- **Solution**: Check if resume is up-to-date
- **Solution**: Consider if role is a good fit
- **Solution**: Focus on learning missing skills

**Issue**: Skills not recognized
- **Solution**: Use standard skill names in resume
- **Solution**: Ensure skills are clearly listed
- **Solution**: Update resume with missing skills

---

## Skill Gap Analysis

### Overview

Skill Gap Analysis identifies the difference between your current skills and the skills required for your target role, providing personalized learning recommendations.

### How to Use

1. **Navigate to Skill Gap**
   - Click "Skill Gap" in the sidebar

2. **Select Resume**
   - Choose your resume from the list

3. **Select Target Role**
   - Choose from predefined roles or enter custom role
   - Examples: Python Developer, Data Scientist, DevOps Engineer

4. **Analyze Gap**
   - Click "Analyze Skill Gap" button
   - Review the gap analysis results

5. **Review Results**
   - **Current Skills**: Skills you currently have
   - **Required Skills**: Skills needed for target role
   - **Missing Skills**: Skills you need to learn
   - **Skill Levels**: Your proficiency vs required level

6. **View Learning Path**
   - **Priority Order**: Skills in order of importance
   - **Learning Resources**: Recommended courses and tutorials
   - **Time Estimates**: Estimated time to learn each skill
   - **Prerequisites**: Skills to learn before others

### Learning Recommendations

- **Online Courses**: Coursera, Udemy, edX recommendations
- **Documentation**: Official documentation and tutorials
- **Projects**: Practical project ideas
- **Certifications**: Relevant certifications to pursue

### Best Practices

- **Set Realistic Goals**: Choose achievable learning targets
- **Focus on Fundamentals**: Master basics before advanced topics
- **Practice Regularly**: Consistent practice is key
- **Build Projects**: Apply skills in real projects
- **Track Progress**: Monitor your learning journey

### Troubleshooting

**Issue**: No target role available
- **Solution**: Enter custom role name
- **Solution**: Choose similar role from list
- **Solution**: Contact support to add role

**Issue**: Too many missing skills
- **Solution**: Focus on top 5-10 priority skills
- **Solution**: Break learning into smaller goals
- **Solution**: Start with foundational skills

---

## Career Coach

### Overview

Career Coach provides AI-powered personalized career advice based on your profile, experience, and goals.

### How to Use

1. **Navigate to Career Coach**
   - Click "Career Coach" in the sidebar

2. **Select Your Profile**
   - Choose your resume or profile
   - Ensure profile is complete and up-to-date

3. **Ask Career Questions**
   - Type your career-related question
   - Examples:
     - "How can I transition from web development to data science?"
     - "What skills should I focus on for a senior role?"
     - "How do I negotiate salary?"

4. **Get Advice**
   - Click "Get Advice" button
   - Review AI-generated career advice
   - Advice is personalized to your profile

5. **Follow Recommendations**
   - Implement suggested actions
   - Track progress over time
   - Ask follow-up questions

### Question Categories

- **Career Transitions**: Moving between roles or industries
- **Skill Development**: What skills to learn and when
- **Job Search**: Strategies for finding opportunities
- **Interview Preparation**: How to prepare for interviews
- **Salary Negotiation**: How to negotiate compensation
- **Career Growth**: Advancement strategies

### Best Practices

- **Be Specific**: Ask specific, detailed questions
- **Provide Context**: Include relevant background information
- **Follow Up**: Ask follow-up questions for deeper insights
- **Take Action**: Implement recommendations
- **Track Results**: Monitor outcomes of advice

### Troubleshooting

**Issue**: Generic advice
- **Solution**: Provide more specific context
- **Solution**: Include your current skills and goals
- **Solution**: Ask more targeted questions

**Issue**: Advice not relevant
- **Solution**: Ensure your profile is accurate
- **Solution**: Update your resume with recent experience
- **Solution**: Clarify your career goals

---

## Career Copilot

### Overview

Career Copilot is an interactive AI chat interface for real-time career guidance and Q&A.

### How to Use

1. **Navigate to Career Copilot**
   - Click "Career Copilot" in the sidebar

2. **Start Conversation**
   - Type your question in the chat box
   - Press Enter or click Send
   - AI will respond with personalized advice

3. **Continue Conversation**
   - Ask follow-up questions
   - Provide additional context
   - Explore different topics

4. **Review Conversation History**
   - Previous messages are displayed
   - Scroll to review earlier parts of conversation
   - Reference previous advice

### Use Cases

- **Quick Questions**: Get quick answers to career questions
- **Brainstorming**: Explore career options and ideas
- **Decision Making**: Get help with career decisions
- **Problem Solving**: Address career challenges
- **Learning Guidance**: Get learning recommendations

### Best Practices

- **Clear Questions**: Ask clear, specific questions
- **Context**: Provide relevant background information
- **Follow-up**: Ask clarifying questions
- **Multiple Perspectives**: Explore different angles
- **Actionable**: Focus on actionable advice

### Troubleshooting

**Issue**: Copilot not responding
- **Solution**: Check internet connection
- **Solution**: Refresh the page
- **Solution**: Check API key configuration

**Issue**: Irrelevant responses
- **Solution**: Provide more context
- **Solution**: Ask more specific questions
- **Solution**: Rephrase your question

---

## Application Tracker

### Overview

Application Tracker helps you manage job applications throughout the entire application process, from discovery to offer.

### How to Use

1. **Navigate to Application Tracker**
   - Click "Application Tracker" in the sidebar

2. **Add New Application**
   - Click "Add Application" button
   - Fill in application details:
     - Job title and company
     - Application date
     - Status (Saved, Applied, Interview, Offer, Rejected)
     - Resume used
     - Notes and follow-up reminders

3. **Track Progress**
   - Update application status as you progress
   - Add interview dates and feedback
   - Record offer details if received
   - Add rejection feedback for learning

4. **View Dashboard**
   - **Applications by Status**: Overview of application pipeline
   - **Response Rate**: Track response rates
   - **Time to Response**: Average response time
   - **Success Rate**: Offer vs application ratio

5. **Set Reminders**
   - Add follow-up reminders
   - Set interview preparation reminders
   - Schedule application deadline reminders

### Application Statuses

- **Saved**: Job saved for future application
- **Applied**: Application submitted
- **Interview**: Interview scheduled or completed
- **Offer**: Job offer received
- **Rejected**: Application rejected

### Best Practices

- **Update Regularly**: Keep application status current
- **Detailed Notes**: Record interview feedback and observations
- **Track Metrics**: Monitor your application metrics
- **Follow Up**: Set reminders for follow-ups
- **Learn from Rejections**: Use rejection feedback to improve

### Troubleshooting

**Issue**: Can't find application
- **Solution**: Use search/filter功能
- **Solution**: Check different status categories
- **Solution**: Verify application was saved

**Issue**: Status not updating
- **Solution**: Refresh the page
- **Solution**: Check for error messages
- **Solution**: Try again after a few moments

---

## Analytics Dashboard

### Overview

Analytics Dashboard provides comprehensive insights into your job search progress, skill development, and application metrics.

### How to Use

1. **Navigate to Analytics Dashboard**
   - Click "Analytics Dashboard" in the sidebar

2. **View Overview Metrics**
   - **Total Applications**: Number of applications submitted
   - **Interview Rate**: Percentage of applications leading to interviews
   - **Offer Rate**: Percentage of interviews leading to offers
   - **Response Time**: Average time to hear back

3. **Analyze Skill Distribution**
   - **Skill Categories**: Breakdown of skills by category
   - **Skill Levels**: Proficiency levels for each skill
   - **Skill Growth**: Progress in skill development over time

4. **Review Application Trends**
   - **Applications Over Time**: Application submission timeline
   - **Status Breakdown**: Distribution of application statuses
   - **Source Analysis**: Which job sources are most effective

5. **Track Career Readiness**
   - **Readiness Score**: Overall career readiness assessment
   - **Skill Coverage**: How well your skills match job market
   - **Improvement Areas**: Areas needing improvement

### Dashboard Features

- **Interactive Charts**: Hover for details, zoom for closer look
- **Date Range**: Filter by time period
- **Export**: Export data as CSV or PDF
- **Custom Views**: Create custom dashboard views

### Best Practices

- **Regular Review**: Check dashboard weekly
- **Track Trends**: Look for patterns in your data
- **Set Goals**: Use metrics to set improvement goals
- **Compare Periods**: Compare different time periods
- **Actionable Insights**: Use insights to guide actions

### Troubleshooting

**Issue**: Charts not loading
- **Solution**: Refresh the page
- **Solution**: Check internet connection
- **Solution**: Clear browser cache

**Issue**: Data not updating
- **Solution**: Ensure applications are being tracked
- **Solution**: Check if data is being saved
- **Solution**: Verify database connection

---

## Learning Roadmap

### Overview

Learning Roadmap generates personalized learning plans based on your skill gaps and career goals.

### How to Use

1. **Navigate to Learning Roadmap**
   - Click "Learning Roadmap" in the sidebar

2. **Select Target Role**
   - Choose your target role from the list
   - Or enter a custom role

3. **Set Timeline**
   - Choose learning timeline:
     - 7 days (quick wins)
     - 30 days (focused learning)
     - 90 days (comprehensive learning)

4. **Generate Roadmap**
   - Click "Generate Roadmap" button
   - Review the personalized learning plan

5. **Follow Roadmap**
   - **Milestones**: Key learning milestones
   - **Resources**: Recommended learning resources
   - **Projects**: Practical projects to build
   - **Timeline**: Suggested timeline for each milestone

6. **Track Progress**
   - Mark completed milestones
   - Update progress percentage
   - Add notes on learning experience

### Roadmap Components

- **Skill Priorities**: Skills in order of importance
- **Learning Resources**: Courses, tutorials, documentation
- **Practice Projects**: Real-world projects to build
- **Assessment Criteria**: How to measure progress
- **Time Estimates**: Expected time for each milestone

### Best Practices

- **Stick to Timeline**: Follow suggested timeline
- **Complete Projects**: Build practical projects
- **Assess Progress**: Regularly assess your learning
- **Adjust as Needed**: Modify roadmap based on progress
- **Document Learning**: Keep notes on what you learn

### Troubleshooting

**Issue**: Roadmap too ambitious
- **Solution**: Choose longer timeline
- **Solution**: Focus on top priorities
- **Solution**: Break milestones into smaller tasks

**Issue**: Resources not helpful
- **Solution**: Try alternative resources
- **Solution**: Search for additional resources
- **Solution**: Ask community for recommendations

---

## Career Fit

### Overview

Career Fit analyzes your profile against various career paths to identify the best matches for your skills and experience.

### How to Use

1. **Navigate to Career Fit**
   - Click "Career Fit" in the sidebar

2. **Select Your Profile**
   - Choose your resume or profile

3. **Analyze Career Options**
   - Click "Analyze Career Fit" button
   - Review career path recommendations

4. **Review Results**
   - **Top Career Paths**: Best matching career paths
   - **Fit Scores**: How well you fit each path
   - **Skill Alignment**: How your skills match each path
   - **Growth Opportunities**: Growth potential for each path

5. **Explore Career Paths**
   - Click on career paths for detailed analysis
   - View required skills and experience
   - Check salary ranges and job outlook
   - Read career progression information

### Career Path Categories

- **Software Development**: Frontend, Backend, Full-Stack
- **Data Science**: Data Analyst, Data Scientist, ML Engineer
- **DevOps**: DevOps Engineer, SRE, Cloud Architect
- **Product**: Product Manager, Product Designer
- **Management**: Engineering Manager, CTO

### Best Practices

- **Open Exploration**: Explore multiple career paths
- **Consider Growth**: Look at long-term growth potential
- **Skill Alignment**: Choose paths aligned with your interests
- **Market Demand**: Consider job market demand
- **Salary Expectations**: Research salary ranges

### Troubleshooting

**Issue**: No good career matches
- **Solution**: Update your profile with more skills
- **Solution**: Add more experience details
- **Solution**: Consider broader career categories

**Issue**: Fit scores seem low
- **Solution**: Ensure profile is complete
- **Solution**: Add more relevant experience
- **Solution**: Include all your skills

---

## Interview Preparation

### Overview

Interview Preparation generates role-specific interview questions and provides preparation tips based on job requirements.

### How to Use

1. **Navigate to Interview Prep**
   - Click "Interview Preparation" in the sidebar

2. **Select Job**
   - Choose a job from your saved applications
   - Or paste job description manually

3. **Generate Questions**
   - Select question type:
     - Technical questions
     - Behavioral questions
     - System design questions
   - Click "Generate Questions" button

4. **Review Questions**
   - **Technical Questions**: Role-specific technical questions
   - **Behavioral Questions**: STAR method questions
   - **System Design**: Architecture and design questions

5. **Practice Answers**
   - Write out your answers
   - Practice speaking your answers
   - Time yourself for each question

6. **Get Feedback**
   - Record your practice sessions
   - Review and improve your answers
   - Focus on areas needing improvement

### Question Types

- **Technical**: Language-specific, framework-specific, algorithms
- **Behavioral**: Situational, leadership, teamwork
- **System Design**: Architecture, scalability, trade-offs
- **Company-Specific**: Company culture, values, products

### Best Practices

- **Practice Regularly**: Consistent practice improves performance
- **STAR Method**: Use STAR for behavioral questions
- **Research Company**: Learn about the company and role
- **Prepare Examples**: Have specific examples ready
- **Mock Interviews**: Practice with friends or mentors

### Troubleshooting

**Issue**: Questions not relevant
- **Solution**: Ensure job description is complete
- **Solution**: Choose specific question types
- **Solution**: Update job details if changed

**Issue**: Too many questions
- **Solution**: Focus on top 10-15 questions
- **Solution**: Prioritize by importance
- **Solution**: Practice in multiple sessions

---

## Tips & Best Practices

### General Tips

1. **Keep Profile Updated**: Regularly update your resume and profile
2. **Be Specific**: Provide detailed information for better analysis
3. **Use All Features**: Leverage all features for comprehensive career management
4. **Track Progress**: Monitor your progress over time
5. **Take Action**: Implement recommendations and advice

### Job Search Tips

1. **Apply Strategically**: Focus on quality over quantity
2. **Customize Applications**: Tailor each application
3. **Follow Up**: Send follow-up emails after applications
4. **Network**: Leverage your professional network
5. **Stay Organized**: Use Application Tracker effectively

### Skill Development Tips

1. **Learn Fundamentals**: Master basics before advanced topics
2. **Build Projects**: Apply skills in real projects
3. **Get Certified**: Obtain relevant certifications
4. **Stay Current**: Keep up with industry trends
5. **Teach Others**: Teaching reinforces learning

### Interview Tips

1. **Research Thoroughly**: Learn about company and role
2. **Practice Consistently**: Regular interview practice
3. **Prepare Examples**: Have specific examples ready
4. **Ask Questions**: Prepare thoughtful questions for interviewers
5. **Follow Up**: Send thank-you notes after interviews

---

## Troubleshooting

### Common Issues

#### Application Not Responding

**Symptoms**: Application freezes or doesn't respond

**Solutions**:
- Refresh the page
- Check internet connection
- Clear browser cache
- Try a different browser
- Check if Streamlit server is running

#### Data Not Saving

**Symptoms**: Changes not persisting

**Solutions**:
- Check database connection
- Verify write permissions
- Check disk space
- Restart the application
- Check error logs

#### API Errors

**Symptoms**: API-related error messages

**Solutions**:
- Verify API key is valid
- Check API quota limits
- Review error messages
- Check internet connection
- Contact support if needed

#### Performance Issues

**Symptoms**: Application is slow or unresponsive

**Solutions**:
- Clear browser cache
- Close other tabs
- Check system resources
- Reduce data size
- Use pagination for large datasets

### Getting Help

If you encounter issues not covered here:

1. **Check Documentation**: Review other documentation files
2. **Search Issues**: Check GitHub Issues for similar problems
3. **Create Issue**: Create a new issue with details
4. **Contact Support**: Email jayesh@example.com

---

## Keyboard Shortcuts

### Navigation

- **Alt + S**: Navigate to sidebar
- **Alt + R**: Resume Parser
- **Alt + J**: Job Discovery
- **Alt + M**: Job Matcher
- **Alt + A**: Analytics Dashboard

### Actions

- **Ctrl + S**: Save (where applicable)
- **Ctrl + Enter**: Submit form
- **Esc**: Close modal/dialog
- **Ctrl + F**: Search (where available)

---

## Accessibility

### Screen Reader Support

The application is designed to be accessible with screen readers. Use semantic HTML and ARIA labels throughout.

### Keyboard Navigation

All features are accessible via keyboard. Use Tab to navigate and Enter to activate.

### High Contrast Mode

The application supports high contrast mode for better visibility.

---

## Mobile Support

The application is responsive and works on mobile devices, though some features may be optimized for desktop use.

---

**Last Updated**: June 20, 2026  
**Maintained By**: Jayesh  
**Version**: 1.0.0
