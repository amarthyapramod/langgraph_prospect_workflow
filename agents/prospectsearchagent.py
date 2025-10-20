"""
Prospect Search Agent - Searches for prospects using Clay and Apollo APIs
"""
from typing import Dict, Any, List
import requests
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ProspectSearchAgent(BaseAgent):
    """Agent for discovering B2B prospects using external APIs"""
    
    def __init__(self, llm):
        super().__init__("ProspectSearchAgent", llm)
    
    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """Search for prospects using Clay and Apollo APIs"""
        
        icp = inputs.get('icp', {})
        signals = inputs.get('signals', [])
        
        logger.info(f"Searching for prospects with ICP: {icp}")
        
        leads = []
        
        # Search using Apollo API
        apollo_tool = next((t for t in tools if t['name'] == 'ApolloAPI'), None)
        if apollo_tool:
            apollo_leads = self._search_apollo(icp, signals, apollo_tool['config'])
            leads.extend(apollo_leads)
        
        # Search using Clay API
        clay_tool = next((t for t in tools if t['name'] == 'ClayAPI'), None)
        if clay_tool:
            clay_leads = self._search_clay(icp, signals, clay_tool['config'])
            leads.extend(clay_leads)
        
        # Deduplicate leads
        unique_leads = self._deduplicate_leads(leads)
        
        logger.info(f"Found {len(unique_leads)} unique prospects")
        
        return {
            'leads': unique_leads,
            'count': len(unique_leads),
            'sources': ['Apollo', 'Clay'],
            'reasoning': reasoning
        }
    
    def _search_apollo(self, icp: Dict, signals: List[str], config: Dict) -> List[Dict]:
        """Search Apollo API for prospects"""
        api_key = config.get('api_key', '')
        endpoint = config.get('endpoint', '')
        
        if not api_key or api_key.startswith('MISSING'):
            logger.warning("Apollo API key not configured, returning mock data")
            return self._generate_mock_leads('Apollo', icp, 5)
        
        try:
            headers = {'Content-Type': 'application/json','Cache-Control': 'no-cache','x-api-key': api_key}
            """headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
                }"""
            #headers={}
            # Build search query
            search_data = {
                'person_titles': ['VP Sales', 'Head of Sales', 'Chief Revenue Officer', 'Sales Director'],
                'organization_num_employees_ranges': [
                    f"{icp.get('employee_count', {}).get('min', 100)},{icp.get('employee_count', {}).get('max', 1000)}"
                ],
                'organization_locations': [icp.get('location', 'USA')],
                'per_page': 25
            }
            #per_page=1 for test
            response = requests.post(endpoint, json=search_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                leads = []
                
                for person in data.get('people', []):
                    leads.append({
                        'company': person.get('organization', {}).get('name', ''),
                        'contact_name': person.get('name', ''),
                        'email': person.get('email', ''),
                        'linkedin': person.get('linkedin_url', ''),
                        'title': person.get('title', ''),
                        'signal': signals[0] if signals else 'general',
                        'source': 'Apollo'
                    })
                
                return leads
            else:
                logger.warning(f"Apollo API returned status {response.status_code}")
                return self._generate_mock_leads('Apollo', icp, 5)
            #return self._generate_mock_leads('Apollo', icp, 5)             
        except Exception as e:
            logger.error(f"Error calling Apollo API: {e}")
            return self._generate_mock_leads('Apollo', icp, 5)
    
    def _search_clay(self, icp: Dict, signals: List[str], config: Dict) -> List[Dict]:
        """Search Clay API for prospects"""
        api_key = config.get('api_key', '')
        endpoint = config.get('endpoint', '')
        
        if not api_key or api_key.startswith('MISSING'):
            logger.warning("Clay API key not configured, returning mock data")
            return self._generate_mock_leads('Clay', icp, 5)
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Build Clay search query
            search_params = {
                'filters': {
                    'industry': icp.get('industry', 'SaaS'),
                    'location': icp.get('location', 'USA'),
                    'revenue_min': icp.get('revenue', {}).get('min', 20000000),
                    'revenue_max': icp.get('revenue', {}).get('max', 200000000)
                },
                'limit': 35
            }
            #limit=1 for test
            response = requests.post(endpoint, json=search_params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                leads = []
                
                for company in data.get('results', []):
                    leads.append({
                        'company': company.get('name', ''),
                        'contact_name': company.get('primary_contact', {}).get('name', 'Unknown'),
                        'email': company.get('primary_contact', {}).get('email', ''),
                        'linkedin': company.get('linkedin_url', ''),
                        'title': company.get('primary_contact', {}).get('title', ''),
                        'signal': signals[0] if signals else 'general',
                        'source': 'Clay'
                    })
                
                return leads
            else:
                logger.warning(f"Clay API returned status {response.status_code}")
                return self._generate_mock_leads('Clay', icp, 5)
                
        except Exception as e:
            logger.error(f"Error calling Clay API: {e}")
            return self._generate_mock_leads('Clay', icp, 5)
    
    def _generate_mock_leads(self, source: str, icp: Dict, count: int) -> List[Dict]:
        """Generate mock lead data for testing"""
        companies = [
            'TechCorp Solutions', 'DataDrive Inc', 'CloudScale Systems',
            'Innovation Labs', 'Digital Ventures', 'SmartOps Co',
            'FutureStack Inc', 'AgileWorks', 'NexGen Software', 'Quantum Analytics'
        ]
        
        titles = ['VP of Sales', 'Head of Revenue', 'Chief Revenue Officer', 
                  'Sales Director', 'VP Marketing']
        
        signals_map = {
            'recent_funding': 'Recent $10M Series B',
            'hiring_for_sales': 'Hiring 5+ sales roles',
            'tech_stack_change': 'Migrating to new CRM',
            'expansion': 'Opening new office'
        }
        
        mock_leads = []
        for i in range(count):
            company = companies[i % len(companies)]
            mock_leads.append({
                'company': company,
                'contact_name': f'John Doe {i+1}',
                'email': f'john.doe{i+1}@{company.lower().replace(" ", "")}.com',
                'linkedin': f'https://linkedin.com/in/johndoe{i+1}',
                'title': titles[i % len(titles)],
                'signal': signals_map.get(icp.get('signals', ['general'])[0] if 'signals' in icp else 'general', 'Active in target market'),
                'source': source
            })
        
        return mock_leads
    
    def _deduplicate_leads(self, leads: List[Dict]) -> List[Dict]:
        """Remove duplicate leads based on email"""
        seen_emails = set()
        unique_leads = []
        
        for lead in leads:
            email = lead.get('email', '').lower()
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_leads.append(lead)
        
        return unique_leads