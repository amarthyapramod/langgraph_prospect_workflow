# agents/scoringagent.py
"""
Scoring Agent - Scores and ranks leads based on ICP criteria
"""
from typing import Dict, Any, List
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ScoringAgent(BaseAgent):
    """Agent for scoring and ranking leads"""
    
    def __init__(self, llm):
        super().__init__("ScoringAgent", llm)
    
    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """Score leads based on ICP criteria"""
        
        enriched_leads = inputs.get('enriched_leads', [])
        scoring_criteria = inputs.get('scoring_criteria', self._default_scoring_criteria())
        
        logger.info(f"Scoring {len(enriched_leads)} leads")
        
        scored_leads = []
        for lead in enriched_leads:
            score = self._calculate_score(lead, scoring_criteria)
            lead['score'] = score
            lead['grade'] = self._assign_grade(score)
            scored_leads.append(lead)
        
        # Rank leads by score
        ranked_leads = sorted(scored_leads, key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Ranked {len(ranked_leads)} leads")
        
        return {
            'ranked_leads': ranked_leads,
            'top_leads': ranked_leads[:10],
            'average_score': sum(l['score'] for l in ranked_leads) / len(ranked_leads) if ranked_leads else 0,
            'reasoning': reasoning
        }
    
    def _default_scoring_criteria(self) -> Dict:
        """Default scoring criteria"""
        return {
            'seniority_weight': 0.3,
            'company_size_weight': 0.2,
            'tech_stack_weight': 0.2,
            'signal_weight': 0.3,
            'preferred_seniority': ['Executive', 'Manager'],
            'preferred_company_sizes': ['100-500', '500-1000'],
            'preferred_technologies': ['Salesforce', 'HubSpot']
        }
    
    def _calculate_score(self, lead: Dict, criteria: Dict) -> float:
        """Calculate lead score based on criteria"""
        score = 0.0
        
        # Seniority score
        if lead.get('seniority') in criteria.get('preferred_seniority', []):
            score += criteria.get('seniority_weight', 0.3) * 100
        
        # Company size score
        if lead.get('company_size') in criteria.get('preferred_company_sizes', []):
            score += criteria.get('company_size_weight', 0.2) * 100
        
        # Tech stack score
        lead_tech = set(lead.get('technologies', []))
        preferred_tech = set(criteria.get('preferred_technologies', []))
        tech_overlap = len(lead_tech.intersection(preferred_tech))
        if tech_overlap > 0:
            score += criteria.get('tech_stack_weight', 0.2) * 100 * (tech_overlap / len(preferred_tech))
        
        # Signal score (always give some points for having a signal)
        if lead.get('signal'):
            score += criteria.get('signal_weight', 0.3) * 100
        
        return round(score, 2)
    
    def _assign_grade(self, score: float) -> str:
        """Assign letter grade based on score"""
        if score >= 80:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 40:
            return 'C'
        else:
            return 'D'