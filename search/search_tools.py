"""
Search tools implementation for the RDR2 Agent system.
Implements the Open/Closed Principle - open for extension, closed for modification.
"""

import requests
import json
import time
from typing import Tuple, List
from models.base_models import BaseSearchTool, SearchProvider, IKnowledgeBase


class LocalDatabaseSearchTool(BaseSearchTool):
    """
    Concrete implementation of search tool for local database.
    Follows Single Responsibility Principle - only handles local database searches.
    """
    
    def __init__(self, knowledge_base: IKnowledgeBase, relevance_threshold: float = 2.2):
        """
        Initialize the local database search tool.
        
        Args:
            knowledge_base: The knowledge base to search
            relevance_threshold: Threshold for relevance scoring
        """
        super().__init__(SearchProvider.LOCAL_DATABASE)
        self._knowledge_base = knowledge_base
        self._relevance_threshold = relevance_threshold
    
    def _perform_search(self, query: str) -> Tuple[str, float]:
        """
        Perform search on the local knowledge base.
        
        Args:
            query: Search query string
            
        Returns:
            Tuple[str, float]: Search content and relevance score
        """
        try:
            print("Searching local database...")
            
            # Use the knowledge base to find relevant content
            content, distance = self._knowledge_base.find_relevant_content(query, top_n=5)
            
            # Check if we have meaningful content
            if content and len(content.strip()) > 10:
                return content, distance
            else:
                return "No relevant information found in local database.", float('inf')
                
        except Exception as e:
            raise Exception(f"Local database search failed: {str(e)}")
    
    def is_result_relevant(self, relevance_score: float) -> bool:
        """
        Check if the search result is relevant based on the threshold.
        
        Args:
            relevance_score: The relevance score from the search
            
        Returns:
            bool: True if result is relevant (score below threshold)
        """
        return relevance_score <= self._relevance_threshold


class WebSearchTool(BaseSearchTool):
    """
    Concrete implementation of search tool for web searches.
    Uses Serper API for web search functionality.
    """
    
    def __init__(self, api_key: str, excluded_domains: List[str] = None):
        """
        Initialize the web search tool.
        
        Args:
            api_key: Serper API key
            excluded_domains: List of domains to exclude from results
        """
        super().__init__(SearchProvider.WEB_SEARCH)
        self._api_key = api_key
        self._excluded_domains = excluded_domains or []
        self._scraper = WebScraper(api_key)
    
    def _perform_search(self, query: str) -> Tuple[str, float]:
        """
        Perform web search using Serper API.
        
        Args:
            query: Search query string
            
        Returns:
            Tuple[str, float]: Search content and relevance score
        """
        try:
            print("Searching web for RDR2 information...")
            
            # Enhance query for RDR2 context
            enhanced_query = f"Red Dead Redemption 2 {query}"
            
            # Get search results
            search_results = self._search_urls(enhanced_query, top_n=3)
            
            if not search_results:
                return "No web search results found.", float('inf')
            
            # Try to scrape the first result with error handling
            try:
                scraped_content = self._scraper.scrape_page(search_results[0])
                
                # Check if scraping returned an error message
                if "Scraper API error" in scraped_content or "Scraping failed" in scraped_content:
                    print(f"⚠️ Scraper returned error, trying fallback approach")
                    return "Web scraping temporarily unavailable due to service issues.", 2.0
                
                # Check if we got very minimal content (less than 20 characters is likely an error)
                if len(scraped_content.strip()) < 20:
                    print(f"⚠️ Scraped content too short ({len(scraped_content)} chars)")
                    return f"Limited web results found for: {query}", 2.0
                
                # Web search gets a relevance score of 1.0 (assuming relevant)
                return scraped_content, 1.0
                
            except Exception as scrape_error:
                print(f"⚠️ Scraping failed: {str(scrape_error)}")
                return f"Web search found results but scraping failed. Limited information available for: {query}", 2.0
            
        except Exception as e:
            print(f"⚠️ Web search completely failed: {str(e)}")
            return f"Web search service unavailable. Please rely on local database information.", float('inf')
    
    def _search_urls(self, query: str, top_n: int = 1) -> List[str]:
        """
        Search for URLs using Serper API.
        
        Args:
            query: Search query
            top_n: Number of top results to return
            
        Returns:
            List[str]: List of URLs
        """
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': self._api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code != 200:
            raise Exception(f"Search API error: {response.status_code} {response.text}")
        
        data = response.json()
        organic_results = data.get("organic", [])
        
        # Filter out excluded domains
        filtered_results = []
        for result in organic_results:
            url = result.get('link', '')
            if not any(domain in url for domain in self._excluded_domains):
                filtered_results.append(url)
                if len(filtered_results) == top_n:
                    break
        
        return filtered_results


