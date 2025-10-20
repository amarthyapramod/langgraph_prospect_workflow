"""
Outreach Executor Agent - Sends emails and tracks delivery
"""
from typing import Dict, Any, List
import logging
import time
from agents.base_agent import BaseAgent
import requests

logger = logging.getLogger(__name__)

class OutreachExecutorAgent(BaseAgent):
    """Agent for executing outreach campaigns"""
    
    def __init__(self, llm):
        super().__init__("OutreachExecutorAgent", llm)
        # Load API key from environment variable
    
    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """Send outreach emails"""
        
        messages = inputs.get('messages', [])
        logger.info(f"Executing outreach for {len(messages)} messages")
        
        apollo_tool = next((t for t in tools if t['name'] == 'ApolloAPI'), None)
        
        sent_status = []
        campaign_id = f"campaign_{int(time.time())}"
        
        for message in messages:
            #status=self._send_email_apollo(message,apollo_tool,campaign_id)
            status = self._send_email(message, apollo_tool, campaign_id)
            sent_status.append(status)
        
        success_count = sum(1 for s in sent_status if s['status'] == 'sent')
        
        logger.info(f"Sent {success_count}/{len(messages)} emails successfully")
        
        return {
            'sent_status': sent_status,
            'campaign_id': campaign_id,
            'success_count': success_count,
            'total': len(messages),
            'reasoning': reasoning
        }
    
    def _send_email(self, message: Dict, apollo_tool: Dict = None, campaign_id: str = None) -> Dict:
        """Send a single email"""
        
        # In production, this would call SendGrid or Apollo API
        # For now, we'll simulate sending
        
        logger.info(f"Sending email to {message.get('email', 'unknown')}")


        # Simulate API call delay
        import random
        time.sleep(0.1)
        
        # Simulate 95% success rate
        success = random.random() < 0.95
        
        return {
            'email': message.get('email', ''),
            'contact_name': message.get('lead', ''),
            'company': message.get('company', ''),
            'status': 'sent' if success else 'failed',
            'campaign_id': campaign_id,
            'sent_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'error': None if success else 'Simulated failure'
        }

    # to send emails, comment out the simulation code above
    def _send_email_apollo(self, message: Dict, apollo_tool: Dict, campaign_id: str) -> Dict:
        """Send a single email using Apollo API"""
        email = message.get('email', '')
        contact_name = message.get('lead', '')
        company = message.get('company', '')
        success = False
        error_message = None
        
        try:
            if not apollo_tool:
                raise ValueError("Apollo tool not provided")
            
            api_key = apollo_tool['config'].get('api_key')
            if not api_key or api_key.startswith('MISSING'):
                raise ValueError("Missing Apollo API key")
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "email_subject": message.get('subject', 'Hello from Axxxxxxx.ai'),
                "email_body": message.get('email_body', ''),
                "to_email": email,
                "from_email": "you@yourdomain.com",  # must be verified in Apollo
                "campaign_id": campaign_id
            }
            
            response = requests.post(
                "https://api.apollo.io/v1/emails",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                success = True
            else:
                error_message = f"Apollo returned {response.status_code}: {response.text}"
        
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error sending email to {email}: {e}")
        
        return {
            'email': email,
            'contact_name': contact_name,
            'company': company,
            'status': 'sent' if success else 'failed',
            'campaign_id': campaign_id,
            'sent_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'error': None if success else error_message
        }
