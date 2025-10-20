"""
Base Agent Class - Foundation for all specialized agents
"""
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import logging
import time

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all agents in the workflow"""
    
    def __init__(self, agent_name: str, llm: ChatGoogleGenerativeAI):
        self.agent_name = agent_name
        self.llm = llm
        self.reasoning_history = []
    
    def execute(self, inputs: Dict[str, Any], instructions: str, tools: List[Dict]) -> Dict[str, Any]:
        """
        Execute agent task using ReAct (Reasoning + Acting) pattern
        
        Args:
            inputs: Input data for the agent
            instructions: Task instructions
            tools: List of tool configurations
            
        Returns:
            Dict containing agent output
        """
        logger.info(f"Agent {self.agent_name} starting execution")
        
        # Build ReAct prompt
        prompt = self._build_react_prompt(inputs, instructions, tools)
        
        # Execute reasoning loop
        reasoning = self._reason(prompt, inputs)
        
        # Take action
        result = self._act(reasoning, inputs, tools)
        
        # Log reasoning
        self.reasoning_history.append({
            'inputs': inputs,
            'reasoning': reasoning,
            'result': result
        })
        
        logger.info(f"Agent {self.agent_name} completed execution")
        
        return result
    
    def _build_react_prompt(self, inputs: Dict, instructions: str, tools: List[Dict]) -> str:
        """Build ReAct-style prompt"""
        
        tool_descriptions = "\n".join([
            f"- {tool['name']}: {tool.get('description', 'No description')}"
            for tool in tools
        ])
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI agent named {agent_name}.
Your role is to analyze the input, reason about the best approach, and execute the task.

Available Tools:
{tools}

Use this ReAct pattern:
1. THOUGHT: Analyze the input and plan your approach
2. ACTION: Decide which tool(s) to use and how
3. OBSERVATION: Consider what you learned
4. REPEAT if needed, or provide FINAL OUTPUT

Always structure your response as JSON with clear reasoning."""),
            ("user", """Task Instructions: {instructions}

Input Data:
{inputs}

Please proceed with your analysis and execution.""")
        ])
        
        return prompt_template.format_messages(
            agent_name=self.agent_name,
            tools=tool_descriptions or "No tools available",
            instructions=instructions,
            inputs=inputs
        )
    
    def _reason(self, prompt: str, inputs: Dict) -> str:
        """Generate reasoning using LLM"""
        try:
            time.sleep(1)
            response = self.llm.invoke(prompt)
            reasoning = response.content
            logger.info(f"Reasoning generated: {reasoning[:200]}...")
            return reasoning
        except Exception as e:
            logger.error(f"Error during reasoning: {e}")
            return f"Error in reasoning: {str(e)}"
    
    def _act(self, reasoning: str, inputs: Dict, tools: List[Dict]) -> Dict[str, Any]:
        """
        Execute action based on reasoning
        Override this method in subclasses for specific implementations
        """
        # Default implementation returns structured output
        return {
            'status': 'completed',
            'reasoning': reasoning,
            'inputs_processed': inputs,
            'agent': self.agent_name
        }
    
    def get_reasoning_history(self) -> List[Dict]:
        """Return reasoning history for analysis"""
        return self.reasoning_history