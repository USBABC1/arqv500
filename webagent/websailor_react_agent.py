# -*- coding: utf-8 -*-
import os
import sys
import json
from typing import Dict, List, Optional, Union, Iterator
import copy
from openai import OpenAI
import tiktoken

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

MAX_LLM_CALL_PER_RUN = int(os.getenv("MAX_LLM_CALL_PER_RUN", 40))
MAX_TOKEN_LENGTH = int(os.getenv("MAX_LENGTH", 31 * 1024 - 500))

safe_print(f"Running with MAX_LLM_CALL_PER_RUN = {MAX_LLM_CALL_PER_RUN}")

class Message:
    def __init__(self, role: str, content: str = None, function_call: Dict = None, name: str = None):
        self.role = role
        self.content = content
        self.function_call = function_call
        self.name = name

    def dict(self):
        return {"role": self.role, "content": self.content, "function_call": self.function_call, "name": self.name}

class MultiTurnReactAgent:
    def __init__(self,
                 function_list: Optional[List[Union[str, Dict]]] = None,
                 llm: Optional[OpenAI] = None,
                 system_message: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 files: Optional[List[str]] = None,
                 **kwargs):
        self.function_list = function_list
        self.llm = llm
        self.system_message = system_message
        self.name = name
        self.description = description
        self.files = files
        self.kwargs = kwargs

    def _run(self, messages: List[Message], lang: str = 'en', **kwargs) -> Iterator[List[Message]]:
        # This is a simplified placeholder for the original _run method.
        # The actual implementation would involve complex LLM calls and tool execution.
        yield [Message(role='assistant', content='This is a simplified run method for demonstration purposes.')]

    def _need_truncate_messages(self, messages: List[Message]) -> bool:
        # Simplified truncation check
        text = " ".join([msg.content for msg in messages if msg.content])
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens) > MAX_TOKEN_LENGTH

    def _truncate_messages(self, messages: List[Message]) -> List[Message]:
        # Simplified truncation
        if len(messages) <= 3:
            return messages
        truncated = [messages[0]]
        for i in range(len(messages) - 1, 0, -1):
            test_messages = [messages[0]] + messages[i:]
            if not self._need_truncate_messages(test_messages):
                truncated = test_messages
                break
        return truncated

class WebSailorAgent:
    """WebSailor Agent for web navigation and information seeking"""
    
    def __init__(self, 
                 model_path: str = None,
                 api_key: str = None,
                 base_url: str = None,
                 google_search_key: str = None,
                 jina_api_key: str = None):
        """
        Initialize WebSailor Agent
        
        Args:
            model_path: Path to local model or model name
            api_key: API key for remote model
            base_url: Base URL for API
            google_search_key: Google search API key
            jina_api_key: Jina API key for web content extraction
        """
        self.model_path = model_path
        self.api_key = api_key
        self.base_url = base_url
        self.google_search_key = google_search_key
        self.jina_api_key = jina_api_key
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize agent
        self.agent = MultiTurnReactAgent(
            function_list=self.tools,
            llm=self.llm,
            system_message=self._get_system_message()
        )
    
    def _initialize_tools(self) -> List[object]: # Changed BaseTool to object
        """Initialize web navigation tools"""
        from services.tools.search_tool import GoogleSearchTool
        from services.tools.visit_tool import WebVisitTool
        
        tools = []
        
        if self.google_search_key:
            tools.append(GoogleSearchTool(api_key=self.google_search_key))
        
        if self.jina_api_key:
            tools.append(WebVisitTool(jina_api_key=self.jina_api_key))
        
        return tools
    
    def _initialize_llm(self):
        """Initialize the language model"""
        if self.model_path and os.path.exists(self.model_path):
            # Local model
            safe_print("Warning: Local model path provided, but qwen_agent is not used. Using OpenAI client.")
            self.llm = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        elif self.api_key and self.base_url:
            # Remote API
            self.llm = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            raise ValueError("Either model_path or (api_key + base_url) must be provided")

    def _get_system_message(self) -> str:
        """Get system message for WebSailor agent"""
        return """You are WebSailor, an advanced web navigation agent designed for complex information seeking tasks.

Your capabilities include:
1. Searching the web using Google Search
2. Visiting and extracting content from web pages
3. Reasoning through complex, multi-step information gathering tasks
4. Handling uncertainty and exploring multiple paths to find answers

When given a task:
1. Break it down into smaller, manageable steps
2. Use search to find relevant information
3. Visit promising web pages to gather detailed information
4. Synthesize information from multiple sources
5. Provide comprehensive, well-reasoned answers

Always think step by step and explain your reasoning process.
Be thorough but efficient in your information gathering.
If you encounter uncertainty, explore multiple angles before concluding.

Available tools:
- google_search: Search the web for information
- web_visit: Visit and extract content from web pages

Use these tools strategically to complete complex information seeking tasks."""

    def search_and_analyze(self, query: str, max_iterations: int = 10) -> Dict:
        """
        Perform web search and analysis using WebSailor methodology
        
        Args:
            query: The search query or task description
            max_iterations: Maximum number of iterations
            
        Returns:
            Dict containing the analysis results
        """
        messages = [
            Message(role='user', content=f"""
Please help me with the following task: {query}

Use your web search and navigation capabilities to gather comprehensive information.
Think step by step and provide a detailed analysis based on your findings.
"""
            )
        ]
        
        results = []
        iteration_count = 0
        
        try:
            for response in self.agent._run(messages):
                if response:
                    results.extend(response)
                    messages.extend(response)
                    
                iteration_count += 1
                if iteration_count >= max_iterations:
                    break
                    
                # Check if agent has provided a final answer
                if response and response[-1].role == 'assistant' and not response[-1].function_call:
                    break
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': results
            }
        
        # Extract final answer
        final_answer = ""
        search_results = []
        visited_pages = []
        
        for msg in results:
            if msg.role == 'assistant' and not msg.function_call:
                final_answer = msg.content
            elif msg.role == 'function':
                if msg.name == 'google_search':
                    search_results.append(msg.content)
                elif msg.name == 'web_visit':
                    visited_pages.append(msg.content)
        
        return {
            'success': True,
            'final_answer': final_answer,
            'search_results': search_results,
            'visited_pages': visited_pages,
            'total_iterations': iteration_count,
            'full_conversation': [msg.dict() for msg in results]
        }
    
    def quick_search(self, query: str) -> str:
        """
        Perform a quick search and return summarized results
        
        Args:
            query: Search query
            
        Returns:
            Summarized search results
        """
        result = self.search_and_analyze(query, max_iterations=5)
        
        if result['success']:
            return result['final_answer']
        else:
            return f"Error: {result['error']}"

