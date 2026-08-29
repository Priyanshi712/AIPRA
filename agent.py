
from llm import create_research_plan, analyze_sources
from search import search_multiple_queries


def research(
    question: str,
    max_results: int = 5,
    max_iterations: int = 2
) -> dict:
    """
    Execute the AIPRA research workflow.

    Workflow:
        1. Generate research queries
        2. Search the web
        3. Evaluate research coverage
        4. Optionally perform another research iteration
        5. Generate final report

    Args:
        question: User's research question.
        max_results: Maximum sources per search query.
        max_iterations: Maximum number of research rounds.

    Returns:
        Dictionary containing:
            queries
            sources
            report
            iterations
            status
    """

    result = {
        "queries": [],
        "sources": [],
        "report": "",
        "iterations": 0,
        "status": "started"
    }

    # ========================================================
    # STEP 1 — CREATE INITIAL RESEARCH PLAN
    # ========================================================

    print("📋 Creating research plan...")

    plan = create_research_plan(question)

    queries = plan.get(
        "queries",
        [question]
    )

    result["queries"].extend(queries)

    print(
        f"🧠 Generated {len(queries)} research queries."
    )


    # ========================================================
    # STEP 2 — ITERATIVE RESEARCH
    # ========================================================

    all_sources = []

    seen_urls = set()


    for iteration in range(
        max_iterations
    ):

        result["iterations"] = iteration + 1

        print(
            f"\n🔬 Research iteration "
            f"{iteration + 1}/{max_iterations}"
        )


        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        print(
            f"🔍 Searching {len(queries)} queries..."
        )

        sources = search_multiple_queries(
            queries,
            max_results=max_results
        )


        # ----------------------------------------------------
        # ADD ONLY NEW SOURCES
        # ----------------------------------------------------

        new_sources = []

        for source in sources:

            url = source.get(
                "url",
                ""
            )

            if not url:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            all_sources.append(source)
            new_sources.append(source)


        print(
            f"📚 Found {len(new_sources)} new sources."
        )


        # ----------------------------------------------------
        # STOP IF NO SOURCES
        # ----------------------------------------------------

        if not new_sources:

            print(
                "⚠️ No new sources found."
            )

            break


        # ----------------------------------------------------
        # CURRENT MVP ITERATION LOGIC
        # ----------------------------------------------------
        #
        # We currently don't have a dedicated LLM
        # research-quality evaluator.
        #
        # Therefore:
        # - First iteration always searches.
        # - Additional iterations currently stop unless
        #   future logic generates new queries.
        #
        # We will replace this section with a proper
        # evidence evaluator in the next upgrade.
        # ----------------------------------------------------

        if iteration < max_iterations - 1:

            print(
                "🔎 Preparing for deeper research..."
            )

            # Temporary strategy:
            # Search the original queries again would
            # produce mostly duplicate sources, so we
            # currently stop here.

            break


    # ========================================================
    # STORE SOURCES
    # ========================================================

    result["sources"] = all_sources


    # ========================================================
    # HANDLE EMPTY RESULTS
    # ========================================================

    if not all_sources:

        result["status"] = "no_sources"

        result["report"] = (
            "❌ No sources were found. "
            "Try a different research question."
        )

        return result


    # ========================================================
    # STEP 3 — SYNTHESIZE REPORT
    # ========================================================

    print(
        f"\n📊 Analyzing "
        f"{len(all_sources)} sources..."
    )

    report = analyze_sources(
        question,
        all_sources
    )

    result["report"] = report

    result["status"] = "completed"


    # ========================================================
    # FINAL STATUS
    # ========================================================

    print(
        f"✅ Research completed with "
        f"{len(all_sources)} sources."
    )

    return result


def format_sources_for_display(
    sources: list
) -> list:
    """
    Format sources for UI display.
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
