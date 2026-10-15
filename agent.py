"""
AI Personal Research Agent - Enhanced Version
Coordinates research planning, web search, page extraction, and comprehensive synthesis.
"""

import re
from typing import Dict, List, Any
from llm import create_research_plan, analyze_sources, generate_summary
from search import search_web, enrich_sources_with_content, normalize_url


def run_research_agent(question: str, depth: str = "Standard", num_sources: int = 6) -> Dict[str, Any]:
    """
    Main research orchestration function.
    
    Args:
        question: User's research question
        depth: Research depth ("Quick Overview", "Standard", "Deep Analysis")
        num_sources: Target number of sources to retrieve
    
    Returns:
        Dictionary with executive summary, key findings, detailed analysis,
        source comparison, conclusion, and verified sources.
    """
    
    # 1. Determine parameters based on depth
    depth_config = {
        "Quick Overview": {
            "queries": 2,
            "sources_per_query": 3,
            "sources_target": 4,
            "findings_target": 4
        },
        "Standard": {
            "queries": 3,
            "sources_per_query": max(num_sources, 6),
            "sources_target": max(num_sources, 6),
            "findings_target": 6
        },
        "Deep Analysis": {
            "queries": 5,
            "sources_per_query": min(max(num_sources + 2, 8), 10),
            "sources_target": min(max(num_sources + 2, 8), 10),
            "findings_target": 8
        }
    }
    
    config = depth_config.get(depth, depth_config["Standard"])
    
    # Step 1: Create research plan
    research_plan = create_research_plan(question, num_queries=config["queries"], depth=depth)
    search_queries = research_plan.get("queries", [question])
    
    # Step 2: Gather candidate sources from web search
    candidate_sources = []
    seen_urls = set()
    
    for query in search_queries:
        try:
            results = search_web(query, max_results=config["sources_per_query"])
            for result in results:
                raw_url = result.get("url", "").strip()
                if not raw_url:
                    continue
                
                normalized = normalize_url(raw_url)
                if normalized not in seen_urls:
                    seen_urls.add(normalized)
                    candidate_sources.append({
                        "title": result.get("title", "Untitled Source").strip(),
                        "url": raw_url,
                        "snippet": result.get("snippet", "").strip(),
                        "content": result.get("content") or result.get("snippet", "").strip(),
                        "source": result.get("source", "web"),
                        "is_page_extracted": result.get("is_page_extracted", False)
                    })
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            continue

    # Cap candidate sources to target
    target_count = config["sources_target"]
    selected_sources = candidate_sources[:target_count]

    # Step 3: Enrich candidate sources with real web page content via BeautifulSoup
    if selected_sources:
        try:
            enriched_sources = enrich_sources_with_content(selected_sources, max_workers=5, timeout=4)
        except Exception as e:
            print(f"Error enriching sources with page content: {e}")
            enriched_sources = selected_sources
    else:
        enriched_sources = []

    # Step 4: Multi-section analysis and synthesis
    synthesis_result = analyze_sources(question, enriched_sources, depth=depth)
    
    # Extract components from synthesis
    if isinstance(synthesis_result, dict):
        summary = synthesis_result.get("summary", "")
        findings = synthesis_result.get("findings", [])
        detailed_analysis = synthesis_result.get("detailed_analysis", "")
        source_comparison = synthesis_result.get("source_comparison", "")
        conclusion = synthesis_result.get("conclusion", "")
        report = synthesis_result.get("report", "")
    else:
        report = str(synthesis_result)
        summary = generate_summary(report, max_length=1500)
        findings = extract_findings_from_report(report, enriched_sources)
        detailed_analysis = report
        source_comparison = "Comparative analysis generated across retrieved sources."
        conclusion = f"Research concluded with {len(enriched_sources)} evidence sources."

    # Validate findings is never empty when sources exist
    if not findings and enriched_sources:
        findings = extract_findings_from_report(report, enriched_sources)

    # Format findings for presentation
    clean_findings = []
    for f in findings:
        if isinstance(f, dict):
            clean_findings.append(f.get("display") or f.get("text") or str(f))
        else:
            clean_findings.append(str(f))

    # Prepare final result
    result = {
        "query": question,
        "summary": summary,
        "findings": clean_findings,
        "raw_findings": findings,
        "detailed_analysis": detailed_analysis,
        "source_comparison": source_comparison,
        "conclusion": conclusion,
        "sources": enriched_sources,
        "total_sources": len(enriched_sources),
        "findings_count": len(clean_findings),
        "report": report,
        "depth": depth,
        "search_queries_used": search_queries
    }
    
    return result


