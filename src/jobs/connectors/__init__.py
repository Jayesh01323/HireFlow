"""
Job Connectors Package

Provides connectors for various job platforms.
Each connector implements the BaseJobConnector interface.

Note: Wellfound now uses ApifyConnector with source="wellfound" for reliable data extraction.
The legacy WellfoundConnector (browser-based) is deprecated due to DataDome CAPTCHA protection.
"""

from src.jobs.connectors.apify import ApifyConnector
from src.jobs.connectors.base import BaseJobConnector
from src.jobs.connectors.cutshort import CutshortConnector
from src.jobs.connectors.foundit import FounditConnector
from src.jobs.connectors.glassdoor import GlassdoorConnector
from src.jobs.connectors.indeed import IndeedConnector
from src.jobs.connectors.internshala import InternshalaConnector
from src.jobs.connectors.linkedin import LinkedInConnector
from src.jobs.connectors.naukri import NaukriConnector
from src.jobs.connectors.unstop import UnstopConnector

__all__ = [
    "ApifyConnector",
    "BaseJobConnector",
    "CutshortConnector",
    "FounditConnector",
    "GlassdoorConnector",
    "IndeedConnector",
    "InternshalaConnector",
    "LinkedInConnector",
    "NaukriConnector",
    "UnstopConnector",
]