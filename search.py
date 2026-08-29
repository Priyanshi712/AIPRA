import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 5) -> list:
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=max_results, include_answer=True)
        results = []
        for result in response.get("results", []):
            results.append({"title": result.get("title", ""), "url": result.get("url", ""), "content": result.get("content", ""), "score": result.get("score", 0)})
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

def search_multiple_queries(queries: list, max_results: int = 5) -> list:
    all_sources = []
    seen_urls = set()
    for query in queries:
        results = search_web(query, max_results)
        for result in results:
            url = result.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_sources.append(result)
    return all_sources