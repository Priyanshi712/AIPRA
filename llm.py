import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found!")

genai.configure(api_key=api_key)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

model = genai.GenerativeModel(MODEL)



def clean_llm_output(text: str) -> str:
    """Removes internal thought traces and raw think tags."""
    if not text:
        return ""
    # Strip <think>...</think> blocks
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Strip any dangling/unclosed <think> tags
    cleaned = re.sub(r"^.*?Here's a thinking process:.*?(?=# |\*\*Executive Summary|\n\n)", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()


def _generate(prompt: str, temperature: float, max_tokens: int) -> str:
    """Helper to call the Gemini API and return raw text."""
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
        request_options={"timeout": 60},
    )
    return response.text or ""


def create_research_plan(question: str, num_queries: int = 3) -> dict:
    prompt = f"""You are a research planner. Generate {num_queries} distinct, direct search queries to research:
"{question}"

Rules:
- Write ONLY the search queries, one per line.
- Do not include numbering, bullets, quotes, or conversational preamble."""

    try:
        raw_text = clean_llm_output(_generate(prompt, temperature=0.2, max_tokens=800))
        lines = [line.strip().lstrip("0123456789.-*•\"'[] ") for line in raw_text.splitlines() if line.strip()]
        queries = [
            q for q in lines
            if len(q) > 3 and not any(tag in q.lower() for tag in ["think", "role:", "topic:", "analyze", "here"])
        ]

        if not queries:
            queries = [question]

        return {"queries": queries[:num_queries]}

    except Exception as e:
        print(f"Error creating research plan: {e}")
        return {"queries": [question]}


def analyze_sources(question: str, sources: list) -> str:
    # Deduplicate sources by URL
    seen_urls = set()
    unique_sources = []
    for s in sources:
        url = s.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(s)

    # Limit to top 6 sources with 500 chars to respect API rate limits
    top_sources = unique_sources[:6]
    formatted_sources = ""
    for i, source in enumerate(top_sources, 1):
        content_snippet = source.get("content", "No content available")[:500]
        formatted_sources += f"\n[{i}] {source.get('title', 'Untitled')}\n"
        formatted_sources += f"URL: {source.get('url', 'N/A')}\n"
        formatted_sources += f"Snippet: {content_snippet}...\n"
        formatted_sources += "-" * 30 + "\n"

    prompt = f"""You are an expert research analyst. Write a research report directly answering: "{question}"

Use only the provided web evidence:
{formatted_sources}

Respond strictly in markdown matching this structure:
# Research Report

## Executive Summary
(2-3 sentences answering the research question directly)

## Key Findings
(Detailed points citing sources using [1], [2], etc.)

## Limitations & Key Takeaways
(Key implications and limitations from the findings)

## Sources
(List format: [1] [Title](URL))"""

    try:
        raw_report = _generate(prompt, temperature=0.2, max_tokens=3000)
        return clean_llm_output(raw_report)

    except Exception as e:
        print(f"Error analyzing sources: {e}")
        return f"Error generating report: {e}"


def generate_summary(text: str, max_length: int = 200) -> str:
    prompt = f"Summarize this text in under {max_length} characters. Return ONLY the summary:\n\n{text}"
    try:
        raw_summary = _generate(prompt, temperature=0.2, max_tokens=1000)
        return clean_llm_output(raw_summary)[:max_length]
    except Exception as e:
        print(f"Error generating summary: {e}")
        return text[:max_length]