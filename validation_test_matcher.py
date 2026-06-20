"""
Job Matcher V2 Validation Script

Tests the matcher with various sample JDs and analyzes:
- Skills extraction accuracy
- False positives
- Match score calculation
- Edge cases
"""

import json
from src.matcher import analyze_match
from src.services.skill_extractor import extract_job_skills

# Sample resume data for testing
SAMPLE_RESUME = {
    "name": "Test Candidate",
    "email": "test@example.com",
    "phone": "123-456-7890",
    "skills": [
        "Python", "JavaScript", "React", "Django", "PostgreSQL", 
        "Docker", "Git", "AWS", "SQL", "HTML", "CSS", "Flask",
        "FastAPI", "Redis", "Linux", "REST API", "GraphQL"
    ],
    "experience": [],
    "education": []
}

# Sample Job Descriptions for testing
SAMPLE_JDS = {
    "jd1_python_backend": """
    Senior Python Backend Developer
    
    Requirements:
    - 5+ years of experience with Python
    - Strong knowledge of Django, Flask, or FastAPI
    - Experience with PostgreSQL and Redis
    - Familiarity with Docker and Kubernetes
    - Knowledge of AWS cloud services
    - Experience with REST API development
    - Understanding of microservices architecture
    - Git version control
    - Linux system administration
    """,
    
    "jd2_fullstack": """
    Full Stack Developer
    
    Required Skills:
    - Proficiency in JavaScript and TypeScript
    - Experience with React or Angular
    - Backend development with Node.js or Python
    - Database knowledge (SQL and NoSQL)
    - Experience with MongoDB and PostgreSQL
    - Cloud platforms (AWS, Azure, or GCP)
    - Docker and containerization
    - Git and CI/CD pipelines
    - HTML, CSS, and modern frontend frameworks
    """,
    
    "jd3_data_science": """
    Data Scientist / Machine Learning Engineer
    
    Requirements:
    - Strong Python programming skills
    - Experience with Pandas, NumPy, and Scikit-learn
    - Knowledge of TensorFlow or PyTorch
    - Understanding of machine learning algorithms
    - Experience with data visualization (Matplotlib, Seaborn)
    - SQL database skills
    - Familiarity with big data technologies (Spark, Hadoop)
    - Statistical analysis background
    - Jupyter notebook experience
    """,
    
    "jd4_devops": """
    DevOps Engineer
    
    Required:
    - Strong Linux/Unix administration
    - Docker and Kubernetes expertise
    - CI/CD pipeline implementation (Jenkins, GitLab CI)
    - Infrastructure as Code (Terraform, Ansible)
    - Cloud platform experience (AWS, Azure, GCP)
    - Monitoring and logging (Prometheus, Grafana, ELK)
    - Git version control
    - Scripting skills (Bash, Python)
    - Network and security knowledge
    """,
    
    "jd5_frontend": """
    Frontend Developer
    
    Requirements:
    - Expert in JavaScript and TypeScript
    - Deep knowledge of React ecosystem
    - Experience with Next.js or similar frameworks
    - Strong HTML5 and CSS3 skills
    - Knowledge of state management (Redux, MobX)
    - Experience with modern build tools (Webpack, Vite)
    - Understanding of responsive design
    - Testing frameworks (Jest, Cypress)
    - Git version control
    """,
    
    "jd6_edge_case_generic": """
    Software Developer
    
    We are looking for a software developer with:
    - Good communication skills
    - Teamwork ability
    - Problem-solving mindset
    - Time management
    - Leadership qualities
    - Critical thinking
    - Adaptability
    - Organization skills
    """,
    
    "jd7_edge_case_mixed": """
    Full Stack Engineer
    
    Technical Requirements:
    - Python, Java, or JavaScript
    - React, Angular, or Vue
    - SQL and NoSQL databases
    - Docker and Kubernetes
    - AWS or Azure
    - Git and CI/CD
    
    Soft Skills:
    - Communication and teamwork
    - Problem-solving abilities
    - Time management
    - Leadership experience
    """,
    
    "jd8_edge_case_ambiguous": """
    Developer Position
    
    Requirements:
    - Experience with software development
    - Knowledge of programming
    - Understanding of databases
    - Familiarity with web technologies
    - Good coding skills
    - Strong technical background
    - Experience with frameworks
    - Knowledge of tools
    """
}

