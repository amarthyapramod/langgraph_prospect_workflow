"""
Data Enrichment Agent - Enriches prospect data using builtwith and other APIs
"""
from typing import Dict, Any, List
import requests
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DataEnrichmentAgent(BaseAgent):
    """Agent for enriching prospect data with additional information"""
    
    def __init__(self, llm):
        super().__init__("DataEnrichmentAgent", llm)
    
    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """Enrich lead data using external APIs"""
        
        leads = inputs.get('leads', [])
        logger.info(f"Enriching {len(leads)} leads")
        
        enriched_leads = []
        
        #builtwith_tool = next((t for t in tools if t['name'] == 'BuiltWith'), None)
        builtwith_tool = next((t for t in tools if t['name'] == 'BuiltWithTool'), None)
        
        for lead in leads:
            enriched_lead = self._enrich_lead(lead, builtwith_tool)
            enriched_leads.append(enriched_lead)
        
        logger.info(f"Enriched {len(enriched_leads)} leads")
        
        return {
            'enriched_leads': enriched_leads,
            'count': len(enriched_leads),
            'reasoning': reasoning
        }
    
    def _enrich_lead(self, lead: Dict, builtwith_tool: Dict = None) -> Dict:
        """Enrich a single lead with additional data"""
        
        enriched = lead.copy()
        
        # Mock enrichment data
        enriched.update({
            'role': lead.get('title', 'Unknown'),
            'seniority': self._determine_seniority(lead.get('title', '')),
            'department': 'Sales',
            'technologies': ['Salesforce', 'HubSpot', 'Outreach'],
            'company_size': '100-500',
            'company_industry': 'SaaS',
            'funding_stage': 'Series B',
            'enrichment_confidence': 0.85
        })
        
        # If builtwith API is configured, call it
        if builtwith_tool and 'api_key' in builtwith_tool.get('config', {}):
            api_key = builtwith_tool['config']['api_key']
            if not api_key.startswith('MISSING'):
                builtwith_data = self._call_builtwith(lead.get('company', ''), api_key)
                if builtwith_data:
                    enriched.update(builtwith_data)
        
        return enriched
    
    def _determine_seniority(self, title: str) -> str:
        """Determine seniority level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['vp', 'chief', 'head', 'director']):
            return 'Executive'
        elif any(word in title_lower for word in ['manager', 'lead']):
            return 'Manager'
        else:
            return 'Individual Contributor'
        
    def _call_builtwith(self, company_domain: str, api_key: str) -> Dict:
        """Call BuiltWith API for tech stack data"""
        if not company_domain or '.' not in company_domain:
            logger.warning(f"Invalid domain provided for BuiltWith: {company_domain}")
            return {}
        try:
            #import builtwith
            
            # Get domain from company name (simplified)
            #domain = f"https://{company_domain.lower().replace(' ', '')}.com"
            # Call BuiltWith
            #tech_data = builtwith.parse(domain)

            # Official BuiltWith Free API Endpoint format
            url = f"https://api.builtwith.com/free1/api.json?KEY={api_key}&LOOKUP={company_domain}"
            response = requests.get(url, timeout=10)
            
            if response.status_code!=200:
                logger.warning(f"BuiltWith API failed with status code {response.status_code}")
                return {}
            
            data=response.json()
            # Check for API error in response structure
            if data.get('Errors'):
                logger.error(f"BuiltWith API Error: {data['Errors']}")
                return {}
            
            # Extract technologies
            technologies = []
            # Iterate through Results -> groups to collect all tech names
            for result in data.get('groups', []):
                technologies.append(result.get('name', ""))
            
            return {
                'technologies': list(set(technologies)),
                'builtwith_enriched': True
            }
        except Exception as e:
            logger.warning(f"BuiltWith API connection error: {e}")
            return {}
