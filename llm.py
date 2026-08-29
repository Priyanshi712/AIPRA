import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def create_research_plan(question: str, num_queries: int = 3) -> dict:
    prompt = f"""You are an AI research planner.
Generate {num_queries} distinct web search queries to thoroughly research: "{question}"

Rules:
- Write ONLY a valid JSON array of search strings.
- Do NOT add thoughts, markdown commentary, or explanations.

Example response:
["what is retrieval augmented generation", "how does RAG work architecture", "RAG use cases and benefits"]"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=250
        )

        raw_text = response.choices[0].message.content or ""
        
        # Remove any internal reasoning tokens
        cleaned_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
        
        # Extract JSON list if present
        match = re.search(r"\[.*?\]", cleaned_text, re.DOTALL)
        if match:
            queries = json.loads(match.group(0))
            valid_queries = [q for q in queries if isinstance(q, str) and len(q) > 3 and not q.startswith("<think")]
            if valid_queries:
                return {"queries": valid_queries[:num_queries]}

        # Fallback line-by-line parsing
        lines = [line.strip().lstrip("0123456789.-*•\"'[] ") for line in cleaned_text.splitlines() if line.strip()]
        queries = [
            q for q in lines 
            if len(q) > 4 and not any(tag in q.lower() for tag in ["think", "role:", "topic:", "analyze"])
        ]

        return {"queries": queries[:num_queries] if queries else [question]}

    except Exception as e:
        print(f"Error creating research plan: {e}")
        return {"queries": [question]}


def analyze_sources(question: str, sources: list) -> str:
    # 1. Deduplicate sources by URL
    seen_urls = set()
    unique_sources = []
    for s in sources:
        url = s.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(s)

    # 2. Limit to top 6 sources and cap content to 600 chars each to stay well under TPM limits
    top_sources = unique_sources[:6]
    formatted_sources = ""
    for i, source in enumerate(top_sources, 1):
        content_snippet = source.get("content", "No content available")[:600]
        formatted_sources += f"\n[{i}] {source.get('title', 'Untitled')}\n"
        formatted_sources += f"URL: {source.get('url', 'N/A')}\n"
        formatted_sources += f"Snippet: {content_snippet}...\n"
        formatted_sources += "-" * 30 + "\n"

    prompt = f"""You are a research analyst. Write a clear markdown report for: "{question}"

Sources:
{formatted_sources}

Report Structure:
# Research Report
## Executive Summary
(2-3 sentences overview)
## Key Findings
(Detailed points citing sources using [1], [2], etc.)
## Limitations & Key Takeaways
## Sources
(List format: [1] [Title](URL))"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500
        )
        report = response.choices[0].message.content or ""
        return re.sub(r"<think>.*?</think>", "", report, flags=re.DOTALL).strip()
    except Exception as e:
        print(f"Error analyzing sources: {e}")
        return f"Error generating report: {e}"


def generate_summary(text: str, max_length: int = 200) -> str:
    prompt = f"Summarize this text in under {max_length} characters. Return ONLY the summary:\n\n{text}"
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=100
        )
        summary = response.choices[0].message.content or ""
        return re.sub(r"<think>.*?</think>", "", summary, flags=re.DOTALL).strip()[:max_length]
    except Exception as e:
        print(f"Error generating summary: {e}")
        return text[:max_length]