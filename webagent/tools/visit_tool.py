# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
from typing import Dict, Optional
from urllib.parse import urlparse, urljoin
from qwen_agent.tools.base import BaseTool, register_tool
import time
import re

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

@register_tool('web_visit')
class WebVisitTool(BaseTool):
    """Web page visit and content extraction tool for WebSailor agent"""
    
    description = 'Visit a web page and extract its content. Useful for reading articles, getting detailed information from specific websites.'
    parameters = [
        {
            'name': 'url',
            'type': 'string',
            'description': 'The URL of the web page to visit',
            'required': True
        },
        {
            'name': 'extract_type',
            'type': 'string',
            'description': 'Type of content to extract: "text" (default), "summary", or "structured"',
            'required': False
        }
    ]
    
    def __init__(self, jina_api_key: Optional[str] = None):
        """
        Initialize Web Visit tool
        
        Args:
            jina_api_key: Jina API key for content extraction
        """
        super().__init__()
        self.jina_api_key = jina_api_key
        self.jina_base_url = "https://r.jina.ai/"
        
    def call(self, params: Dict, **kwargs) -> str:
        """
        Visit a web page and extract content
        
        Args:
            params: Visit parameters
            
        Returns:
            Extracted content
        """
        url = params.get('url', '')
        extract_type = params.get('extract_type', 'text')
        
        if not url:
            return "Error: URL is required"
        
        # Validate URL
        if not self._is_valid_url(url):
            return f"Error: Invalid URL format: {url}"
        
        try:
            # Try Jina API first if available
            if self.jina_api_key:
                content = self._extract_with_jina(url, extract_type)
                if content:
                    return content
            
            # Fallback to direct HTTP request
            return self._extract_with_requests(url, extract_type)
            
        except Exception as e:
            return f"Error visiting {url}: {str(e)}"
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_with_jina(self, url: str, extract_type: str) -> Optional[str]:
        """Extract content using Jina API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.jina_api_key}',
                'Accept': 'application/json'
            }
            
            # Configure Jina based on extract type
            jina_url = self.jina_base_url + url
            if extract_type == 'summary':
                jina_url += '?summary=true'
            elif extract_type == 'structured':
                jina_url += '?format=structured'
            
            response = requests.get(jina_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                content = data['data']
                return self._format_jina_content(content, url, extract_type)
            else:
                return None
                
        except Exception as e:
            safe_print(f"Jina API error: {e}")
            return None
    
    def _extract_with_requests(self, url: str, extract_type: str) -> str:
        """Extract content using direct HTTP requests"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                return f"Content type not supported: {content_type}"
            
            html_content = response.text
            return self._extract_text_from_html(html_content, url, extract_type)
            
        except requests.exceptions.RequestException as e:
            return f"Error accessing {url}: {str(e)}"
    
    def _extract_text_from_html(self, html: str, url: str, extract_type: str) -> str:
        """Extract text content from HTML"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Get title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Extract main content
            main_content = self._find_main_content(soup)
            
            if extract_type == 'summary':
                return self._create_summary(title_text, main_content, url)
            elif extract_type == 'structured':
                return self._create_structured_content(soup, title_text, url)
            else:
                return self._create_text_content(title_text, main_content, url)
                
        except ImportError:
            # Fallback without BeautifulSoup
            return self._simple_text_extraction(html, url)
        except Exception as e:
            return f"Error parsing content from {url}: {str(e)}"
    
    def _find_main_content(self, soup):
        """Find main content area in HTML"""
        # Try common content selectors
        content_selectors = [
            'main', 'article', '[role="main"]', '.content', '.post-content',
            '.entry-content', '.article-content', '.main-content', '#content',
            '.post', '.article', '.story-body'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return content
        
        # Fallback to body
        return soup.find('body') or soup
    
    def _create_text_content(self, title: str, content_element, url: str) -> str:
        """Create formatted text content"""
        lines = [
            f"[WEB PAGE CONTENT]",
            f"URL: {url}",
            f"Title: {title}",
            "=" * 60,
            ""
        ]
        
        if content_element:
            # Extract paragraphs and headings
            for element in content_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                text = element.get_text().strip()
                if text and len(text) > 10:  # Filter out very short text
                    if element.name.startswith('h'):
                        lines.append(f"\n## {text}")
                    elif element.name == 'li':
                        lines.append(f"• {text}")
                    else:
                        lines.append(f"{text}")
                        lines.append("")
        
        # Limit content length
        content = "\n".join(lines)
        if len(content) > 8000:
            content = content[:8000] + "\n\n[Content truncated due to length...]"
        
        return content
    
    def _create_summary(self, title: str, content_element, url: str) -> str:
        """Create a summary of the content"""
        lines = [
            f"[WEB PAGE SUMMARY]",
            f"URL: {url}",
            f"Title: {title}",
            "=" * 60,
            ""
        ]
        
        if content_element:
            # Extract first few paragraphs and key headings
            paragraphs = content_element.find_all('p')[:3]
            headings = content_element.find_all(['h1', 'h2', 'h3'])[:5]
            
            if headings:
                lines.append("Key Topics:")
                for heading in headings:
                    text = heading.get_text().strip()
                    if text:
                        lines.append(f"• {text}")
                lines.append("")
            
            if paragraphs:
                lines.append("Summary:")
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 20:
                        lines.append(text)
                        lines.append("")
        
        return "\n".join(lines)
    
    def _create_structured_content(self, soup, title: str, url: str) -> str:
        """Create structured content extraction"""
        lines = [
            f"[STRUCTURED CONTENT]",
            f"URL: {url}",
            f"Title: {title}",
            "=" * 60,
            ""
        ]
        
        # Extract metadata
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            lines.append(f"Description: {meta_description.get('content', '')}")
            lines.append("")
        
        # Extract headings structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        if headings:
            lines.append("Content Structure:")
            for heading in headings:
                level = int(heading.name[1])
                indent = "  " * (level - 1)
                text = heading.get_text().strip()
                if text:
                    lines.append(f"{indent}• {text}")
            lines.append("")
        
        # Extract key information
        lists = soup.find_all(['ul', 'ol'])
        if lists:
            lines.append("Key Points:")
            for lst in lists[:2]:  # Limit to first 2 lists
                for li in lst.find_all('li')[:5]:  # Limit to 5 items per list
                    text = li.get_text().strip()
                    if text:
                        lines.append(f"• {text}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _simple_text_extraction(self, html: str, url: str) -> str:
        """Simple text extraction without BeautifulSoup"""
        # Remove HTML tags using regex
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "No title"
        
        lines = [
            f"[WEB PAGE CONTENT (Simple Extraction)]",
            f"URL: {url}",
            f"Title: {title}",
            "=" * 60,
            "",
            text[:5000] + ("..." if len(text) > 5000 else "")
        ]
        
        return "\n".join(lines)
    
    def _format_jina_content(self, content: Dict, url: str, extract_type: str) -> str:
        """Format content from Jina API response"""
        lines = [
            f"[WEB PAGE CONTENT (Jina API)]",
            f"URL: {url}",
            f"Title: {content.get('title', 'No title')}",
            "=" * 60,
            ""
        ]
        
        if extract_type == 'summary' and 'summary' in content:
            lines.append("Summary:")
            lines.append(content['summary'])
        elif 'content' in content:
            lines.append(content['content'])
        elif 'text' in content:
            lines.append(content['text'])
        
        return "\n".join(lines)

class AlternativeWebVisitTool(BaseTool):
    """Alternative web visit tool for when Jina is not available"""
    
    description = 'Visit web pages and extract content using alternative methods.'
    parameters = [
        {
            'name': 'url',
            'type': 'string',
            'description': 'The URL of the web page to visit',
            'required': True
        }
    ]
    
    def __init__(self):
        super().__init__()
    
    def call(self, params: Dict, **kwargs) -> str:
        """Visit web page using alternative method"""
        url = params.get('url', '')
        
        if not url:
            return "Error: URL is required"
        
        try:
            # Use a simple HTTP request with text extraction
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; WebSailor/1.0)'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Simple text extraction
            content = response.text
            
            # Remove HTML tags
            import re
            text = re.sub(r'<[^>]+>', ' ', content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Limit length
            if len(text) > 3000:
                text = text[:3000] + "..."
            
            return f"Content from {url}:\n\n{text}"
            
        except Exception as e:
            return f"Error visiting {url}: {str(e)}"

# Factory function to create appropriate visit tool
def create_visit_tool(jina_api_key: Optional[str] = None) -> BaseTool:
    """
    Create appropriate web visit tool based on available API keys
    
    Args:
        jina_api_key: Jina API key
        
    Returns:
        Web visit tool instance
    """
    if jina_api_key:
        return WebVisitTool(jina_api_key)
    else:
        return AlternativeWebVisitTool()
