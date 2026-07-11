"""
Job Actors Package

Provides reusable, self-contained job data acquisition actors.
Each actor encapsulates the complete logic for extracting jobs from a single source.
Actors are designed to be independently removable without affecting the rest of HireFlow.

Architecture:
    BaseJobActor (abstract) → WellfoundActor, FutureActor, etc.
    Actor → Connector (minimal integration layer) → Normalizer → Deduplicator → Ranking → DB → UI
"""

from src.jobs.actors.base_actor import BaseJobActor
from src.jobs.actors.wellfound_actor import WellfoundActor

__all__ = [
    "BaseJobActor",
    "WellfoundActor",
]