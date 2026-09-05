"""
Web Search Module - Enhanced Version
Handles searching with fallback strategies and result processing
"""


import os
import json
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
load_dotenv()


class SearchEngine:
    """
    Multi-strategy search engine with fallbacks
    """
    
    def __init__(self):
        """Initialize search engines"""
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.timeout = 10
    
    def search_with_serper(self, query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """
        Search using Serper API (recommended for production)
        """
        if not self.serper_api_key:
            return []
        
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": query,
                "num": num_results,
                "autocorrect": True,
                "page": 1
            })
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, data=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Process organic results
                for item in data.get("organic", [])[:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "serper"
                    })
                
                return results
        
        except Exception as e:
            print(f"Serper API error: {e}")
        
        return []
    
    def search_with_google_custom(self, query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """
        Search using Google Custom Search API
        """
        if not self.google_api_key or not self.google_cse_id:
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": query,
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "num": min(10, num_results)
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("items", [])[:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google_cse"
                    })
                
                return results
        
        except Exception as e:
            print(f"Google Custom Search error: {e}")
        
        return []
    
    def search_with_duckduckgo(self, query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """
        Fallback search using DuckDuckGo (no API key needed)
        """
        try:
            # Using duckduckgo-search library (add to requirements)
            from duckduckgo_search import DDGS
            
            with DDGS(timeout=self.timeout) as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
                
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "source": "duckduckgo"
                    })
                
                return formatted_results
        
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
        
        return []
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Multi-strategy search with fallbacks
        Priority: Serper > Google Custom Search > DuckDuckGo
        """
        
        # Try Serper API first
        results = self.search_with_serper(query, max_results)
        if results:
            return results
        
        # Fallback to Google Custom Search
        results = self.search_with_google_custom(query, max_results)
        if results:
            return results
        
        # Final fallback to DuckDuckGo
        results = self.search_with_duckduckgo(query, max_results)
        if results:
            return results
        
        # If all fail, return empty results
        print(f"Warning: No search results found for '{query}'")
        return []


# Global search engine instance
_search_engine = None


def get_search_engine() -> SearchEngine:
    """Get or create search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine


def search_web(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Simple interface for web search
    """
    engine = get_search_engine()
    return engine.search(query, max_results)


def process_search_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Process and clean search results
    """
    processed = []
    seen_urls = set()
    
    for result in results:
        url = result.get("url", "").strip()
        
        # Skip duplicates and invalid URLs
        if not url or url in seen_urls:
            continue
        
        # Skip untrustworthy domains (optional)
        if any(blocked in url.lower() for blocked in ["reddit.com/r/", "pinterest.com"]):
            continue
        
        seen_urls.add(url)
        
        # Clean snippet
        snippet = result.get("snippet", "").strip()
        if snippet.endswith("..."):
            snippet = snippet[:-3].strip()
        
        processed.append({
            "title": result.get("title", "").strip(),
            "url": url,
            "snippet": snippet,
            "source": result.get("source", "unknown")
        })
    
    return processed


# Example usage
if __name__ == "__main__":
    test_query = "artificial intelligence latest developments 2026"
    
    print(f"Searching for: {test_query}\n")
    results = search_web(test_query, max_results=5)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Source: {result['source']}")
        print(f"   {result['snippet'][:100]}...\n")