async def run_research_agent_async(question: str, depth: str = "Standard", num_sources: int = 6) -> Dict[str, Any]:
    """
    Asynchronous compatibility wrapper for research agent.
    """
    return run_research_agent(question, depth, num_sources)


def extract_findings_from_report(report: str, sources: List[Dict[str, Any]] = None) -> List[str]:
    """
    Extract distinct key findings from the report markdown with guaranteed fallback.
    """
    findings = []
    
    # 1. Look specifically within Key Findings section
    if "## Key Findings" in report:
        findings_sec = report.split("## Key Findings", 1)[1]
        next_sec = re.split(r"\n##\s+", findings_sec)[0]
        lines = findings_sec.splitlines()
    else:
        lines = report.splitlines()

    current_finding = []
    
    for line in lines:
        stripped = line.strip()
        
        # Stop if we hit the next major markdown header
        if stripped.startswith("## ") and current_finding:
            break

        # Match bullet points or numbered lists
        bullet_match = re.match(r"^(?:[-*•]\s+|\d+[\.)]\s+)(.+)$", stripped)
        if bullet_match:
            if current_finding:
                text = " ".join(current_finding).strip()
                if len(text) > 20:
                    findings.append(text)
                current_finding = []
            current_finding.append(bullet_match.group(1).strip())
        elif current_finding:
            if stripped and not stripped.startswith("#"):
                current_finding.append(stripped)
            else:
                text = " ".join(current_finding).strip()
                if len(text) > 20:
                    findings.append(text)
                current_finding = []

    if current_finding:
        text = " ".join(current_finding).strip()
        if len(text) > 20:
            findings.append(text)

    # Format markdown bold labels: **Label**: to <strong>Label</strong>:
    formatted_findings = []
    for f in findings:
        formatted = re.sub(r"\*\*(.*?)\*\*[:\-]?\s*", r"<strong>\1</strong>: ", f)
        # Style citations [1], [2]
        formatted = re.sub(r"\[(\d+)\]", r"<span style='color:#5f8fff; font-weight:600;'>[\1]</span>", formatted)
        formatted_findings.append(formatted)

    # Guaranteed fallback: if parsing yielded 0 findings but sources are present
    if not formatted_findings and sources:
        for idx, s in enumerate(sources[:6], 1):
            title = s.get("title", f"Source {idx}")
            snippet = s.get("content") or s.get("snippet") or ""
            clean_s = snippet.strip()
            if clean_s:
                sentence = clean_s.split(".")[0].strip()
                if len(sentence) > 30:
                    formatted_findings.append(
                        f"<strong>{title}</strong>: {sentence}. <span style='color:#5f8fff; font-weight:600;'>[{idx}]</span>"
                    )

    return formatted_findings


def validate_research_result(result: Dict[str, Any]) -> bool:
    """
    Validate research result completeness.
    """
    required_fields = ["query", "summary", "findings", "sources"]
    return all(field in result and result[field] is not None for field in required_fields)


if __name__ == "__main__":
    test_query = "What is artificial intelligence and its key mechanisms?"
    print(f"Running test research on: {test_query}\n")
    res = run_research_agent(test_query, depth="Standard", num_sources=6)
    print("=" * 80)
    print(f"SUMMARY:\n{res['summary']}\n")
    print(f"FINDINGS ({len(res['findings'])}):")
    for i, f in enumerate(res['findings'], 1):
        print(f"  {i}. {f}\n")
    print(f"SOURCES ({len(res['sources'])}):")
    for i, s in enumerate(res['sources'], 1):
        extracted_flag = "PAGE" if s.get("is_page_extracted") else "SNIPPET"
        print(f"  {i}. [{extracted_flag}] {s['title']} -> {s['url']}")