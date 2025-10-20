"""
LangGraph Builder - Dynamically constructs and executes agent workflows from JSON config
"""
import json
import os
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):
    """State object that gets passed between nodes"""
    workflow_name: str
    current_step: str
    data: Dict[str, Any]
    errors: List[str]
    history: List[Dict[str, Any]]

class LangGraphBuilder:
    """Builds and executes LangGraph workflows from JSON configuration"""
    
    def __init__(self, workflow_path: str = "workflow.json"):
        self.workflow_path = workflow_path
        self.workflow_config = None
        self.graph = None
        self.agents = {}
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
)
        
    def load_workflow(self) -> Dict:
        """Load and validate workflow JSON"""
        try:
            with open(self.workflow_path, 'r') as f:
                self.workflow_config = json.load(f)
            logger.info(f"Loaded workflow: {self.workflow_config.get('workflow_name')}")
            self._validate_workflow()
            return self.workflow_config
        except FileNotFoundError:
            logger.error(f"Workflow file not found: {self.workflow_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in workflow file: {e}")
            raise
    
    def _validate_workflow(self):
        """Validate workflow structure"""
        required_keys = ['workflow_name', 'steps']
        for key in required_keys:
            if key not in self.workflow_config:
                raise ValueError(f"Missing required key in workflow: {key}")
        
        if not self.workflow_config['steps']:
            raise ValueError("Workflow must have at least one step")
        
        logger.info("Workflow validation passed")
    
    def _resolve_env_variables(self, config: Dict) -> Dict:
        """Replace {{ENV_VAR}} placeholders with actual values"""
        config_str = json.dumps(config)
        
        # Find all {{VAR}} patterns and replace
        import re
        pattern = r'\{\{([A-Z_]+)\}\}'
        matches = re.findall(pattern, config_str)
        
        for var in matches:
            env_value = os.getenv(var, f"MISSING_{var}")
            config_str = config_str.replace(f"{{{{{var}}}}}", env_value)
        
        return json.loads(config_str)
    
    def _load_agent(self, agent_name: str):
        """Dynamically import agent class"""
        try:
            module_path = f"agents.{agent_name.lower()}"
            #dynamic import - from agents import xxxagent as module
            module = __import__(module_path, fromlist=[agent_name])
            #from agents.xxxagent import xxxAgent
            agent_class = getattr(module, agent_name)
            return agent_class(llm=self.llm)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load agent {agent_name}: {e}")
            # Return a generic agent wrapper
            from agents.base_agent import BaseAgent
            return BaseAgent(agent_name, self.llm)
    
    def _resolve_inputs(self, inputs: Dict, state: WorkflowState) -> Dict:
        """Resolve input references like {{step.output.field}}"""
        resolved = {}
        
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Extract reference path
                ref_path = value[2:-2].strip()
                parts = ref_path.split('.')
                # Check if it's a config reference
                if parts[0] == 'config':
                    # Look in workflow_config instead of state
                    current = self.workflow_config
                    try:
                        for part in parts:
                            current = current[part]
                        resolved[key] = current
                    except (KeyError, TypeError):
                        logger.warning(f"Could not resolve config reference: {ref_path}")
                        resolved[key] = None
                else:
                    # Navigate through state data
                    current = state['data']
                    try:
                        for part in parts:
                            current = current[part]
                        resolved[key] = current
                    except (KeyError, TypeError):
                        logger.warning(f"Could not resolve reference: {ref_path}")
                        resolved[key] = None
                """# Navigate through state data
                current = state['data']
                try:
                    for part in parts:
                        current = current[part]
                    resolved[key] = current
                except (KeyError, TypeError):
                    logger.warning(f"Could not resolve reference: {ref_path}")
                    resolved[key] = None"""
            else:
                resolved[key] = value
        
        return resolved
    
    def _create_node_function(self, step_config: Dict):
        """Create a node function for a workflow step"""
        
        def node_function(state: WorkflowState) -> WorkflowState:
            step_id = step_config['id']
            agent_name = step_config['agent']
            
            logger.info(f"Executing node: {step_id} ({agent_name})")
            
            # Load agent if not already loaded
            if agent_name not in self.agents:
                self.agents[agent_name] = self._load_agent(agent_name)
            
            agent = self.agents[agent_name]
            
            # Resolve input references
            inputs = self._resolve_inputs(step_config.get('inputs', {}), state)
            
            # Resolve tool configurations
            tools_config = self._resolve_env_variables({'tools': step_config.get('tools', [])})
            
            # Execute agent
            try:
                result = agent.execute(
                    inputs=inputs,
                    instructions=step_config.get('instructions', ''),
                    tools=tools_config['tools']
                )
                
                # Update state
                state['data'][step_id] = {'output': result}
                state['current_step'] = step_id
                state['history'].append({
                    'step': step_id,
                    'agent': agent_name,
                    'inputs': inputs,
                    'output': result
                })
                
                logger.info(f"Node {step_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Error in node {step_id}: {e}")
                state['errors'].append(f"{step_id}: {str(e)}")
            
            return state
        
        return node_function
    
    def build_graph(self) -> StateGraph:
        """Build LangGraph from workflow configuration"""
        if not self.workflow_config:
            self.load_workflow()
        
        # Create graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        steps = self.workflow_config['steps']
        for step in steps:
            node_func = self._create_node_function(step)
            workflow.add_node(step['id'], node_func)
        
        # Add edges (sequential flow)
        for i in range(len(steps) - 1):
            workflow.add_edge(steps[i]['id'], steps[i+1]['id'])
        
        # Set entry point
        workflow.set_entry_point(steps[0]['id'])
        
        # Set finish point
        workflow.add_edge(steps[-1]['id'], END)
        
        # Compile graph
        self.graph = workflow.compile()
        logger.info("LangGraph built successfully")
        
        return self.graph
    
    def execute(self, initial_data: Dict = None) -> Dict:
        """Execute the workflow"""
        if not self.graph:
            self.build_graph()
        
        # Initialize state
        initial_state: WorkflowState = {
            'workflow_name': self.workflow_config['workflow_name'],
            'current_step': '',
            'data': initial_data or {},
            'errors': [],
            'history': []
        }
        
        logger.info(f"Starting workflow execution: {self.workflow_config['workflow_name']}")
        
        # Run graph
        final_state = self.graph.invoke(initial_state)
        
        logger.info("Workflow execution completed")
        
        # Return results
        return {
            'success': len(final_state['errors']) == 0,
            'data': final_state['data'],
            'errors': final_state['errors'],
            'history': final_state['history']
        }

def main():
    """Main execution function"""
    # Initialize builder
    builder = LangGraphBuilder("workflow.json")
    
    # Load and build workflow
    builder.load_workflow()
    builder.build_graph()
    
    # Execute workflow
    result = builder.execute()
    
    # Print results
    print("\n" + "="*50)
    print("WORKFLOW EXECUTION RESULTS")
    print("="*50)
    print(f"Success: {result['success']}")
    print(f"Steps executed: {len(result['history'])}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Save results
    with open('workflow_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\nResults saved to workflow_results.json")

if __name__ == "__main__":
    main()