class WebScraper:
    """
    Web scraper utility using Serper API.
    Separate class following Single Responsibility Principle.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the web scraper.
        
        Args:
            api_key: Serper API key
        """
        self._api_key = api_key
    
    def scrape_page(self, target_url: str) -> str:
        """
        Scrape content from a web page with retry mechanism.
        
        Args:
            target_url: URL to scrape
            
        Returns:
            str: Scraped text content
        """
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                url = "https://scrape.serper.dev"
                payload = json.dumps({"url": target_url})
                headers = {
                    'X-API-KEY': self._api_key,
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(url, headers=headers, data=payload, timeout=30)
                
                if response.status_code == 500:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Scraper API returned 500 error (attempt {attempt + 1}), retrying in 3 seconds...")
                        time.sleep(3)
                        continue
                    else:
                        print(f"⚠️ Scraper service experiencing persistent issues (500 error after {max_retries} attempts)")
                        return "Scraper API error: 500 - Service temporarily unavailable after retries"
                
                if response.status_code != 200:
                    error_msg = f"Scraper API error: {response.status_code}"
                    return f"{error_msg} {response.text}"
                
                data = response.json()
                
                # Check for error messages in the response
                if "message" in data and "Scraping failed" in data.get("message", ""):
                    if attempt < max_retries - 1:
                        print(f"⚠️ Scraping failed for URL: {target_url} (attempt {attempt + 1}), retrying...")
                        time.sleep(2)
                        continue
                    else:
                        print(f"⚠️ Scraping failed for URL: {target_url} after {max_retries} attempts")
                        return f"Scraping failed for {target_url} after retries"
                
                text_content = data.get("text", "")
                
                if not text_content or len(text_content.strip()) < 10:
                    if attempt < max_retries - 1:
                        print(f"⚠️ No/minimal content from {target_url} (attempt {attempt + 1}), retrying...")
                        time.sleep(1)
                        continue
                    else:
                        return f"No content extracted from {target_url} after retries"
                
                word_count = len(text_content.split())
                print(f"✅ Scraped {word_count} words from {target_url} (attempt {attempt + 1})")
                
                return text_content
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ Timeout while scraping {target_url} (attempt {attempt + 1}), retrying...")
                    time.sleep(3)
                    continue
                else:
                    print(f"⚠️ Persistent timeout while scraping {target_url}")
                    return f"Timeout error while scraping {target_url} after retries"
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Network error while scraping {target_url} (attempt {attempt + 1}): {str(e)}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print(f"⚠️ Persistent network error while scraping {target_url}: {str(e)}")
                    return f"Network error while scraping {target_url} after retries"
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Unexpected error while scraping {target_url} (attempt {attempt + 1}): {str(e)}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print(f"⚠️ Persistent unexpected error while scraping {target_url}: {str(e)}")
                    return f"Unexpected error while scraping {target_url} after retries"


class SearchToolFactory:
    """
    Factory class for creating search tools.
    Implements the Factory Pattern to create appropriate search tools.
    """
    
    @staticmethod
    def create_local_search_tool(knowledge_base: IKnowledgeBase, relevance_threshold: float = 2.2) -> LocalDatabaseSearchTool:
        """
        Create a local database search tool.
        
        Args:
            knowledge_base: The knowledge base to search
            relevance_threshold: Threshold for relevance scoring
            
        Returns:
            LocalDatabaseSearchTool: Configured local search tool
        """
        return LocalDatabaseSearchTool(knowledge_base, relevance_threshold)
    
    @staticmethod
    def create_web_search_tool(api_key: str, excluded_domains: List[str] = None) -> WebSearchTool:
        """
        Create a web search tool.
        
        Args:
            api_key: Serper API key
            excluded_domains: List of domains to exclude
            
        Returns:
            WebSearchTool: Configured web search tool
        """
        return WebSearchTool(api_key, excluded_domains)
    
    @staticmethod
    def create_all_search_tools(knowledge_base: IKnowledgeBase, api_key: str, 
                               relevance_threshold: float = 2.2, 
                               excluded_domains: List[str] = None) -> Tuple[LocalDatabaseSearchTool, WebSearchTool]:
        """
        Create both local and web search tools.
        
        Args:
            knowledge_base: The knowledge base to search
            api_key: Serper API key
            relevance_threshold: Threshold for relevance scoring
            excluded_domains: List of domains to exclude
            
        Returns:
            Tuple[LocalDatabaseSearchTool, WebSearchTool]: Both search tools
        """
        local_tool = SearchToolFactory.create_local_search_tool(knowledge_base, relevance_threshold)
        web_tool = SearchToolFactory.create_web_search_tool(api_key, excluded_domains)
        
        return local_tool, web_tool