def test_skill_extraction():
    """Test skill extraction from various JDs."""
    print("=" * 80)
    print("SKILL EXTRACTION TESTS")
    print("=" * 80)
    
    extraction_results = {}
    
    for jd_name, jd_text in SAMPLE_JDS.items():
        print(f"\n{'='*80}")
        print(f"Testing: {jd_name}")
        print(f"{'='*80}")
        
        extracted_skills = extract_job_skills(jd_text)
        extraction_results[jd_name] = {
            "extracted_skills": sorted(extracted_skills),
            "count": len(extracted_skills)
        }
        
        print(f"Extracted {len(extracted_skills)} skills:")
        for skill in sorted(extracted_skills):
            print(f"  - {skill}")
    
    return extraction_results

def test_match_analysis():
    """Test complete match analysis."""
    print("\n" + "=" * 80)
    print("MATCH ANALYSIS TESTS")
    print("=" * 80)
    
    match_results = {}
    
    for jd_name, jd_text in SAMPLE_JDS.items():
        print(f"\n{'='*80}")
        print(f"Testing: {jd_name}")
        print(f"{'='*80}")
        
        analysis = analyze_match(SAMPLE_RESUME, jd_text)
        
        match_results[jd_name] = analysis
        
        # Print key metrics
        weighted_match = analysis["match_results"]["weighted_match_percentage"]
        tech_match = analysis["technical_vs_soft"]["technical_match_percentage"]
        soft_match = analysis["technical_vs_soft"]["soft_skill_match_percentage"]
        
        print(f"\nOverall Match: {weighted_match}%")
        print(f"Technical Match: {tech_match}%")
        print(f"Soft Skill Match: {soft_match}%")
        
        print(f"\nMatched Skills ({len(analysis['match_results']['matched_skills'])}):")
        for skill in sorted(analysis["match_results"]["matched_skills"]):
            print(f"  ✓ {skill}")
        
        print(f"\nMissing Skills ({len(analysis['match_results']['missing_skills'])}):")
        for skill in sorted(analysis["match_results"]["missing_skills"]):
            print(f"  ✗ {skill}")
        
        print("\nPriority Breakdown:")
        print(f"  High Priority: {analysis['match_results']['high_priority_match']}%")
        print(f"  Medium Priority: {analysis['match_results']['medium_priority_match']}%")
        print(f"  Low Priority: {analysis['match_results']['low_priority_match']}%")
    
    return match_results

def analyze_false_positives(extraction_results):
    """Analyze potential false positives in skill extraction."""
    print("\n" + "=" * 80)
    print("FALSE POSITIVE ANALYSIS")
    print("=" * 80)
    
    false_positives = {
        "generic_terms": [],
        "soft_skills": [],
        "ambiguous_terms": []
    }
    
    # Terms that should NOT be extracted as skills
    problematic_terms = {
        "generic_terms": ["software", "development", "programming", "coding", 
                         "technical", "frameworks", "tools", "technologies"],
        "soft_skills": ["communication", "teamwork", "leadership", "problem-solving",
                       "time management", "critical thinking", "adaptability", "organization"],
        "ambiguous_terms": ["knowledge", "experience", "understanding", "familiarity",
                          "strong", "good", "proficient"]
    }
    
    for jd_name, result in extraction_results.items():
        skills = result["extracted_skills"]
        
        for category, terms in problematic_terms.items():
            for skill in skills:
                if any(term in skill.lower() for term in terms):
                    false_positives[category].append({
                        "jd": jd_name,
                        "skill": skill
                    })
    
    print("\nGeneric Terms Extracted (should be filtered):")
    for fp in false_positives["generic_terms"]:
        print(f"  {fp['jd']}: {fp['skill']}")
    
    print("\nSoft Skills Extracted:")
    for fp in false_positives["soft_skills"]:
        print(f"  {fp['jd']}: {fp['skill']}")
    
    print("\nAmbiguous Terms Extracted:")
    for fp in false_positives["ambiguous_terms"]:
        print(f"  {fp['jd']}: {fp['skill']}")
    
    return false_positives

