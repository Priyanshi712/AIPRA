import os
from urllib.parse import urlparse, urlunparse

from tavily import TavilyClient
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError(
        "TAVILY_API_KEY is missing. "
        "Please add it to your .env file."
    )

tavily = TavilyClient(api_key=TAVILY_API_KEY)


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(url: str) -> str:
    """
    Normalize a URL so that minor URL differences
    don't cause duplicate sources.

    Example:
        https://example.com/article/
        https://example.com/article
        https://example.com/article?utm_source=test

    are treated as the same source.
    """

    if not url:
        return ""

    try:
        parsed = urlparse(url)

        # Remove query parameters and fragments.
        normalized = parsed._replace(
            query="",
            fragment=""
        )

        # Remove trailing slash from path.
        path = normalized.path.rstrip("/")

        normalized = normalized._replace(
            path=path
        )

        return urlunparse(normalized)

    except Exception:
        return url.strip()


# ============================================================
# SINGLE WEB SEARCH
# ============================================================

def search_web(
    query: str,
    max_results: int = 5
) -> list:
    """
    Search the web using Tavily.

    Args:
        query: Search query.
        max_results: Maximum number of results.

    Returns:
        Cleaned list of source dictionaries.
    """

    try:

        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )

        results = []

        for result in response.get("results", []):

            title = result.get(
                "title",
                ""
            ).strip()

            url = result.get(
                "url",
                ""
            ).strip()

            content = result.get(
                "content",
                ""
            ).strip()

            score = result.get(
                "score",
                0
            )

            # -----------------------------------------------
            # Ignore incomplete results
            # -----------------------------------------------

            if not url or not content:
                continue

            # -----------------------------------------------
            # Normalize score
            # -----------------------------------------------

            try:
                score = float(score)
            except (TypeError, ValueError):
                score = 0.0

            results.append(
                {
                    "title": title or "Untitled",
                    "url": normalize_url(url),
                    "content": content,
                    "score": score
                }
            )

        # -----------------------------------------------
        # Highest relevance first
        # -----------------------------------------------

        results.sort(
            key=lambda source: source["score"],
            reverse=True
        )

        return results

    except Exception as e:

        print(
            f"❌ Search error for query "
            f"'{query}': {e}"
        )

        return []


# ============================================================
# MULTI-QUERY SEARCH
# ============================================================

def search_multiple_queries(
    queries: list,
    max_results: int = 5
) -> list:
    """
    Search multiple queries and combine their results.

    Duplicate URLs are removed and the final results
    are sorted by relevance score.

    Args:
        queries: List of search queries.
        max_results: Maximum results per query.

    Returns:
        Deduplicated and ranked source list.
    """

    all_sources = []

    seen_urls = set()

    for query in queries:

        # -----------------------------------------------
        # Skip invalid queries
        # -----------------------------------------------

        if not query or not query.strip():
            continue

        print(
            f"🔎 Searching: {query}"
        )

        results = search_web(
            query,
            max_results=max_results
        )

        for result in results:

            url = normalize_url(
                result.get("url", "")
            )

            if not url:
                continue

            # -------------------------------------------
            # Deduplicate sources
            # -------------------------------------------

            if url in seen_urls:
                continue

            seen_urls.add(url)

            all_sources.append(
                result
            )

    # ====================================================
    # FINAL RANKING
    # ====================================================

    all_sources.sort(
        key=lambda source: source.get(
            "score",
            0
        ),
        reverse=True
    )

    print(
        f"📚 Collected {len(all_sources)} "
        f"unique sources."
    )

    return all_sources

