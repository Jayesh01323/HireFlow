"""
Career Copilot Agent

AI-powered career assistant that provides personalized career guidance.
Uses Gemini AI to answer career questions with context from user data.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.ai.gemini_client import GeminiClient
from src.services.career_fit_engine import CareerFitEngine
from src.services.job_intelligence_service import JobIntelligenceService
from src.utils import get_env

logger = logging.getLogger(__name__)

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))


@dataclass
class ConversationContext:
    """Context data for career conversations."""
    
    resume: Optional[Dict[str, Any]]
    career_fit: Optional[Dict[str, Any]]
    saved_jobs: List[Dict[str, Any]]
    applications: List[Dict[str, Any]]
    skill_gaps: List[str]
    top_career_path: Optional[str]


class CareerCopilotAgent:
    """AI Career Copilot agent for personalized career guidance."""
    
    def __init__(self) -> None:
        """Initialize career copilot agent."""
        self.gemini_client = GeminiClient()
        self.career_fit_engine = CareerFitEngine()
        self.job_intelligence_service = JobIntelligenceService()
    
    def get_conversation_context(self, user_id: Optional[int] = None) -> ConversationContext:
        """
        Gather context data for career conversations.
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            ConversationContext with relevant data
        """
        # Get latest resume
        resume = self._get_latest_resume()
        
        # Get career fit analysis
        career_fit = None
        if resume:
            try:
                fit_analysis = self.career_fit_engine.analyze_career_fit(resume)
                career_fit = {
                    "top_career_path": fit_analysis.top_career_path,
                    "top_5_careers": fit_analysis.top_5_careers,
                    "overall_recommendations": fit_analysis.overall_recommendations,
                }
            except Exception as e:
                logger.error(f"Error getting career fit: {e}")
        
        # Get saved jobs
        saved_jobs = self._get_saved_jobs(user_id)
        
        # Get applications
        applications = self._get_applications(user_id)
        
        # Get skill gaps (from recent job matches)
        skill_gaps = self._get_common_skill_gaps()
        
        # Get top career path
        top_career_path = career_fit["top_career_path"] if career_fit else None
        
        return ConversationContext(
            resume=resume,
            career_fit=career_fit,
            saved_jobs=saved_jobs,
            applications=applications,
            skill_gaps=skill_gaps,
            top_career_path=top_career_path,
        )
    
    def ask_question(
        self,
        question: str,
        context: ConversationContext,
        user_id: Optional[int] = None,
    ) -> str:
        """
        Ask a career question and get AI-powered answer.
        
        Args:
            question: User's career question
            context: Conversation context
            user_id: User ID (optional)
            
        Returns:
            AI-generated answer
        """
        try:
            # Build context-aware prompt
            prompt = self._build_prompt(question, context)
            
            # Generate response using Gemini
            response = self.gemini_client.generate_response(prompt)
            
            # Save conversation to database
            self._save_conversation(user_id, question, response, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating career advice: {e}")
            return self._generate_fallback_response(question, context)
    
    def _build_prompt(
        self,
        question: str,
        context: ConversationContext,
    ) -> str:
        """Build context-aware prompt for Gemini."""
        prompt = "You are an AI Career Coach helping a job seeker with personalized career advice.\n\n"
        
        # Add resume context
        if context.resume:
            skills = context.resume.get("skills", [])
            skill_names = [s.get("name", s) if isinstance(s, dict) else s for s in skills]
            prompt += f"User's Skills: {', '.join(skill_names[:10])}\n"
            prompt += f"User's Projects: {len(context.resume.get('projects', []))} projects\n"
            prompt += f"User's Experience: {len(context.resume.get('experience', []))} entries\n\n"
        
        # Add career fit context
        if context.career_fit:
            prompt += f"Top Career Path: {context.career_fit['top_career_path']}\n"
            top_careers = context.career_fit.get('top_5_careers', [])[:3]
            if top_careers:
                prompt += "Top Career Matches:\n"
                for career, score in top_careers:
                    prompt += f"  - {career}: {score}% fit\n"
            prompt += "\n"
        
        # Add saved jobs context
        if context.saved_jobs:
            prompt += f"Saved Jobs: {len(context.saved_jobs)} jobs saved\n"
            if context.saved_jobs:
                prompt += f"Recent saved job: {context.saved_jobs[0].get('job_title', 'N/A')} at {context.saved_jobs[0].get('company', 'N/A')}\n"
            prompt += "\n"
        
        # Add applications context
        if context.applications:
            prompt += f"Applications: {len(context.applications)} applications submitted\n"
            prompt += "\n"
        
        # Add skill gaps context
        if context.skill_gaps:
            prompt += f"Common Missing Skills: {', '.join(context.skill_gaps[:5])}\n\n"
        
        # Add the question
        prompt += f"User Question: {question}\n\n"
        prompt += "Provide a helpful, personalized, and actionable answer. Be specific and practical. "
        prompt += "If the question requires data you don't have, acknowledge this and provide general guidance."
        
        return prompt
    
    def _get_latest_resume(self) -> Optional[Dict[str, Any]]:
        """Get latest resume from database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT parsed_json FROM resumes ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    return json.loads(row["parsed_json"])
        except Exception as e:
            logger.error(f"Error getting resume: {e}")
        return None
    
    def _get_saved_jobs(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get saved jobs from database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                query = "SELECT * FROM saved_jobs"
                params = []
                
                if user_id is not None:
                    query += " WHERE user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY saved_at DESC LIMIT 10"
                
                rows = conn.execute(query, params).fetchall()
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting saved jobs: {e}")
        return []
    
    def _get_applications(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get applications from database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                query = "SELECT * FROM applications"
                params = []
                
                if user_id is not None:
                    query += " WHERE user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY created_at DESC LIMIT 10"
                
                rows = conn.execute(query, params).fetchall()
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting applications: {e}")
        return []
    
    def _get_common_skill_gaps(self) -> List[str]:
        """Get common skill gaps from job matches."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT missing_skills FROM job_matches
                    WHERE missing_skills IS NOT NULL
                    ORDER BY created_at DESC
                    LIMIT 10
                """).fetchall()
                
                all_missing = []
                for row in rows:
                    try:
                        missing = json.loads(row["missing_skills"])
                        all_missing.extend(list(missing)[:5])
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Count frequency
                from collections import Counter
                counter = Counter(all_missing)
                
                return [skill for skill, _ in counter.most_common(10)]
        except Exception as e:
            logger.error(f"Error getting skill gaps: {e}")
        return []
    
    def _save_conversation(
        self,
        user_id: Optional[int],
        question: str,
        answer: str,
        context: ConversationContext,
    ) -> bool:
        """Save conversation to database."""
        try:
            # Ensure table exists
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS career_conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        context TEXT,
                        conversation_type TEXT,
                        created_at TEXT NOT NULL DEFAULT (datetime('now')),
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                    """
                )
                
                # Determine conversation type
                conv_type = self._classify_conversation_type(question)
                
                # Serialize context
                context_json = json.dumps({
                    "top_career_path": context.top_career_path,
                    "saved_jobs_count": len(context.saved_jobs),
                    "applications_count": len(context.applications),
                })
                
                # Insert conversation
                conn.execute(
                    """
                    INSERT INTO career_conversations (user_id, question, answer, context, conversation_type)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, question, answer, context_json, conv_type),
                )
                conn.commit()
                
                return True
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False
    
    def _classify_conversation_type(self, question: str) -> str:
        """Classify the type of career conversation."""
        question_lower = question.lower()
        
        if any(term in question_lower for term in ["job", "apply", "position", "role"]):
            return "job_advice"
        elif any(term in question_lower for term in ["skill", "learn", "gap", "improve"]):
            return "skill_gap"
        elif any(term in question_lower for term in ["career", "path", "track", "future"]):
            return "career_path"
        elif any(term in question_lower for term in ["resume", "cv", "profile"]):
            return "resume_advice"
        elif any(term in question_lower for term in ["interview", "prepare", "question"]):
            return "interview_prep"
        else:
            return "general"
    
    def _generate_fallback_response(
        self,
        question: str,
        context: ConversationContext,
    ) -> str:
        """Generate fallback response when AI fails."""
        fallback = "I apologize, but I'm unable to provide a specific answer right now. "
        
        if context.top_career_path:
            fallback += f"Based on your profile, your top career fit is {context.top_career_path}. "
        
        if context.skill_gaps:
            fallback += f"Consider focusing on learning: {', '.join(context.skill_gaps[:3])}. "
        
        fallback += "Please try rephrasing your question or check back later."
        
        return fallback
    
    def get_conversation_history(
        self,
        user_id: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a user."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                query = "SELECT * FROM career_conversations"
                params = []
                
                if user_id is not None:
                    query += " WHERE user_id = ?"
                    params.append(user_id)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                rows = conn.execute(query, params).fetchall()
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
        return []
    
    def get_suggested_questions(self, context: ConversationContext) -> List[str]:
        """Generate suggested questions based on context."""
        suggestions = []
        
        # General career questions
        suggestions.append("Which jobs should I apply to first?")
        suggestions.append("What should I learn next?")
        
        # Context-specific suggestions
        if context.top_career_path:
            suggestions.append(f"How can I become a better {context.top_career_path}?")
        
        if context.skill_gaps:
            suggestions.append(f"What's the best way to learn {context.skill_gaps[0]}?")
        
        if context.saved_jobs:
            suggestions.append("Which of my saved jobs should I prioritize?")
        
        if context.applications:
            suggestions.append("How can I improve my application success rate?")
        
        if context.resume:
            suggestions.append("How can I improve my resume?")
        
        return suggestions[:6]
