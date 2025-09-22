"""
Main coordinator implementation for the RDR2 Agent system.
Implements the Dependency Inversion Principle and coordinates the entire workflow.
"""

import asyncio
import time
from typing import Dict, List, Optional
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

from models.base_models import IAgentCoordinator, IAgent, TaskResult, AgentRole, ISearchTool, SearchProvider
from config.configuration_manager import ConfigurationManager
from llm.llm_providers import CrewAILLMProvider, LLMProviderFactory
from knowledge.knowledge_base import ChromaKnowledgeBase
from search.search_tools import SearchToolFactory
from utils.response_cleaner import ResponseCleaner


class RDR2AgentCoordinator(IAgentCoordinator):
    """
    Main coordinator for the RDR2 Agent system.
    Follows Dependency Inversion Principle - depends on abstractions, not concrete implementations.
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        """
        Initialize the RDR2 Agent Coordinator.
        
        Args:
            config_manager: Configuration manager instance
        """
        self._config = config_manager
        self._knowledge_base: Optional[ChromaKnowledgeBase] = None
        self._search_tools: Dict[SearchProvider, ISearchTool] = {}
        self._crew: Optional[Crew] = None
        self._agents: Dict[AgentRole, Agent] = {}
        
        # Initialize the system
        self._initialize_system()
    
    def _initialize_system(self) -> None:
        """Initialize all components of the system."""
        try:
            print("Initializing RDR2 Agent System...")
            
            # Initialize knowledge base
            self._initialize_knowledge_base()
            
            # Initialize search tools
            self._initialize_search_tools()
            
            # Initialize CrewAI agents and crew
            self._initialize_crew()
            
            print("RDR2 Agent System initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing system: {e}")
            raise
    
    def _initialize_knowledge_base(self) -> None:
        """Initialize the knowledge base."""
        try:
            db_path = self._config.get_chroma_db_path()
            embedding_model = self._config.get_embedding_model()
            
            self._knowledge_base = ChromaKnowledgeBase(db_path, embedding_model)
            
            # Load knowledge from files
            knowledge_path = self._config.get_knowledge_base_path()
            success = self._knowledge_base.load_knowledge(knowledge_path)
            
            if not success:
                raise Exception("Failed to load knowledge base")
            
            print(f"Knowledge base initialized with {self._knowledge_base.get_document_count()} documents")
            
        except Exception as e:
            print(f"Error initializing knowledge base: {e}")
            raise
    
    def _initialize_search_tools(self) -> None:
        """Initialize search tools."""
        try:
            # Get configuration
            serper_api_key = self._config.get_api_key("serper")
            relevance_threshold = self._config.get_relevance_threshold()
            excluded_domains = self._config.get_excluded_domains()
            
            # Create search tools
            local_tool, web_tool = SearchToolFactory.create_all_search_tools(
                self._knowledge_base,
                serper_api_key,
                relevance_threshold,
                excluded_domains
            )
            
            self._search_tools[SearchProvider.LOCAL_DATABASE] = local_tool
            self._search_tools[SearchProvider.WEB_SEARCH] = web_tool
            
            print("Search tools initialized successfully")
            
        except Exception as e:
            print(f"Error initializing search tools: {e}")
            raise
    
    def _initialize_crew(self) -> None:
        """Initialize CrewAI agents and crew."""
        try:
            # Get LLM configuration
            llm_config = self._config.get_llm_config("gemini-flash")
            
            # Create LLM provider
            llm_provider = LLMProviderFactory.create_provider("crewai", llm_config)
            crewai_llm = llm_provider.get_crewai_llm()
            
            # Create CrewAI tools
            local_search_tool = self._create_local_search_crewai_tool()
            web_search_tool = self._create_web_search_crewai_tool()
            
            # Create CrewAI agents
            self._agents[AgentRole.ORCHESTRATOR] = Agent(
                role='RDR2 Query Orchestrator',
                goal='Analyze user questions and coordinate the appropriate agents to provide comprehensive answers.',
                backstory=(
                    "You are a strategic coordinator who understands the strengths of different specialists. "
                    "You analyze each user question to determine what type of information is needed, "
                    "coordinate with the appropriate agents, and ensure the final output meets the user's needs."
                ),
                llm=crewai_llm,
                verbose=True
            )
            
            self._agents[AgentRole.RESEARCHER] = Agent(
                role='Expert RDR2 Researcher',
                goal='Find the most relevant and accurate information on any given topic about Red Dead Redemption 2.',
                backstory=(
                    "You are a master researcher, skilled at using both local database and web search tools strategically. "
                    "You always start with the local database, then decide if web search is needed based on the quality "
                    "and completeness of the results. You are a fact-finder, not a writer. "
                    "IMPORTANT: You have search limits - local: 1 search, web: 2 searches maximum. Use them wisely and stop when limits are reached or no relevant info is found."
                ),
                tools=[local_search_tool, web_search_tool],
                llm=crewai_llm,
                verbose=True
            )
            
            self._agents[AgentRole.WRITER] = Agent(
                role='Professional Gaming Content Writer',
                goal='Compose clear, engaging, and well-structured reports based on research findings.',
                backstory=(
                    "You are a renowned writer in the gaming community, known for your ability to "
                    "transform raw data and notes into high-quality, easy-to-read articles. "
                    "You do not perform research yourself; you work with the material provided to you."
                ),
                llm=crewai_llm,
                verbose=True
            )
            
            # Create crew
            self._crew = Crew(
                agents=list(self._agents.values()),
                tasks=[],  # Tasks will be created dynamically
                process=Process.sequential,
                memory=True,
                max_iter=3,  # Limit iterations to prevent infinite loops
                embedder={
                    "provider": "google",
                    "config": {
                        "api_key": self._config.get_api_key("gemini"),
                        "model": "text-embedding-004"
                    }
                },
                verbose=True
            )
            
            print("CrewAI agents and crew initialized successfully")
            
        except Exception as e:
            print(f"Error initializing crew: {e}")
            raise
    
    def _create_local_search_crewai_tool(self):
        """Create CrewAI tool for local database search."""
        local_tool = self._search_tools[SearchProvider.LOCAL_DATABASE]
        
        @tool("Local RDR2 Database Search")
        def local_search_tool(question: str) -> str:
            """
            Search the local RDR2 database for information. Use this first for any RDR2 question.
            Returns local database results with distance score to help evaluate relevance.
            """
            try:
                result = local_tool.search(question)
                return f"Local Database Result (Similarity Score: {result.relevance_score:.2f}):\\n\\n{result.content}"
            except Exception as e:
                return f"Error searching local database: {str(e)}"
        
        return local_search_tool
    
    def _create_web_search_crewai_tool(self):
        """Create CrewAI tool for web search."""
        web_tool = self._search_tools[SearchProvider.WEB_SEARCH]
        
        @tool("Web Search RDR2")
        def web_search_tool(question: str) -> str:
            """
            Search the web for Red Dead Redemption 2 information. Use this when local database 
            results are insufficient or when you need more comprehensive/recent information.
            """
            max_retries = 2
            
            for attempt in range(max_retries):
                try:
                    result = web_tool.search(question)
                    
                    # Check if the result contains error messages that might be temporary
                    if "Scraper API error: 500" in result.content or "Scraping failed" in result.content:
                        if attempt < max_retries - 1:  # Not the last attempt
                            print(f"⚠️ Web search attempt {attempt + 1} failed (server error), retrying...")
                            time.sleep(2)  # Brief delay before retry
                            continue
                        else:  # Last attempt failed
                            print(f"⚠️ Web search failed after {max_retries} attempts")
                            return "Web search is temporarily unavailable due to server issues. Please provide the best answer you can based on your existing knowledge."
                    
                    # Check for other errors that probably won't benefit from retry
                    if "Timeout error" in result.content or "Network error" in result.content:
                        print(f"⚠️ Web search encountered network issues")
                        return "Web search experienced network issues. Please provide the best answer you can based on your existing knowledge."
                    
                    # Check if we got very minimal content (less than 20 characters is likely an error)
                    if len(result.content.strip()) < 20:
                        if attempt < max_retries - 1:  # Try once more for minimal content
                            print(f"⚠️ Web search returned minimal content, retrying...")
                            time.sleep(1)
                            continue
                        else:
                            print(f"⚠️ Web search returned minimal content after retries")
                            return "Web search returned limited results. Please provide the best answer you can based on your existing knowledge."
                    
                    # Success! Return the result
                    print(f"✅ Web search successful on attempt {attempt + 1}")
                    return f"Web Search Result:\\n\\n{result.content}"
                    
                except Exception as e:
                    if attempt < max_retries - 1:  # Not the last attempt
                        print(f"⚠️ Web search attempt {attempt + 1} failed with exception: {str(e)}, retrying...")
                        time.sleep(2)
                        continue
                    else:  # Last attempt failed
                        print(f"⚠️ Web search failed after {max_retries} attempts: {str(e)}")
                        return "Web search is currently unavailable. Please provide the best answer you can based on your existing knowledge."
        
        return web_search_tool
    
    def execute_workflow(self, user_query: str) -> TaskResult:
        """
        Execute the complete workflow for a user query.
        
        Args:
            user_query: The user's question/query
            
        Returns:
            TaskResult: The final result of the workflow
        """
        try:
            # Reset crew memory for new query
            self._crew.reset_memories(command_type='long')
            
            # Create tasks dynamically
            tasks = self._create_tasks(user_query)
            self._crew.tasks = tasks
            
            # Execute the crew workflow (synchronous - more reliable with LLMs)
            print(f"\\nExecuting workflow for query: {user_query}")
            crew_output = self._crew.kickoff(inputs={"question": user_query})
            
            # Extract final result with validation
            final_content = crew_output.tasks_output[-1].raw if crew_output.tasks_output else "No output generated"
            
            # Validate the response
            if not final_content or final_content.strip() == "" or final_content.lower() == "none":
                print("⚠️ Empty or invalid response detected from LLM")
                final_content = f"I apologize, but I encountered a technical issue while processing your question: '{user_query}'. Please try asking your question in a different way, or contact support if the issue persists."
            
            # Check for error indicators in the response
            if any(error_phrase in final_content.lower() for error_phrase in [
                "scraper api error", "scraping failed", "500", "invalid response", 
                "none or empty response", "llm call"
            ]):
                print("⚠️ Error indicators detected in response, providing fallback")
                final_content = f"I encountered some technical difficulties while gathering additional information about '{user_query}'. However, I can still provide you with helpful information based on my comprehensive Red Dead Redemption 2 knowledge base. Please try your question again if you'd like me to attempt another search."
            
            # Clean the response to remove repetition and fix formatting
            cleaned_content = ResponseCleaner.clean_response(final_content)
            
            return TaskResult(
                content=cleaned_content,
                success=True,
                agent_role=AgentRole.WRITER
            )
            
        except Exception as e:
            return TaskResult(
                content="",
                success=False,
                agent_role=AgentRole.WRITER,
                error_message=str(e)
            )
    
    def _create_tasks(self, user_query: str) -> List[Task]:
        """
        Create tasks for the workflow.
        
        Args:
            user_query: The user's question
            
        Returns:
            List[Task]: List of tasks for the crew
        """
        orchestrator_task = Task(
            agent=self._agents[AgentRole.ORCHESTRATOR],
            description=(
                "The user has asked: '{question}'\\n\\n"
                "**Your role is to analyze this question and coordinate the appropriate agents to provide a comprehensive answer.**\\n\\n"
                "Analyze the question and determine:\\n"
                "1. What type of information is needed (gameplay mechanics, locations, items, strategies, lore, etc.)\\n"
                "2. How comprehensive the answer should be\\n"
                "3. Whether standard research will be sufficient or if specialized knowledge is needed\\n\\n"
                "Based on your analysis, provide clear instructions for the research phase. "
                "Your output will guide the researcher on what to focus on and how deep to go."
            ),
            expected_output=(
                "A clear analysis of the user's question including: the type of information needed, "
                "the scope of research required, and specific guidance for the researcher on what to focus on."
            )
        )
        
        research_task = Task(
            agent=self._agents[AgentRole.RESEARCHER],
            description=(
                "Based on the orchestrator's analysis, research the user's question: '{question}'\\n\\n"
                "**Your primary role is to research and extract factual information, not to compose a final answer.**\\n\\n"
                "Follow these steps:\\n"
                "1. Consider the orchestrator's guidance on research scope and focus areas\\n"
                "2. Start by searching the local RDR2 database using the Local RDR2 Database Search tool\\n"
                "3. Evaluate the local results:\\n"
                "   - If similarity score is low (>2.0) or information seems incomplete/irrelevant, use the Web Search tool\\n"
                "   - If local results directly answer the question with sufficient detail, you can use them\\n"
                "4. **SEARCH LIMITS: Use local search max 1 time, web search max 2 times. Do not exceed these limits.**\\n"
                "5. **If both searches return irrelevant results or no results, immediately conclude with: 'No relevant information found for [topic] in available sources'**\\n"
                "6. Return **all relevant factual findings** exactly as retrieved, without summarizing or rephrasing\\n\\n"
                "Your output should be raw researched content, ready for the writer to process."
            ),
            expected_output=(
                "A comprehensive block of factual text exactly as retrieved by the tools, containing all relevant information found, with no summaries or conclusions. Ready for the writer to process."
            ),
            context=[orchestrator_task]
        )
        
        write_task = Task(
            agent=self._agents[AgentRole.WRITER],
            description=(
                """You have been provided with research material about Red Dead Redemption 2 and orchestrator guidance.

