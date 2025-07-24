# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
from typing import Dict, List, Optional
from qwen_agent.tools.base import BaseTool, register_tool

# Configurar encoding UTF-8 no Windows
if sys.platform.startswith('win'):
    try:
        os.system('chcp 65001 > nul 2>&1')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Função para print seguro
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais
        import re
        clean_text = re.sub(r'[^\x00-\x7F]+', '', str(text))
        print(clean_text)

@register_tool('google_search')
class GoogleSearchTool(BaseTool):
    """Google Search tool for WebSailor agent"""
    
    description = 'Search the web using Google Search API. Useful for finding current information, news, and general web content.'
    parameters = [
        {
            'name': 'query',
            'type': 'string',
            'description': 'The search query to execute',
            'required': True
        },
        {
            'name': 'num_results',
            'type': 'integer', 
            'description': 'Number of search results to return (default: 10, max: 20)',
            'required': False
        }
    ]
    
    def __init__(self, api_key: str):
        """
        Initialize Google Search tool
        
        Args:
            api_key: Serper API key for Google Search
        """
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def call(self, params: Dict, **kwargs) -> str:
        """
        Execute Google search
        
        Args:
            params: Search parameters
            
        Returns:
            Formatted search results
        """
        query = params.get('query', '')
        num_results = min(params.get('num_results', 10), 20)
        
        if not query:
            return "Error: Search query is required"
        
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results,
                'gl': 'br',  # Brazil
                'hl': 'pt'   # Portuguese
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return self._format_search_results(data, query)
            
        except requests.exceptions.RequestException as e:
            return f"Error performing search: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def _format_search_results(self, data: Dict, query: str) -> str:
        """Format search results for the agent"""
        results = []
        results.append(f"Search Results for: {query}")
        results.append("=" * 50)
        
        # Answer box (if available)
        if 'answerBox' in data:
            answer = data['answerBox']
            results.append("\n[ANSWER BOX]:")
            if 'answer' in answer:
                results.append(f"Answer: {answer['answer']}")
            if 'snippet' in answer:
                results.append(f"Details: {answer['snippet']}")
            if 'link' in answer:
                results.append(f"Source: {answer['link']}")
            results.append("")
        
        # Knowledge graph (if available)
        if 'knowledgeGraph' in data:
            kg = data['knowledgeGraph']
            results.append("[KNOWLEDGE GRAPH]:")
            if 'title' in kg:
                results.append(f"Title: {kg['title']}")
            if 'description' in kg:
                results.append(f"Description: {kg['description']}")
            if 'attributes' in kg:
                for key, value in kg['attributes'].items():
                    results.append(f"{key}: {value}")
            results.append("")
        
        # Organic results
        if 'organic' in data:
            results.append("[SEARCH RESULTS]:")
            for i, result in enumerate(data['organic'][:10], 1):
                results.append(f"\n{i}. {result.get('title', 'No title')}")
                results.append(f"   URL: {result.get('link', 'No URL')}")
                if 'snippet' in result:
                    results.append(f"   Summary: {result['snippet']}")
                if 'date' in result:
                    results.append(f"   Date: {result['date']}")
        
        # Related searches
        if 'relatedSearches' in data:
            results.append("\n[RELATED SEARCHES]:")
            for related in data['relatedSearches'][:5]:
                results.append(f"- {related.get('query', '')}")
        
        # News results (if available)
        if 'news' in data:
            results.append("\n[NEWS RESULTS]:")
            for news in data['news'][:3]:
                results.append(f"- {news.get('title', 'No title')}")
                results.append(f"  Source: {news.get('source', 'Unknown')}")
                results.append(f"  Date: {news.get('date', 'Unknown')}")
                results.append(f"  URL: {news.get('link', 'No URL')}")
                results.append("")
        
        return "\n".join(results)

class AlternativeSearchTool(BaseTool):
    """Alternative search tool using DuckDuckGo or other free APIs"""
    
    description = 'Search the web using alternative search engines when Google Search is not available.'
    parameters = [
        {
            'name': 'query',
            'type': 'string',
            'description': 'The search query to execute',
            'required': True
        }
    ]
    
    def __init__(self):
        super().__init__()
    
    def call(self, params: Dict, **kwargs) -> str:
        """
        Execute alternative search
        
        Args:
            params: Search parameters
            
        Returns:
            Formatted search results
        """
        query = params.get('query', '')
        
        if not query:
            return "Error: Search query is required"
        
        try:
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params_ddg = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params_ddg, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return self._format_ddg_results(data, query)
            
        except Exception as e:
            return f"Search temporarily unavailable: {str(e)}"
    
    def _format_ddg_results(self, data: Dict, query: str) -> str:
        """Format DuckDuckGo results"""
        results = []
        results.append(f"Search Results for: {query}")
        results.append("=" * 50)
        
        # Abstract (main answer)
        if data.get('Abstract'):
            results.append(f"\n[SUMMARY]:")
            results.append(data['Abstract'])
            if data.get('AbstractURL'):
                results.append(f"Source: {data['AbstractURL']}")
        
        # Definition
        if data.get('Definition'):
            results.append(f"\n[DEFINITION]:")
            results.append(data['Definition'])
            if data.get('DefinitionURL'):
                results.append(f"Source: {data['DefinitionURL']}")
        
        # Related topics
        if data.get('RelatedTopics'):
            results.append(f"\n[RELATED TOPICS]:")
            for topic in data['RelatedTopics'][:5]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append(f"- {topic['Text']}")
                    if 'FirstURL' in topic:
                        results.append(f"  URL: {topic['FirstURL']}")
        
        # Answer (direct answer)
        if data.get('Answer'):
            results.append(f"\n[DIRECT ANSWER]:")
            results.append(data['Answer'])
        
        if not any([data.get('Abstract'), data.get('Definition'), data.get('Answer')]):
            results.append("\nNo direct results found. Try a more specific query or use web_visit to explore specific websites.")
        
        return "\n".join(results)

# Factory function to create appropriate search tool
def create_search_tool(google_api_key: Optional[str] = None) -> BaseTool:
    """
    Create appropriate search tool based on available API keys
    
    Args:
        google_api_key: Google/Serper API key
        
    Returns:
        Search tool instance
    """
    if google_api_key:
        return GoogleSearchTool(google_api_key)
    else:
        return AlternativeSearchTool()
