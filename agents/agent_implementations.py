"""
Agent implementations for the RDR2 Agent system.
Each agent has a single responsibility following the Single Responsibility Principle.
"""

from typing import Optional
from models.base_models import BaseAgent, AgentRole, ILLMProvider, TaskResult


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator agent responsible for analyzing user queries and coordinating workflow.
    Follows Single Responsibility Principle - only handles query analysis and coordination.
    """
    
    def __init__(self, llm_provider: ILLMProvider):
        """
        Initialize the orchestrator agent.
        
        Args:
            llm_provider: LLM provider for generating responses
        """
        super().__init__(AgentRole.ORCHESTRATOR, llm_provider)
    
    def _prepare_prompt(self, task_description: str, context: Optional[str] = None) -> str:
        """
        Prepare the prompt for orchestrator analysis.
        
        Args:
            task_description: The user's question/task
            context: Optional context (not used by orchestrator)
            
        Returns:
            str: Formatted prompt for the LLM
        """
        prompt = f"""
        You are an RDR2 Query Orchestrator with expertise in analyzing user questions about Red Dead Redemption 2.

        The user has asked: '{task_description}'

        **Your role is to analyze this question and provide guidance for the research team.**

        Analyze the question and determine:
        1. What type of information is needed (gameplay mechanics, locations, items, strategies, lore, etc.)
        2. How comprehensive the answer should be (brief tip vs detailed guide)
        3. What specific aspects should be researched
        4. The scope and depth of research required

        Provide clear, specific guidance for the research phase including:
        - The main topic areas to focus on
        - Key details that should be included
        - The appropriate level of detail needed
        - Any specific subtopics or related information that would be valuable

        Your analysis will guide the researcher on what to focus on and how deep to go.
        """
        
        return prompt


class ResearcherAgent(BaseAgent):
    """
    Researcher agent responsible for finding and gathering information.
    Follows Single Responsibility Principle - only handles research operations.
    """
    
    def __init__(self, llm_provider: ILLMProvider):
        """
        Initialize the researcher agent.
        
        Args:
            llm_provider: LLM provider for generating responses
        """
        super().__init__(AgentRole.RESEARCHER, llm_provider)
    
    def _prepare_prompt(self, task_description: str, context: Optional[str] = None) -> str:
        """
        Prepare the prompt for research task.
        
        Args:
            task_description: The research task/user question
            context: Context from orchestrator analysis
            
        Returns:
            str: Formatted prompt for the LLM
        """
        orchestrator_context = context if context else "No specific guidance provided."
        
        prompt = f"""
        You are an Expert RDR2 Researcher skilled at finding the most relevant and accurate information about Red Dead Redemption 2.

        **User's Question:** '{task_description}'

        **Orchestrator's Analysis:** {orchestrator_context}

        **Your primary role is to research and extract factual information, not to compose a final answer.**

        Based on the orchestrator's guidance, your task is to:
        1. Consider the research scope and focus areas identified
        2. Identify the key information needed to answer the user's question
        3. Return comprehensive factual findings exactly as retrieved from your tools
        4. Include all relevant details, data points, and gameplay information
        5. Do not summarize or rephrase - provide raw researched content

        You have access to:
        - Local RDR2 Database Search (use this first)
        - Web Search RDR2 (use if local results are insufficient)

        Strategy:
        - Start with local database search
        - If similarity score is high (>2.0) or information seems incomplete, supplement with web search
        - Return all relevant factual findings ready for the writer to process

        Your output should be comprehensive raw research material containing all relevant information found.
        """
        
        return prompt


class WriterAgent(BaseAgent):
    """
    Writer agent responsible for composing final reports from research material.
    Follows Single Responsibility Principle - only handles content writing and formatting.
    """
    
    def __init__(self, llm_provider: ILLMProvider):
        """
        Initialize the writer agent.
        
        Args:
            llm_provider: LLM provider for generating responses
        """
        super().__init__(AgentRole.WRITER, llm_provider)
    
    def _prepare_prompt(self, task_description: str, context: Optional[str] = None) -> str:
        """
        Prepare the prompt for writing task.
        
        Args:
            task_description: The original user question
            context: Research material and orchestrator guidance
            
        Returns:
            str: Formatted prompt for the LLM
        """
        research_context = context if context else "No research material provided."
        
        prompt = f"""
        You are a Professional Gaming Content Writer specializing in Red Dead Redemption 2.

        **Original User Question:** '{task_description}'

        **Research Material and Guidance:** 
        {research_context}

        **Your task is to synthesize this into a clear, concise, and well-structured final report.**

        Follow these steps:
        1. Review the orchestrator's guidance on the type and scope of answer needed
        2. Carefully read all research material and identify key facts, data points, and gameplay tips
        3. Extract only **directly relevant** practical details (locations, costs, mission names, strategies)
        4. Compose a cohesive report that:
           - Answers the user's question directly
           - Matches the scope indicated by the orchestrator
           - Includes valuable related gameplay insights
           - Uses headings or bullet points for clarity
           - Is written in an engaging, helpful tone

        **Important Guidelines:**
        - Do NOT mention the research process, tools, sources, or URLs
        - Your final report should read as if written by a knowledgeable human expert
        - Focus on actionable information and practical tips
        - Use markdown formatting for better readability
        - Keep the tone friendly and helpful

        Provide your final answer as a complete, polished report in markdown format.
        """
        
        return prompt
    
    def _post_process_response(self, response: str) -> str:
        """
        Post-process the writer's response to ensure proper formatting.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            str: Processed response with proper formatting
        """
        # Ensure the response is properly formatted
        # Add any additional formatting logic here if needed
        return response.strip()


class AgentFactory:
    """
    Factory class for creating different types of agents.
    Implements the Factory Pattern for agent creation.
    """
    
    @staticmethod
    def create_orchestrator(llm_provider: ILLMProvider) -> OrchestratorAgent:
        """
        Create an orchestrator agent.
        
        Args:
            llm_provider: LLM provider for the agent
            
        Returns:
            OrchestratorAgent: Configured orchestrator agent
        """
        return OrchestratorAgent(llm_provider)
    
    @staticmethod
    def create_researcher(llm_provider: ILLMProvider) -> ResearcherAgent:
        """
        Create a researcher agent.
        
        Args:
            llm_provider: LLM provider for the agent
            
        Returns:
            ResearcherAgent: Configured researcher agent
        """
        return ResearcherAgent(llm_provider)
    
    @staticmethod
    def create_writer(llm_provider: ILLMProvider) -> WriterAgent:
        """
        Create a writer agent.
        
        Args:
            llm_provider: LLM provider for the agent
            
        Returns:
            WriterAgent: Configured writer agent
        """
        return WriterAgent(llm_provider)
    
    @staticmethod
    def create_all_agents(llm_provider: ILLMProvider) -> tuple[OrchestratorAgent, ResearcherAgent, WriterAgent]:
        """
        Create all three types of agents.
        
        Args:
            llm_provider: LLM provider for all agents
            
        Returns:
            tuple: (orchestrator, researcher, writer) agents
        """
        orchestrator = AgentFactory.create_orchestrator(llm_provider)
        researcher = AgentFactory.create_researcher(llm_provider)
        writer = AgentFactory.create_writer(llm_provider)
        
        return orchestrator, researcher, writer