Your task is to synthesize this into a **clear, concise, and well-structured final report** that answers the user's specific question.

Consider both:
1. The orchestrator's analysis of what the user needs
2. The research material provided

Follow these steps:
1. Review the orchestrator's guidance on the type and scope of answer needed
2. Carefully read all research material and identify key facts, data points, and gameplay tips
3. Extract only **directly relevant** practical details (locations, costs, mission names, strategies)
4. Compose a cohesive report that:
   - Answers the user's question directly
   - Matches the scope indicated by the orchestrator
   - Includes valuable related gameplay insights
   - Uses headings or bullet points for clarity

**Important:**  
- Do NOT mention the research process, tools, sources, or URLs
- Your final report should read as if written by a knowledgeable human expert
- Output your final answer in markdown format
- **If the research material doesn't contain information to answer the question, honestly say "I don't have information about [topic] in my Red Dead Redemption 2 knowledge base" rather than providing unrelated content**
"""
            ),
            expected_output=(
                "A clear, detailed, and helpful report in markdown format that answers the user's question directly. "
                "Use headings or bullet points if needed for clarity. The report should feel like it comes from a single, expert human source."
            ),
            context=[orchestrator_task, research_task]
        )
        
        return [orchestrator_task, research_task, write_task]
    
    def add_agent(self, agent: IAgent) -> None:
        """
        Add an agent to the coordination system.
        
        Args:
            agent: Agent to add
        """
        # This method is part of the interface but not used in the current CrewAI implementation
        # It could be extended for custom agent management
        pass
    
    def get_system_status(self) -> Dict[str, any]:
        """
        Get the status of the system components.
        
        Returns:
            Dict[str, any]: System status information
        """
        return {
            "knowledge_base": {
                "initialized": self._knowledge_base is not None,
                "document_count": self._knowledge_base.get_document_count() if self._knowledge_base else 0
            },
            "search_tools": {
                "local": SearchProvider.LOCAL_DATABASE in self._search_tools,
                "web": SearchProvider.WEB_SEARCH in self._search_tools
            },
            "crew": {
                "initialized": self._crew is not None,
                "agent_count": len(self._agents)
            }
        }
