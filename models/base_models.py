"""
Base models and interfaces for the RDR2 Agent system.
This file defines the foundation classes that follow SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class AgentRole(Enum):
    """Enumeration of different agent roles in the system."""
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher" 
    WRITER = "writer"


class SearchProvider(Enum):
    """Enumeration of different search providers."""
    LOCAL_DATABASE = "local_database"
    WEB_SEARCH = "web_search"


@dataclass
class SearchResult:
    """Data class representing a search result."""
    content: str
    relevance_score: float
    source: SearchProvider
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TaskResult:
    """Data class representing the result of a task execution."""
    content: str
    success: bool
    agent_role: AgentRole
    execution_time: float = 0.0
    error_message: Optional[str] = None


# Abstract Base Classes (Interfaces)

class ISearchTool(ABC):
    """
    Any search tool must implement this interface.
    """
    
    @abstractmethod
    def search(self, query: str) -> SearchResult:
        """
        Perform a search operation.
        
        Args:
            query: The search query string
            
        Returns:
            SearchResult: The search result with content and metadata
        """
        pass


class IKnowledgeBase(ABC):
    """
    Interface for knowledge base operations.
    """
    
    @abstractmethod
    def load_knowledge(self, source_path: str) -> bool:
        """Load knowledge from a source."""
        pass
    
    @abstractmethod
    def find_relevant_content(self, query: str, top_n: int = 5) -> Tuple[str, float]:
        """Find the most relevant content for a query."""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """Get the total number of documents in the knowledge base."""
        pass


class ILLMProvider(ABC):
    """
    Interface for Language Model providers.
    Abstracts away the specific LLM implementation.
    """
    
    @abstractmethod
    def generate_response(self, prompt: str, temperature: float = 0.0) -> str:
        """Generate a response using the language model."""
        pass


class IAgentCoordinator(ABC):
    
    @abstractmethod
    async def execute_workflow(self, user_query: str) -> TaskResult:
        """Execute the complete workflow for a user query."""
        pass
    
    @abstractmethod
    def add_agent(self, agent: 'IAgent') -> None:
        """Add an agent to the coordination system."""
        pass


class IAgent(ABC):
    """
    Base interface for all agents.
    Each agent has a single responsibility (SRP).
    """
    
    @abstractmethod
    def execute_task(self, task_description: str, context: Optional[str] = None) -> TaskResult:
        """Execute a specific task assigned to this agent."""
        pass
    
    @abstractmethod
    def get_role(self) -> AgentRole:
        """Get the role of this agent."""
        pass


class IConfigurationManager(ABC):
    """
    Interface for configuration management.
    Handles all configuration-related operations.
    """
    
    @abstractmethod
    def get_api_key(self, service: str) -> str:
        """Get API key for a specific service."""
        pass
    
    @abstractmethod
    def get_llm_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific LLM model."""
        pass
    
    @abstractmethod
    def load_configuration(self, config_path: Optional[str] = None) -> bool:
        """Load configuration from file or environment."""
        pass


# Abstract Base Classes for Implementation

class BaseAgent(IAgent):
    """
    Base implementation for agents providing common functionality.
    Follows Template Method Pattern - subclasses implement specific behavior.
    """
    
    def __init__(self, role: AgentRole, llm_provider: ILLMProvider):
        self._role = role
        self._llm_provider = llm_provider
    
    def get_role(self) -> AgentRole:
        """Return the role of this agent."""
        return self._role
    
    @abstractmethod
    def _prepare_prompt(self, task_description: str, context: Optional[str] = None) -> str:
        """Prepare the prompt for the LLM. Must be implemented by subclasses."""
        pass
    
    def execute_task(self, task_description: str, context: Optional[str] = None) -> TaskResult:
        """
        Execute task using Template Method Pattern.
        This method defines the algorithm structure while allowing subclasses
        to customize specific steps.
        """
        try:
            # Step 1: Prepare the prompt (implemented by subclasses)
            prompt = self._prepare_prompt(task_description, context)
            
            # Step 2: Generate response using LLM
            response = self._llm_provider.generate_response(prompt)
            
            # Step 3: Post-process if needed
            final_response = self._post_process_response(response)
            
            return TaskResult(
                content=final_response,
                success=True,
                agent_role=self._role
            )
            
        except Exception as e:
            return TaskResult(
                content="",
                success=False,
                agent_role=self._role,
                error_message=str(e)
            )
    
    def _post_process_response(self, response: str) -> str:
        """
        Post-process the LLM response. Can be overridden by subclasses.
        Default implementation returns the response as-is.
        """
        return response


class BaseSearchTool(ISearchTool):
    """
    Base implementation for search tools.
    Provides common functionality while allowing specific implementations.
    """
    
    def __init__(self, provider_type: SearchProvider):
        self._provider_type = provider_type
    
    @abstractmethod
    def _perform_search(self, query: str) -> Tuple[str, float]:
        """Perform the actual search operation. Must be implemented by subclasses."""
        pass
    
    def search(self, query: str) -> SearchResult:
        """Search for a query.
        Template method for search operation.
        Handles common logic while delegating specific search to subclasses.
        """
        try:
            content, relevance_score = self._perform_search(query)
            
            return SearchResult(
                content=content,
                relevance_score=relevance_score,
                source=self._provider_type,
                metadata={
                    "query": query,
                    "timestamp": self._get_timestamp()
                }
            )
            
        except Exception as e:
            return SearchResult(
                content=f"Search failed: {str(e)}",
                relevance_score=float('inf'),
                source=self._provider_type,
                metadata={"error": str(e)}
            )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        from datetime import datetime
        return datetime.now().isoformat()
