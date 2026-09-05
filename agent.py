"""

AI Personal Research Agent - Enhanced Version
Coordinates research planning, searching, and analysis
"""

import asyncio
from typing import Dict, List, Any
from llm import create_research_plan, analyze_sources, generate_summary
from search import search_web


async def run_research_agent_async(question: str, depth: str = "Standard", num_sources: int = 6) -> Dict[str, Any]:
    """
    Main research orchestration function (async version for better performance)
    
    Args:
        question: User's research question
        depth: Research depth ("Quick Overview", "Standard", "Deep Analysis")
        num_sources: Number of sources to retrieve
    
    Returns:
        Dictionary with research findings, sources, and summary
    """
    
    # Determine search parameters based on depth
    depth_config = {
        "Quick Overview": {"queries": 2, "sources_per_query": 3},
        "Standard": {"queries": 3, "sources_per_query": num_sources},
        "Deep Analysis": {"queries": 5, "sources_per_query": min(num_sources + 2, 10)}
    }
    
    config = depth_config.get(depth, depth_config["Standard"])
    
    # Step 1: Create research plan
    research_plan = create_research_plan(question, num_queries=config["queries"])
    search_queries = research_plan.get("queries", [question])
    
    # Step 2: Gather sources from web search
    all_sources = []
    
    seen_urls = set()
    
    for query in search_queries:
        try:
            search_results = search_web(query, max_results=config["sources_per_query"])
            
            for result in search_results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_sources.append({
                        "title": result.get("title", "Untitled"),
                        "url": url,
                        "snippet": result.get("snippet", ""),
                        "content": result.get("snippet", "")[:600]
                    })
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            continue
    
    # Limit to requested number of sources
    all_sources = all_sources[:num_sources]
    
    # Step 3: Analyze sources and generate report
    report = analyze_sources(question, all_sources)
    
    # Step 4: Generate summary
    summary = generate_summary(report, max_length=300)
    
    # Step 5: Extract findings from report
    findings = extract_findings_from_report(report)
    
    # Prepare result
    result = {
        "query": question,
        "summary": summary,
        "findings": findings,
        "sources": all_sources[:6],  # Return top 6 sources for display
        "total_sources": len(all_sources),
        "report": report,
        "depth": depth,
        "search_queries_used": search_queries
    }
    
    return result


def run_research_agent(question: str, depth: str = "Standard", num_sources: int = 6) -> Dict[str, Any]:
    """
    Synchronous wrapper for research agent
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(run_research_agent_async(question, depth, num_sources))


def extract_findings_from_report(report: str) -> List[str]:
    """
    Extract key findings from the research report
    """
    findings = []
    
    # Split by bullet points or numbered lists
    lines = report.split('\n')
    current_finding = []
    
    for line in lines:
        line = line.strip()
        
        # Skip headers and empty lines
        if not line or line.startswith('#'):
            if current_finding:
                finding_text = ' '.join(current_finding).strip()
                if finding_text and len(finding_text) > 20:
                    findings.append(finding_text)
                current_finding = []
            continue
        
        # Detect bullet points and numbered items
        if any(line.startswith(x) for x in ['-', '•', '*', '1.', '2.', '3.']):
            line = line.lstrip('-•* 0123456789.').strip()
            if line:
                current_finding.append(line)
        elif current_finding:
            current_finding.append(line)
    
    # Add remaining finding
    if current_finding:
        finding_text = ' '.join(current_finding).strip()
        if finding_text and len(finding_text) > 20:
            findings.append(finding_text)
    
    # Return top 5 findings, each limited to 250 chars
    return [f[:250] for f in findings[:5] if f]


def validate_research_result(result: Dict[str, Any]) -> bool:
    """
    Validate research result completeness
    """
    required_fields = ["query", "summary", "findings", "sources"]
    return all(field in result for field in required_fields)


# Example usage
if __name__ == "__main__":
    # Test the research agent
    test_query = "What are the latest developments in artificial intelligence?"
    result = run_research_agent(test_query, depth="Standard")
    
    print("=" * 80)
    print("RESEARCH RESULTS")
    print("=" * 80)
    print(f"Query: {result['query']}")
    print(f"\nSummary:\n{result['summary']}\n")
    print(f"Findings ({len(result['findings'])}):")
    for i, finding in enumerate(result['findings'], 1):
        print(f"  {i}. {finding}\n")
    print(f"Sources ({len(result['sources'])}):")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source['title']}")
        print(f"     {source['url']}\n")