def generate_validation_report(extraction_results, match_results, false_positives):
    """Generate comprehensive validation report."""
    print("\n" + "=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)
    
    report = {
        "summary": {},
        "skill_extraction": {},
        "match_analysis": {},
        "false_positives": {},
        "weaknesses": [],
        "recommendations": []
    }
    
    # Summary statistics
    total_jds = len(SAMPLE_JDS)
    avg_skills_extracted = sum(r["count"] for r in extraction_results.values()) / total_jds
    avg_match_score = sum(m["match_results"]["weighted_match_percentage"] for m in match_results.values()) / total_jds
    
    report["summary"] = {
        "total_jds_tested": total_jds,
        "avg_skills_extracted": round(avg_skills_extracted, 2),
        "avg_match_score": round(avg_match_score, 2),
        "sample_resume_skills": len(SAMPLE_RESUME["skills"])
    }
    
    print("\nSUMMARY:")
    print(f"  Total JDs Tested: {total_jds}")
    print(f"  Average Skills Extracted: {avg_skills_extracted:.2f}")
    print(f"  Average Match Score: {avg_match_score:.2f}%")
    print(f"  Sample Resume Skills: {len(SAMPLE_RESUME['skills'])}")
    
    # Skill extraction analysis
    print("\nSKILL EXTRACTION BY JD:")
    for jd_name, result in extraction_results.items():
        print(f"  {jd_name}: {result['count']} skills")
        report["skill_extraction"][jd_name] = result
    
    # Match analysis
    print("\nMATCH SCORES BY JD:")
    for jd_name, analysis in match_results.items():
        score = analysis["match_results"]["weighted_match_percentage"]
        print(f"  {jd_name}: {score}%")
        report["match_analysis"][jd_name] = score
    
    # False positives
    total_false_positives = sum(len(v) for v in false_positives.values())
    print(f"\nFALSE POSITIVES: {total_false_positives}")
    report["false_positives"] = false_positives
    
    # Identify weaknesses
    weaknesses = []
    
    # Check for generic terms in extraction
    if false_positives["generic_terms"]:
        weaknesses.append("Generic technical terms are being extracted as skills")
    
    # Check for soft skills in extraction
    if false_positives["soft_skills"]:
        weaknesses.append("Soft skills are being extracted despite being in the whitelist")
    
    # Check for ambiguous terms
    if false_positives["ambiguous_terms"]:
        weaknesses.append("Ambiguous terms are being extracted as skills")
    
    # Check edge cases
    edge_case_jds = ["jd6_edge_case_generic", "jd8_edge_case_ambiguous"]
    for jd in edge_case_jds:
        if jd in extraction_results and extraction_results[jd]["count"] > 0:
            weaknesses.append(f"Edge case JD '{jd}' extracted skills when it shouldn't")
    
    report["weaknesses"] = weaknesses
    
    print("\nIDENTIFIED WEAKNESSES:")
    for i, weakness in enumerate(weaknesses, 1):
        print(f"  {i}. {weakness}")
    
    # Generate recommendations
    recommendations = []
    
    if false_positives["generic_terms"]:
        recommendations.append("Improve stopword filtering to exclude generic technical terms")
    
    if false_positives["soft_skills"]:
        recommendations.append("Consider separating soft skills from technical skills in extraction")
    
    if false_positives["ambiguous_terms"]:
        recommendations.append("Add context-aware filtering to avoid extracting ambiguous terms")
    
    recommendations.append("Add skill validation to ensure extracted terms are actual technologies")
    recommendations.append("Implement confidence scoring for skill extraction")
    recommendations.append("Add support for skill variants and abbreviations")
    
    report["recommendations"] = recommendations
    
    print("\nRECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    return report

def main():
    """Run complete validation."""
    print("JOB MATCHER V2 VALIDATION")
    print("=" * 80)
    
    # Test skill extraction
    extraction_results = test_skill_extraction()
    
    # Test match analysis
    match_results = test_match_analysis()
    
    # Analyze false positives
    false_positives = analyze_false_positives(extraction_results)
    
    # Generate validation report
    report = generate_validation_report(extraction_results, match_results, false_positives)
    
    # Save report to file
    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 80)
    print("Validation complete. Report saved to validation_report.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
