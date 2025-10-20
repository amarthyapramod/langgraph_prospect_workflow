"""
Response Tracker Agent - Monitors email responses and engagement
"""
from typing import Dict, Any, List
import logging
import random
from agents.base_agent import BaseAgent
import requests
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ResponseTrackerAgent(BaseAgent):
    """Agent for tracking email responses and engagement"""
    
    def __init__(self, llm):
        super().__init__("ResponseTrackerAgent", llm)

    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """Track responses for a campaign"""
        
        campaign_id = inputs.get('campaign_id', '')
        logger.info(f"Tracking responses for campaign {campaign_id}")
        
        # In production, this would call Apollo API to get real metrics
        #responses= self._fetch_apollo_responses(campaign_id)

        # For demo, we'll generate realistic mock data
        
        responses = self._generate_mock_responses(campaign_id)
        
        logger.info(f"Tracked {len(responses)} responses")
        
        return {
            'responses': responses,
            'campaign_id': campaign_id,
            'metrics': self._calculate_metrics(responses),
            'reasoning': reasoning
        }
    
    def _generate_mock_responses(self, campaign_id: str) -> List[Dict]:
        """Generate mock response data"""
        
        # Simulate realistic email metrics
        num_sent = random.randint(15, 20)
        
        responses = []
        for i in range(num_sent):
            opened = random.random() < 0.35  # 35% open rate
            clicked = opened and random.random() < 0.15  # 15% click rate if opened
            replied = clicked and random.random() < 0.25  # 25% reply rate if clicked
            meeting_booked = replied and random.random() < 0.30  # 30% meeting rate if replied
            
            responses.append({
                'contact_id': f'contact_{i+1}',
                'campaign_id': campaign_id,
                'sent': True,
                'opened': opened,
                'clicked': clicked,
                'replied': replied,
                'meeting_booked': meeting_booked,
                'sentiment': 'positive' if replied else 'neutral'
            })
        
        return responses
    
    def _calculate_metrics(self, responses: List[Dict]) -> Dict:
        """Calculate campaign metrics"""
        
        total = len(responses)
        if total == 0:
            return {}
        
        opened = sum(1 for r in responses if r.get('opened'))
        clicked = sum(1 for r in responses if r.get('clicked'))
        replied = sum(1 for r in responses if r.get('replied'))
        meetings = sum(1 for r in responses if r.get('meeting_booked'))
        
        return {
            'total_sent': total,
            'open_rate': round(opened / total * 100, 2),
            'click_rate': round(clicked / total * 100, 2),
            'reply_rate': round(replied / total * 100, 2),
            'meeting_rate': round(meetings / total * 100, 2),
            'opened': opened,
            'clicked': clicked,
            'replied': replied,
            'meetings_booked': meetings
        }
    
    # Real Apollo integration
    def _fetch_apollo_responses(self, campaign_id: str) -> List[Dict]:
        """Fetch real response data from Apollo API for a campaign"""
        api_key = os.getenv("APOLLO_API_KEY")  # load from .env
        if not api_key:
            logger.warning("Apollo API key missing. Using mock data.")
            return self._generate_mock_responses(campaign_id)

        try:
            url = f"https://api.apollo.io/v1/email_activities?campaign_id={campaign_id}"
            headers = {"Authorization": f"Bearer {api_key}"}

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "data" not in data:
                logger.warning("Apollo API response missing 'data' key.")
                return self._generate_mock_responses(campaign_id)

            responses = []
            for item in data["data"]:
                responses.append({
                    "contact_id": item.get("contact_id", ""),
                    "campaign_id": campaign_id,
                    "sent": True,  # assume sent if activity exists
                    "opened": item.get("opened", False),
                    "clicked": item.get("clicked", False),
                    "replied": item.get("replied", False),
                    "meeting_booked": item.get("meeting_booked", False),
                    "sentiment": item.get("sentiment", "neutral")
                })

            return responses

        except Exception as e:
            logger.warning(f"Apollo API fetch failed: {e}")
            return self._generate_mock_responses(campaign_id)
