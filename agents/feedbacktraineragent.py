"""
Feedback Trainer Agent - Analyzes performance and suggests improvements
"""
from typing import Dict, Any, List
import logging
from agents.base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class FeedbackTrainerAgent(BaseAgent):
    """Agent for analyzing campaign performance and suggesting improvements"""
    
    def __init__(self, llm):
        super().__init__("FeedbackTrainerAgent", llm)
    
    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """Analyze responses and generate recommendations"""
        
        responses = inputs.get('responses', [])
        logger.info(f"Analyzing {len(responses)} responses for feedback")
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics(responses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, responses)
        
        # Write to Google Sheets if configured
        sheets_tool = next((t for t in tools if t['name'] == 'GoogleSheets'), None)
        if sheets_tool:
            self._write_to_sheets(recommendations, metrics, sheets_tool)
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        return {
            'recommendations': recommendations,
            'metrics': metrics,
            'status': 'awaiting_approval',
            'reasoning': reasoning
        }
    
    def _calculate_performance_metrics(self, responses: List[Dict]) -> Dict:
        """Calculate detailed performance metrics"""
        
        total = len(responses)
        if total == 0:
            return {}
        
        metrics = {
            'total_sent': total,
            'open_rate': sum(1 for r in responses if r.get('opened')) / total * 100,
            'click_rate': sum(1 for r in responses if r.get('clicked')) / total * 100,
            'reply_rate': sum(1 for r in responses if r.get('replied')) / total * 100,
            'meeting_rate': sum(1 for r in responses if r.get('meeting_booked')) / total * 100,
            'positive_sentiment': sum(1 for r in responses if r.get('sentiment') == 'positive')
        }
        
        return metrics
    def _generate_recommendations(self, metrics: Dict, responses: List[Dict]) -> List[Dict]:
        """Generate recommendations using LLM (Gemini)"""
        
        # Prepare a prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a B2B outreach expert analyzing campaign metrics.
Generate actionable recommendations to improve email performance.

Consider these weighted criteria when evaluating performance:
- Open Rate (weight 0.3): Are subject lines engaging enough?
- Click Rate (weight 0.25): Are CTAs clear and compelling?
- Reply Rate (weight 0.25): Is targeting and personalization sufficient?
- Meeting Rate (weight 0.2): Is follow-up strategy effective?

Prioritize recommendations based on these weights and suggest improvements
that will maximize overall campaign effectiveness."""),

            ("user", """Here are campaign metrics: {metrics}
        Here are sample responses: {responses}

        Return a JSON array of recommendations with:
        type, priority, current_performance, suggestion, expected_impact, status""")
        ])

        try:
            # Call Gemini LLM
            response = self.llm.invoke(prompt.format_messages(metrics=metrics, responses=responses[:10]))
            
            import json
            content = response.content
            
            # Parse JSON output
            if '{' in content and '}' in content:
                start = content.index('[')
                end = content.rindex(']') + 1
                recommendations = json.loads(content[start:end])
                return recommendations

        except Exception as e:
            logger.warning(f"LLM failed, falling back to rule-based: {e}")

        # Fallback: existing rule-based logic
        return self._generate_recommendations_hardcode(metrics, responses)

    def _generate_recommendations_hardcode(self, metrics: Dict, responses: List[Dict]) -> List[Dict]:
        """Generate improvement recommendations based on performance"""
        
        recommendations = []
        
        # Analyze open rate
        if metrics.get('open_rate', 0) < 25:
            recommendations.append({
                'type': 'subject_line',
                'priority': 'high',
                'current_performance': f"{metrics.get('open_rate', 0):.1f}%",
                'suggestion': 'Test more personalized subject lines with company-specific triggers',
                'expected_impact': '+10-15% open rate',
                'status': 'pending_approval'
            })
        
        # Analyze click rate
        if metrics.get('click_rate', 0) < 10:
            recommendations.append({
                'type': 'email_body',
                'priority': 'medium',
                'current_performance': f"{metrics.get('click_rate', 0):.1f}%",
                'suggestion': 'Add more compelling CTA and reduce email length to 2-3 sentences',
                'expected_impact': '+5-8% click rate',
                'status': 'pending_approval'
            })
        
        # Analyze reply rate
        if metrics.get('reply_rate', 0) < 5:
            recommendations.append({
                'type': 'targeting',
                'priority': 'high',
                'current_performance': f"{metrics.get('reply_rate', 0):.1f}%",
                'suggestion': 'Refine ICP to focus on companies with recent funding or expansion signals',
                'expected_impact': '+3-5% reply rate',
                'status': 'pending_approval'
            })
        
        # If performance is good, suggest scaling
        if metrics.get('meeting_rate', 0) > 2:
            recommendations.append({
                'type': 'scaling',
                'priority': 'medium',
                'current_performance': f"{metrics.get('meeting_rate', 0):.1f}%",
                'suggestion': 'Current approach is working well. Increase daily outreach volume by 50%',
                'expected_impact': '50% more meetings',
                'status': 'pending_approval'
            })
        
        return recommendations
    
    def _write_to_sheets(self, recommendations: List[Dict], metrics: Dict, sheets_tool: Dict):
        """Write recommendations to Google Sheets"""
        
        # In production, this would use Google Sheets API
        logger.info(f"Would write {len(recommendations)} recommendations to Google Sheets")
        logger.info(f"Metrics: {metrics}")
        
        # Mock implementation
        return True