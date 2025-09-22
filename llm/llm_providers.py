"""
LLM Provider implementations for the RDR2 Agent system.
Implements the Dependency Inversion Principle by providing concrete implementations
of the ILLMProvider interface.
"""

from typing import Dict, Any
from crewai import LLM
import google.generativeai as genai
from models.base_models import ILLMProvider


class GeminiLLMProvider(ILLMProvider):
    """
    Concrete implementation of LLM provider using Google's Gemini API.
    Follows Single Responsibility Principle - only handles Gemini LLM operations.
    """
    
    def __init__(self, model_name: str, api_key: str, temperature: float = 0.0):
        """
        Initialize the Gemini LLM provider.
        
        Args:
            model_name: Name of the Gemini model (e.g., 'gemini-2.5-pro')
            api_key: API key for Gemini
            temperature: Temperature for generation (0.0 to 1.0)
        """
        self._model_name = model_name
        self._api_key = api_key
        self._temperature = temperature
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)
    
    def generate_response(self, prompt: str, temperature: float = None) -> str:
        """
        Generate a response using the Gemini model.
        
        Args:
            prompt: The input prompt for the model
            temperature: Optional temperature override
            
        Returns:
            str: Generated response
            
        Raises:
            Exception: If generation fails
        """
        try:
            # Use provided temperature or default
            gen_temperature = temperature if temperature is not None else self._temperature
            
            # Generate response
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=gen_temperature)
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini LLM generation failed: {str(e)}")


class CrewAILLMProvider(ILLMProvider):
    """
    Concrete implementation of LLM provider using CrewAI's LLM wrapper.
    This allows integration with CrewAI agents while maintaining our interface.
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize the CrewAI LLM provider.
        
        Args:
            model_config: Configuration dictionary containing model settings
        """
        self._config = model_config
        self._llm = LLM(
            model=model_config["model"],
            api_key=model_config["api_key"],
            temperature=model_config.get("temperature", 0.0),
            timeout=60,  # Increase timeout
            max_retries=3  # Add retries
        )
    
    def generate_response(self, prompt: str, temperature: float = None) -> str:
        """
        Generate a response using the CrewAI LLM wrapper.
        
        Args:
            prompt: The input prompt for the model
            temperature: Optional temperature override (not supported in this implementation)
            
        Returns:
            str: Generated response
            
        Raises:
            Exception: If generation fails
        """
        try:
            # Note: CrewAI LLM doesn't support dynamic temperature changes
            # This would need to be handled differently if required
            response = self._llm.generate(prompt)
            return response
            
        except Exception as e:
            raise Exception(f"CrewAI LLM generation failed: {str(e)}")
    
    def get_crewai_llm(self) -> LLM:
        """
        Get the underlying CrewAI LLM object for use with CrewAI agents.
        This method provides access to the original LLM for CrewAI integration.
        
        Returns:
            LLM: The CrewAI LLM object
        """
        return self._llm


class LLMProviderFactory:
    """
    Factory class for creating LLM providers.
    Implements the Factory Pattern to create appropriate LLM providers
    based on configuration.
    """
    
    @staticmethod
    def create_provider(provider_type: str, config: Dict[str, Any]) -> ILLMProvider:
        """
        Create an LLM provider based on the specified type.
        
        Args:
            provider_type: Type of provider ('gemini', 'crewai')
            config: Configuration dictionary for the provider
            
        Returns:
            ILLMProvider: Concrete LLM provider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        if provider_type.lower() == "gemini":
            return GeminiLLMProvider(
                model_name=config["model"],
                api_key=config["api_key"],
                temperature=config.get("temperature", 0.0)
            )
        elif provider_type.lower() == "crewai":
            return CrewAILLMProvider(config)
        else:
            raise ValueError(f"Unsupported LLM provider type: {provider_type}")
    
    @staticmethod
    def create_gemini_provider(model_name: str, api_key: str, temperature: float = 0.0) -> GeminiLLMProvider:
        """
        Convenience method to create a Gemini provider.
        
        Args:
            model_name: Name of the Gemini model
            api_key: API key for Gemini
            temperature: Temperature for generation
            
        Returns:
            GeminiLLMProvider: Configured Gemini provider
        """
        return GeminiLLMProvider(model_name, api_key, temperature)
    
    @staticmethod
    def create_crewai_provider(model_config: Dict[str, Any]) -> CrewAILLMProvider:
        """
        Convenience method to create a CrewAI provider.
        
        Args:
            model_config: Configuration dictionary for the model
            
        Returns:
            CrewAILLMProvider: Configured CrewAI provider
        """
        return CrewAILLMProvider(model_config)
