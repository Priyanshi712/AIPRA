"""
Comprehensive Test Suite for AIPRA Research Engine
Tests:
1. Basic Question: "What is artificial intelligence?"
2. Multi-perspective Question: "Open source vs closed source AI models"
3. Empty / Failed Search Results
4. Malformed LLM Output / API Fallback
5. Finding Count Verification & displayed findings consistency
6. Citations mapping to real retrieved sources
7. Quick Overview vs Standard vs Deep Analysis differentiation
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, r"c:\Users\priya\OneDrive\Desktop\AIPRA")

from agent import run_research_agent, extract_findings_from_report
from llm import parse_llm_research_report, extractive_analyze_sources, clean_source_snippet
from search import fetch_page_content, normalize_url, process_search_results

def test_empty_search():
    print("--- Test 1: Empty / Failed Search Results ---")
    res = extractive_analyze_sources("xyznonexistenttopic99999", [])
    assert res["findings"] == [], "Empty sources should yield empty findings list"
    assert "No verified external sources were retrieved" in res["summary"]
    print("PASS: Empty search handled gracefully.")

def test_malformed_llm_output():
    print("\n--- Test 2: Malformed LLM Output & Parsing Fallback ---")
    mock_sources = [
        {"title": "Quantum Supremacy", "url": "https://example.com/quantum", "snippet": "Quantum supremacy is the milestone where a quantum computer solves a problem classical computers cannot in reasonable time.", "content": "Quantum supremacy is the milestone where a quantum computer solves a problem classical computers cannot in reasonable time."}
    ]
    # Garbage output without headers
    garbage_output = "I am an AI and I don't follow markdown templates. Just rambling text here."
    parsed = parse_llm_research_report(garbage_output, mock_sources, "Quantum computing milestone", depth="Quick Overview")
    assert len(parsed["findings"]) > 0, f"Expected fallback findings, got {len(parsed['findings'])}"
    assert parsed["findings"][0]["title"] == "Quantum Supremacy"
    print(f"PASS: Malformed LLM output fell back to {len(parsed['findings'])} reliable findings.")

def test_citation_mapping():
    print("\n--- Test 3: Citation Mapping & URL Normalization ---")
    url1 = "https://example.com/article?utm_source=twitter&utm_medium=social"
    url2 = "https://example.com/article"
    assert normalize_url(url1) == normalize_url(url2), "Normalized URLs must match regardless of tracking parameters"
    
    mock_sources = [
        {"title": "Source Alpha", "url": "https://alpha.org", "snippet": "Alpha is a framework for distributed computing.", "content": "Alpha is a framework for distributed computing."},
        {"title": "Source Beta", "url": "https://beta.org", "snippet": "Beta provides consensus algorithms for distributed nodes.", "content": "Beta provides consensus algorithms for distributed nodes."}
    ]
    res = extractive_analyze_sources("Distributed frameworks", mock_sources, depth="Standard")
    assert len(res["findings"]) >= 2
    for f in res["findings"]:
        assert "source_ids" in f and len(f["source_ids"]) > 0
        assert f["source_ids"][0] in [1, 2]
    print("PASS: Citations correctly map to source indices.")

def test_depth_differentiation():
    print("\n--- Test 4: Quick Overview vs Standard vs Deep Analysis Differentiation ---")
    res_quick = run_research_agent("What is machine learning?", depth="Quick Overview")
    res_standard = run_research_agent("What is machine learning?", depth="Standard")
    
    print(f"Quick Overview: {res_quick['total_sources']} sources, {len(res_quick['findings'])} findings, {len(res_quick['search_queries_used'])} search queries")
    print(f"Standard: {res_standard['total_sources']} sources, {len(res_standard['findings'])} findings, {len(res_standard['search_queries_used'])} search queries")
    
    assert len(res_quick["search_queries_used"]) == 2, "Quick Overview should use 2 queries"
    assert len(res_standard["search_queries_used"]) >= 3, "Standard should use at least 3 queries"
    assert res_standard["total_sources"] >= res_quick["total_sources"], "Standard should have >= sources than Quick Overview"
    assert len(res_quick["findings"]) > 0 and len(res_standard["findings"]) > 0, "Findings must never be 0"
    print("PASS: Depth configurations properly differentiate search and findings depth.")

def test_basic_question_and_findings_count():
    print("\n--- Test 5: Basic Question & Non-Zero Findings Count ---")
    res = run_research_agent("What is artificial intelligence?", depth="Standard", num_sources=6)
    
    assert len(res["summary"]) > 200, "Executive summary must be substantive (multiple paragraphs)"
    assert len(res["findings"]) >= 4, f"Expected at least 4 key findings, got {len(res['findings'])}"
    assert res["findings_count"] == len(res["findings"]), "findings_count metric must match displayed findings count"
    assert res["total_sources"] == len(res["sources"]), "total_sources metric must match sources count"
    assert len(res["detailed_analysis"]) > 100, "Detailed analysis section must be present"
    assert len(res["conclusion"]) > 50, "Conclusion must be present"
    
    # Check that at least some sources have page content extracted
    page_extracted = sum(1 for s in res["sources"] if s.get("is_page_extracted"))
    print(f"Verified: {len(res['findings'])} findings, {res['total_sources']} sources ({page_extracted} full page extracted)")
    print("PASS: Full pipeline generates complete, multi-section research answer.")

def test_comparison_question():
    print("\n--- Test 6: Multi-Perspective Question (Open Source vs Closed Source AI) ---")
    res = run_research_agent("Open source vs closed source AI models comparison", depth="Standard", num_sources=4)
    assert len(res["findings"]) >= 3
    assert len(res["summary"]) > 150
    print(f"Verified multi-perspective query: {len(res['findings'])} findings generated.")
    print("PASS: Multi-perspective synthesis completed.")

if __name__ == "__main__":
    test_empty_search()
    test_malformed_llm_output()
    test_citation_mapping()
    test_depth_differentiation()
    test_basic_question_and_findings_count()
    test_comparison_question()
    print("\n==========================================")
    print("ALL 6 PIPELINE TESTS PASSED SUCCESSFULLY! 🎉")
    print("==========================================")
