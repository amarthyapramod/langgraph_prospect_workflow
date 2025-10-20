"""
Outreach Content Agent - Generates personalized outreach messages
"""
from typing import Dict, Any, List
import logging
from agents.base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class OutreachContentAgent(BaseAgent):
    """Agent for generating personalized outreach content"""
    
    def __init__(self, llm):
        super().__init__("OutreachContentAgent", llm)
    
    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """Generate personalized outreach messages"""
        
        ranked_leads = inputs.get('ranked_leads', [])
        persona = inputs.get('persona', 'SDR')
        tone = inputs.get('tone', 'friendly')
        
        # Only generate for top leads (grade A and B)
        top_leads = [l for l in ranked_leads if l.get('grade') in ['A', 'B']]
        
        logger.info(f"Generating outreach for {len(top_leads)} top leads")
        
        messages = []
        for lead in top_leads[:20]:  # Limit to top 20
            message = self._generate_message(lead, persona, tone)
            messages.append({
                'lead': lead.get('contact_name', 'Unknown'),
                'email': lead.get('email', ''),
                'company': lead.get('company', ''),
                'subject': message['subject'],
                'email_body': message['body'],
                'score': lead.get('score', 0),
                'grade': lead.get('grade', 'N/A')
            })
        
        logger.info(f"Generated {len(messages)} personalized messages")
        
        return {
            'messages': messages,
            'count': len(messages),
            'reasoning': reasoning
        }
    
    def _generate_message(self, lead: Dict, persona: str, tone: str) -> Dict:
        """Generate a personalized message for a lead"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert {persona} writing personalized outreach emails.
Write in a {tone} tone. Keep emails concise (3-4 sentences max).
Focus on the prospect's pain points and how we can help."""),
            ("user", """Write a personalized email for:
Contact: {contact_name}
Title: {title}
Company: {company}
Signal: {signal}
Technologies: {technologies}

Our company: Axxxxxxx.ai - AI-powered analytics for B2B revenue teams.
Goal: Book a 15-minute discovery call.

Return JSON with 'subject' and 'body' fields.""")
        ])
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(
                    persona=persona,
                    tone=tone,
                    contact_name=lead.get('contact_name', 'there'),
                    title=lead.get('title', 'sales leader'),
                    company=lead.get('company', 'your company'),
                    signal=lead.get('signal', 'interest in analytics'),
                    technologies=', '.join(lead.get('technologies', []))
                )
            )
            
            import json
            content = response.content
            # Try to extract JSON from response
            if '{' in content and '}' in content:
                start = content.index('{')
                end = content.rindex('}') + 1
                message_data = json.loads(content[start:end])
                return message_data
            
        except Exception as e:
            logger.warning(f"Error generating message with LLM: {e}")
        
        # Fallback template
        return {
            'subject': f"Quick question about {lead.get('company', 'your company')}'s analytics",
            'body': f"""Hi {lead.get('contact_name', 'there')},

I noticed {lead.get('company', 'your company')} is {lead.get('signal', 'growing fast')}. Many {lead.get('title', 'sales leaders')} we work with struggle to get actionable insights from their data.

Axxxxxxx.ai helps B2B teams like yours turn raw data into revenue-driving decisions. Would you be open to a quick 15-min call to explore if we can help?

Best regards"""
        }