# Simplified interface for integration
class WebSailorService:
    """Simplified WebSailor service for integration with ARQV30"""
    
    def __init__(self, config: Dict):
        """
        Initialize WebSailor service
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """
        Initialize the WebSailor agent
        """
        try:
            self.agent = WebSailorAgent(
                api_key=self.config.get('api_key'),
                base_url=self.config.get('base_url'),
                google_search_key=self.config.get('google_search_key'),
                jina_api_key=self.config.get('jina_api_key')
            )
        except Exception as e:
            safe_print(f"Warning: Failed to initialize WebSailor agent: {e}")
            self.agent = None
    
    def is_available(self) -> bool:
        """
        Check if WebSailor is available
        """
        return self.agent is not None
    
    def perform_research(self, query: str, context: Dict = None) -> Dict:
        """
        Perform research using WebSailor
        
        Args:
            query: Research query
            context: Additional context for the research
            
        Returns:
            Research results
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'WebSailor agent not available',
                'results': None
            }
        
        # Enhance query with context if provided
        enhanced_query = query
        if context:
            context_str = json.dumps(context, indent=2)
            enhanced_query = f"""
Research Query: {query}

Additional Context:
{context_str}

Please conduct thorough research considering this context and provide comprehensive insights.
"""
        
        try:
            result = self.agent.search_and_analyze(enhanced_query)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': None
            }
    
    def quick_fact_check(self, statement: str) -> str:
        """
        Quick fact checking using WebSailor
        
        Args:
            statement: Statement to fact-check
            
        Returns:
            Fact-check result
        """
        if not self.is_available():
            return "WebSailor not available for fact-checking"
        
        query = f"Please fact-check the following statement and provide evidence: {statement}"
        return self.agent.quick_search(query)
    
    def market_research(self, topic: str, region: str = "Brazil") -> Dict:
        """
        Perform market research using WebSailor
        
        Args:
            topic: Market research topic
            region: Geographic region for research
            
        Returns:
            Market research results
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'WebSailor not available',
                'results': None
            }
        
        query = f"""
Conduct comprehensive market research on: {topic}
Geographic focus: {region}

Please provide:
1. Market size and trends
2. Key players and competitors
3. Consumer behavior insights
4. Growth opportunities
5. Challenges and risks
6. Recent developments and news

Use current data and multiple reliable sources.
"""
        
        return self.perform_research(query)
