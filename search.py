"""
Web Search Module - Enhanced Version
Handles searching with fallback strategies and result processing
"""


import os
import json
import re
import html
import urllib.parse
import concurrent.futures
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()


def get_env_or_secret(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


class SearchEngine:
    """
    Multi-strategy search engine with fallbacks
    """
    
    def __init__(self):
        """Initialize search engines"""
        self.serper_api_key = get_env_or_secret("SERPER_API_KEY")
        self.google_api_key = get_env_or_secret("GOOGLE_API_KEY")
        self.google_cse_id = get_env_or_secret("GOOGLE_CSE_ID")
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
    
    def search_with_wikipedia(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Reliable open-encyclopedia fallback search using Wikipedia API.
        Does not require any API keys and works even when search engines block scraping.
        """
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": 1,
                "srlimit": num_results
            }
            headers = {"User-Agent": "AIPRA-ResearchAgent/1.0"}
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return []
            
            data = response.json()
            items = data.get("query", {}).get("search", [])
            results = []
            
            for item in items:
                title = item.get("title", "")
                raw_snippet = item.get("snippet", "")
                clean_snippet = re.sub(r"<.*?>", "", html.unescape(raw_snippet)).strip()
                content = clean_snippet
                
                # Fetch summary extract for deeper evidence
                try:
                    slug = urllib.parse.quote(title)
                    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
                    sum_res = requests.get(summary_url, headers=headers, timeout=5)
                    if sum_res.status_code == 200:
                        extract = sum_res.json().get("extract", "")
                        if extract:
                            content = extract
                except Exception:
                    pass
                
                encoded_title = urllib.parse.quote(title.replace(" ", "_"))
                results.append({
                    "title": title,
                    "url": f"https://en.wikipedia.org/wiki/{encoded_title}",
                    "snippet": clean_snippet,
                    "content": content[:600],
                    "source": "wikipedia"
                })
            
            return results
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Multi-strategy search with fallbacks
        Priority: Serper > Google Custom Search > DuckDuckGo > Wikipedia
        """
        
        # Try Serper API first
        results = self.search_with_serper(query, max_results)
        if results:
            return results
        
        # Fallback to Google Custom Search
        results = self.search_with_google_custom(query, max_results)
        if results:
            return results
        
        # Fallback to DuckDuckGo
        results = self.search_with_duckduckgo(query, max_results)
        if results:
            return results
        
        # Reliable fallback to Wikipedia
        results = self.search_with_wikipedia(query, max_results)
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


def normalize_url(url: str) -> str:
    """Strip tracking params and normalize trailing slash for deduplication"""
    try:
        parsed = urllib.parse.urlparse(url)
        # Filter tracking query parameters
        clean_qs = [
            (k, v) for k, v in urllib.parse.parse_qsl(parsed.query)
            if not k.lower().startswith(("utm_", "ref", "fbclid", "gclid"))
        ]
        new_query = urllib.parse.urlencode(clean_qs)
        clean_path = parsed.path.rstrip("/")
        normalized = urllib.parse.urlunparse((parsed.scheme, parsed.netloc.lower(), clean_path, parsed.params, new_query, ""))
        return normalized or url
    except Exception:
        return url


def process_search_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Process, clean, and deduplicate search results
    """
    processed = []
    seen_urls = set()
    
    for result in results:
        raw_url = result.get("url", "").strip()
        if not raw_url:
            continue
        
        url = normalize_url(raw_url)
        if url in seen_urls:
            continue
        
        # Skip untrustworthy or social media aggregators that block scrapers
        if any(blocked in url.lower() for blocked in ["reddit.com/r/", "pinterest.com", "tiktok.com", "instagram.com"]):
            continue
        
        seen_urls.add(url)
        
        # Clean snippet
        snippet = result.get("snippet", "").strip()
        if snippet.endswith("..."):
            snippet = snippet[:-3].strip()
        
        processed.append({
            "title": result.get("title", "").strip() or "Untitled Source",
            "url": raw_url,
            "snippet": snippet,
            "content": result.get("content") or snippet,
            "source": result.get("source", "unknown"),
            "is_page_extracted": result.get("is_page_extracted", False)
        })
    
    return processed


def fetch_page_content(url: str, timeout: int = 5) -> str:
    """
    Fetch and clean text content from a web page using BeautifulSoup.
    Removes navigation, headers, footers, scripts, styles, and cookie notices.
    Returns cleaned article/body text up to 2,500 characters, or empty string on failure.
    """
    if not url or not url.startswith(("http://", "https://")):
        return ""
    
    lower_url = url.lower().split("?")[0]
    if lower_url.endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mp3", ".zip", ".tar", ".gz")):
        return ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if response.status_code != 200:
            return ""
        
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return ""
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove noisy non-content elements and boilerplate tables
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "svg", "iframe", "noscript", "dialog", "table"]):
            tag.decompose()
        
        # Strip common boilerplate layout classes (Wikipedia and news sidebars/infoboxes)
        for noise in soup.find_all(class_=["sidebar", "navbox", "infobox", "toc", "thumb", "metadata", "mw-editsection", "noprint", "mw-jump-link", "mw-empty-elt"]):
            noise.decompose()
        
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(" ", strip=True)
            # Filter short fragments and cookie/legal notices
            if len(text) > 50 and not any(kw in text.lower() for kw in ["cookie", "terms of", "privacy policy", "all rights reserved", "subscribe"]):
                paragraphs.append(text)
                if sum(len(p) for p in paragraphs) > 2800:
                    break
        
        if paragraphs:
            return "\n\n".join(paragraphs)[:2800]
        
        # Fallback to general article sections if <p> tags were minimal
        for sec in soup.find_all(["article", "section"]):
            text = sec.get_text(" ", strip=True)
            if len(text) > 80:
                return text[:2500]
        
        body_text = " ".join(soup.stripped_strings)
        return body_text[:2000] if len(body_text) > 60 else ""
        
    except Exception:
        return ""


def enrich_sources_with_content(sources: List[Dict[str, Any]], max_workers: int = 5, timeout: int = 5) -> List[Dict[str, Any]]:
    """
    Concurrently fetch real web page content for sources to provide rich substance for research.
    """
    def _fetch_one(source):
        # If content already has deep extract (e.g. Wikipedia summary extract), verify length
        existing = source.get("content", "")
        if existing and len(existing) > 500:
            source["is_page_extracted"] = True
            return source
        
        url = source.get("url", "")
        page_text = fetch_page_content(url, timeout=timeout)
        if page_text and len(page_text) > 120:
            source["content"] = page_text
            source["is_page_extracted"] = True
        else:
            source["content"] = source.get("snippet", "")
            source["is_page_extracted"] = False
        return source

    if not sources:
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(sources))) as executor:
        enriched = list(executor.map(_fetch_one, sources))
    return enriched



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