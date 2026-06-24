"""
Job Normalizer Module

Normalizes job postings from different sources into a consistent format.
Handles company name standardization, location parsing, salary extraction.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

from src.jobs.schemas import JobPosting, NormalizedJob
from src.services.skill_extractor import extract_job_skills

logger = logging.getLogger(__name__)


class JobNormalizer:
    """Normalizes job postings from various sources."""
    
    def __init__(self) -> None:
        """Initialize job normalizer with normalization rules and mappings."""
        self.company_aliases: Dict[str, str] = self._load_company_aliases()
        self.location_mappings: Dict[str, str] = self._load_location_mappings()
        self.title_variations: Dict[str, str] = self._load_title_variations()
    
    def _load_company_aliases(self) -> Dict[str, str]:
        """Load company name aliases for normalization."""
        return {
            "google llc": "Google",
            "alphabet inc": "Google",
            "microsoft corporation": "Microsoft",
            "microsoft": "Microsoft",
            "amazon com": "Amazon",
            "amazon web services": "AWS",
            "meta platforms": "Meta",
            "facebook": "Meta",
            "apple inc": "Apple",
            "tata consultancy services": "TCS",
            "infosys limited": "Infosys",
            "wipro limited": "Wipro",
            "hcl technologies": "HCL",
            "accenture plc": "Accenture",
            "ibm india": "IBM",
            "flipkart internet": "Flipkart",
            "swiggy": "Swiggy",
            "zomato": "Zomato",
            "paytm": "Paytm",
            "phonepe": "PhonePe",
            "razorpay": "Razorpay",
        }
    
    def _load_location_mappings(self) -> Dict[str, str]:
        """Load location name mappings for normalization."""
        return {
            "bangalore": "Bengaluru",
            "bengaluru": "Bengaluru",
            "blr": "Bengaluru",
            "mumbai": "Mumbai",
            "bombay": "Mumbai",
            "delhi": "Delhi",
            "new delhi": "Delhi",
            "ncr": "Delhi NCR",
            "gurugram": "Gurugram",
            "gurgaon": "Gurugram",
            "hyderabad": "Hyderabad",
            "chennai": "Chennai",
            "pune": "Pune",
            "kolkata": "Kolkata",
            "ahmedabad": "Ahmedabad",
            "remote": "Remote",
            "work from home": "Remote",
            "wfh": "Remote",
        }
    
    def _load_title_variations(self) -> Dict[str, str]:
        """Load job title variations for normalization."""
        return {
            "sr. software engineer": "Senior Software Engineer",
            "sr software engineer": "Senior Software Engineer",
            "senior software engineer": "Senior Software Engineer",
            "software engineer ii": "Senior Software Engineer",
            "software engineer 2": "Senior Software Engineer",
            "jr. software engineer": "Junior Software Engineer",
            "jr software engineer": "Junior Software Engineer",
            "software engineer i": "Junior Software Engineer",
            "software engineer 1": "Junior Software Engineer",
            "sde 1": "Software Development Engineer",
            "sde 2": "Senior Software Development Engineer",
            "sde 3": "Staff Software Development Engineer",
            "frontend developer": "Frontend Developer",
            "front-end developer": "Frontend Developer",
            "full stack developer": "Full Stack Developer",
            "fullstack developer": "Full Stack Developer",
            "backend developer": "Backend Developer",
            "back-end developer": "Backend Developer",
            "data scientist": "Data Scientist",
            "ml engineer": "Machine Learning Engineer",
            "machine learning engineer": "Machine Learning Engineer",
            "devops engineer": "DevOps Engineer",
            "qa engineer": "QA Engineer",
            "quality assurance engineer": "QA Engineer",
            "product manager": "Product Manager",
            "pm": "Product Manager",
        }
    
    def _experience_to_min_max(self, experience_level: Optional[str]) -> tuple[Optional[int], Optional[int]]:
        """Convert experience level string to min/max years."""
        level_map = {
            "entry": (0, 2),
            "mid": (3, 5),
            "senior": (5, 8),
            "lead": (7, 10),
            "principal": (10, 15),
        }
        if not experience_level:
            return (None, None)
        return level_map.get(experience_level.lower(), (None, None))

    def normalize_job(self, job: JobPosting) -> NormalizedJob:
        """Normalize a job posting to standard format."""
        experience_level = self.normalize_experience(job.experience_level, job.description)
        experience_min, experience_max = self._experience_to_min_max(experience_level)
        return NormalizedJob(
            title=self.normalize_title(job.title),
            company=self.normalize_company(job.company),
            location=self.normalize_location(job.location),
            salary=job.salary,
            salary_min=self.extract_salary_min(job.salary),
            salary_max=self.extract_salary_max(job.salary),
            description=job.description,
            url=job.url,
            source=job.source,
            external_id=job.external_id,
            is_remote=job.is_remote or self._is_remote_location(job.location),
            experience_level=experience_level,
            experience_min=experience_min,
            experience_max=experience_max,
            skills=self.extract_skills(job.description),
            posted_date=job.posted_date,
        )
    
    def normalize_title(self, title: str) -> str:
        """Normalize job title to standard format."""
        if not title:
            return "Unknown"
        
        # Clean and standardize
        cleaned = title.strip().lower()
        
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^(urgent|hiring|looking for)\s*', '', cleaned)
        cleaned = re.sub(r'\s*(needed|required|wanted)$', '', cleaned)
        
        # Check for known variations
        if cleaned in self.title_variations:
            return self.title_variations[cleaned]
        
        # Title case the result
        return title.strip().title()
    
    def normalize_company(self, company: str) -> str:
        """Normalize company name to standard format."""
        if not company:
            return "Unknown"
        
        # Clean and lowercase for matching
        cleaned = company.strip().lower()
        
        # Remove common suffixes
        cleaned = re.sub(r'\s+(pvt\.?|ltd\.?|llc|inc\.?|corp\.?|limited|private)\s*$', '', cleaned)
        cleaned = cleaned.strip()
        
        # Check for known aliases
        if cleaned in self.company_aliases:
            return self.company_aliases[cleaned]
        
        # Title case the result
        return company.strip().title()
    
    def normalize_location(self, location: Optional[str]) -> Optional[str]:
        """Normalize location to standard format."""
        if not location:
            return None
        
        # Clean and lowercase for matching
        cleaned = location.strip().lower()
        
        # Check for known mappings
        if cleaned in self.location_mappings:
            return self.location_mappings[cleaned]
        
        # Handle multiple locations (take first one)
        if ',' in cleaned:
            cleaned = cleaned.split(',')[0].strip()
        
        # Title case the result
        return location.strip().title()
    
    def normalize_experience(self, experience: Optional[str], description: Optional[str] = None) -> Optional[str]:
        """Normalize experience level to standard values."""
        valid_levels = ["entry", "mid", "senior", "lead", "principal"]
        
        # Check provided experience level
        if experience:
            exp_lower = experience.lower()
            if exp_lower in valid_levels:
                return exp_lower
            
            # Map common variations
            exp_mapping = {
                "fresher": "entry",
                "entry level": "entry",
                "junior": "entry",
                "0-1 years": "entry",
                "0-2 years": "entry",
                "1-3 years": "entry",
                "mid level": "mid",
                "middle": "mid",
                "intermediate": "mid",
                "3-5 years": "mid",
                "2-5 years": "mid",
                "5-7 years": "senior",
                "senior level": "senior",
                "7+ years": "senior",
                "8+ years": "lead",
                "10+ years": "principal",
            }
            
            if exp_lower in exp_mapping:
                return exp_mapping[exp_lower]
        
        # Try to extract from description
        if description:
            desc_lower = description.lower()
            
            # Look for experience keywords
            if "fresher" in desc_lower or "entry level" in desc_lower or "0-1 year" in desc_lower:
                return "entry"
            elif "3-5 year" in desc_lower or "2-5 year" in desc_lower:
                return "mid"
            elif "5-7 year" in desc_lower or "senior" in desc_lower:
                return "senior"
            elif "7+ year" in desc_lower or "8+ year" in desc_lower:
                return "lead"
            elif "10+ year" in desc_lower:
                return "principal"
        
        return None
    
    def extract_salary_min(self, salary: Optional[str]) -> Optional[int]:
        """Extract minimum salary from salary string."""
        if not salary:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[₹$£€,\s]', '', salary.lower())
            
            # Handle annual/monthly/hourly
            is_annual = 'year' in salary.lower() or 'annual' in salary.lower() or 'pa' in salary.lower()
            is_monthly = 'month' in salary.lower() or 'monthly' in salary.lower() or 'pm' in salary.lower()
            is_hourly = 'hour' in salary.lower() or 'hourly' in salary.lower() or 'ph' in salary.lower()
            
            # Extract numbers
            numbers = re.findall(r'\d+', cleaned)
            if not numbers:
                return None
            
            # Get minimum (first number)
            min_salary = int(numbers[0])
            
            # Normalize to annual (assuming INR)
            if is_monthly:
                min_salary *= 12
            elif is_hourly:
                min_salary *= 2080  # 40 hours * 52 weeks
            
            return min_salary
        except (ValueError, IndexError):
            return None
    
    def extract_salary_max(self, salary: Optional[str]) -> Optional[int]:
        """Extract maximum salary from salary string."""
        if not salary:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[₹$£€,\s]', '', salary.lower())
            
            # Handle annual/monthly/hourly
            is_annual = 'year' in salary.lower() or 'annual' in salary.lower() or 'pa' in salary.lower()
            is_monthly = 'month' in salary.lower() or 'monthly' in salary.lower() or 'pm' in salary.lower()
            is_hourly = 'hour' in salary.lower() or 'hourly' in salary.lower() or 'ph' in salary.lower()
            
            # Extract numbers
            numbers = re.findall(r'\d+', cleaned)
            if not numbers:
                return None
            
            # Get maximum (last number if multiple, or first if single)
            max_salary = int(numbers[-1]) if len(numbers) > 1 else int(numbers[0])
            
            # Normalize to annual (assuming INR)
            if is_monthly:
                max_salary *= 12
            elif is_hourly:
                max_salary *= 2080  # 40 hours * 52 weeks
            
            return max_salary
        except (ValueError, IndexError):
            return None
    
    def extract_skills(self, description: Optional[str]) -> List[str]:
        """Extract skills from job description using skill extractor service."""
        if not description:
            return []
        
        try:
            # Use the existing skill extractor service
            skills = extract_job_skills(description)
            return list(skills)
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return []
    
    def _is_remote_location(self, location: Optional[str]) -> bool:
        """Check if location indicates remote work."""
        if not location:
            return False
        
        remote_keywords = ['remote', 'wfh', 'work from home', 'anywhere', 'virtual']
        location_lower = location.lower()
        
        return any(keyword in location_lower for keyword in remote_keywords)
    
    def batch_normalize(self, jobs: List[JobPosting]) -> List[NormalizedJob]:
        """Normalize a batch of job postings."""
        return [self.normalize_job(job) for job in jobs]
