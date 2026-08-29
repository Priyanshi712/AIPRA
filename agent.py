
from llm import create_research_plan, analyze_sources
from search import search_multiple_queries


def research(question: str, max_results: int = 5) -> dict:
    """
    Execute the complete research workflow:

    1. Create a research plan with multiple queries
    2. Search the web using those queries
    3. Analyze and synthesize sources
    4. Return a structured report

    Args:
        question: The research question.
        max_results: Maximum number of web sources to retrieve
                     per search query.

    Returns:
        Dictionary containing:
        - queries: List of search queries used
        - sources: List of source dictionaries
        - report: Markdown-formatted research report
    """

    result = {
        "queries": [],
        "sources": [],
        "report": ""
    }

    # ========================================================
    # STEP 1: CREATE RESEARCH PLAN
    # ========================================================

    print("📋 Creating research plan...")

    plan = create_research_plan(question)

    queries = plan.get(
        "queries",
        [question]
    )

    result["queries"] = queries


    # ========================================================
    # STEP 2: SEARCH THE WEB
    # ========================================================

    print(
        f"🔍 Searching the web "
        f"(up to {max_results} sources per query)..."
    )

    sources = search_multiple_queries(
        queries,
        max_results=max_results
    )

    result["sources"] = sources


    # ========================================================
    # HANDLE EMPTY SEARCH RESULTS
    # ========================================================

    if not sources:

        result["report"] = (
            "❌ No sources found. "
            "Try a different research question."
        )

        return result


    # ========================================================
    # STEP 3: ANALYZE AND SYNTHESIZE SOURCES
    # ========================================================

    print(
        "📊 Analyzing sources and generating report..."
    )

    report = analyze_sources(
        question,
        sources
    )

    result["report"] = report


    # ========================================================
    # RETURN FINAL RESULT
    # ========================================================

    return result


def format_sources_for_display(
    sources: list
) -> list:
    """
    Format sources for UI display.

    Args:
        sources: List of source dictionaries.

    Returns:
        List of formatted source dictionaries.
    """

    formatted = []

    for i, source in enumerate(
        sources,
        1
    ):

        formatted.append(
            {
                "number": i,
                "title": source.get(
                    "title",
                    "Untitled"
                ),
                "url": source.get(
                    "url",
                    "#"
                ),
                "score": source.get(
                    "score",
                    0
                )
            }
        )

    return formatted

