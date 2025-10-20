"""
Agents package for LangGraph Prospect-to-Lead Workflow

This package contains all specialized agents that make up the workflow:
- ProspectSearchAgent: Discovers prospects using Clay and Apollo APIs
- DataEnrichmentAgent: Enriches leads with Clearbit and other sources
- ScoringAgent: Scores and ranks leads based on ICP fit
- OutreachContentAgent: Generates personalized email content
- OutreachExecutorAgent: Sends emails and tracks delivery
- ResponseTrackerAgent: Monitors campaign engagement metrics
- FeedbackTrainerAgent: Analyzes performance and suggests improvements
"""

from agents.base_agent import BaseAgent
from agents.prospectsearchagent import ProspectSearchAgent
from agents.dataenrichmentagent import DataEnrichmentAgent
from agents.scoringagent import ScoringAgent
from agents.outreachcontentagent import OutreachContentAgent
from agents.outreachexecutoragent import OutreachExecutorAgent
from agents.responsetrackeragent import ResponseTrackerAgent
from agents.feedbacktraineragent import FeedbackTrainerAgent

__all__ = [
    'BaseAgent',
    'ProspectSearchAgent',
    'DataEnrichmentAgent',
    'ScoringAgent',
    'OutreachContentAgent',
    'OutreachExecutorAgent',
    'ResponseTrackerAgent',
    'FeedbackTrainerAgent'
]

__version__ = '1.0.0'