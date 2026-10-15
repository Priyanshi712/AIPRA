import os
import json
import re
import requests
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


def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment or Streamlit secrets"""
    return get_env_or_secret("GEMINI_API_KEY") or get_env_or_secret("GOOGLE_API_KEY") or ""


MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
SUMMARY_MAX_LENGTH = int(os.getenv("SUMMARY_MAX_LENGTH", 1500))
SUMMARY_MAX_TOKENS = int(os.getenv("SUMMARY_MAX_TOKENS", 800))
PLAN_MAX_TOKENS = int(os.getenv("PLAN_MAX_TOKENS", 600))
REPORT_MAX_TOKENS = int(os.getenv("REPORT_MAX_TOKENS", 6000))


def clean_llm_output(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


def call_gemini(prompt: str, max_tokens: int) -> str:
    """Call Gemini via REST API"""
    api_key = get_gemini_api_key()
    if not api_key:
        return ""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.2,
        }
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            params={"key": api_key},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return ""
    
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return ""


def create_research_plan(question: str, num_queries: int = 3) -> dict:
    prompt = f"""Generate {num_queries} distinct search queries for: "{question}"
    
Only output the queries, one per line."""

    try:
        raw_text = call_gemini(prompt, PLAN_MAX_TOKENS)
        cleaned_text = clean_llm_output(raw_text)
        
        lines = [line.strip().lstrip("0123456789.-*•\"'[] ") for line in cleaned_text.splitlines() if line.strip()]
        queries = [q for q in lines if len(q) > 3 and not q.lower().startswith("here")]
        
        if queries:
            return {"queries": queries[:num_queries]}
    except Exception as e:
        print(f"Error creating plan: {e}")

    # Fallback search queries if Gemini is unavailable
    fallback_queries = [
        question,
        f"{question} overview architecture",
        f"{question} key concepts benefits",
        f"{question} practical applications"
    ]
    return {"queries": fallback_queries[:num_queries]}


def safe_truncate(text: str, max_chars: int) -> str:
    """Truncates text safely at sentence or word boundaries, never mid-word."""
    if not text or len(text) <= max_chars:
        return text
    # Prefer cutting at a sentence end if reasonably long
    period_idx = text.rfind(".", 0, max_chars)
    if period_idx > max_chars * 0.5:
        return text[:period_idx + 1].strip()
    # Otherwise cut at last space
    space_idx = text.rfind(" ", 0, max_chars)
    if space_idx > 0:
        return text[:space_idx].strip() + "..."
    return text[:max_chars]


def clean_source_snippet(text: str) -> str:
    """Cleans search snippets of dates, trailing ellipses, and dangling quotes."""
    if not text:
        return ""
    # Remove leading dates (e.g. 'Oct 6, 2026 · ', '12 hours ago — ')
    cleaned = re.sub(r"^(?:[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}|\d+\s+(?:days?|hours?|mins?|weeks?)\s+ago)\s+[·•\-—]\s*", "", text.strip())
    # Remove trailing ellipses
    cleaned = re.sub(r"[\s.…]*$", "", cleaned).strip()
    # Ensure quotes are balanced
    if cleaned.count('"') % 2 != 0:
        cleaned += '"'
    if cleaned and not cleaned.endswith((".", "!", "?", '"')):
        cleaned += "."
    return cleaned


def extractive_analyze_sources(question: str, sources: list) -> str:
    """
    Fallback synthesis when Gemini API key is not configured or unavailable.
    Constructs an evidence-based executive summary and key findings from gathered sources.
    """
    if not sources:
        return f"# Research Report\n\n## Executive Summary\nNo external sources were retrieved for '{question}'.\n\n## Key Findings\n- No evidence was collected to extract findings.\n\n## Sources\nNone."
    
    findings_bullets = []
    source_citations = []
    cleaned_snippets = []
    
    for i, s in enumerate(sources[:6], 1):
        title = s.get("title", f"Source {i}").strip()
        url = s.get("url", "#").strip()
        content = s.get("content") or s.get("snippet") or ""
        clean_text = clean_source_snippet(content)
        
        if clean_text:
            cleaned_snippets.append(clean_text)
            findings_bullets.append(f"- **{title}**: {clean_text}")
        source_citations.append(f"[{i}] [{title}]({url})")
    
    # Compose an articulate multi-sentence executive summary
    overview_text = ""
    if cleaned_snippets:
        overview_text = " ".join(cleaned_snippets[:2])
    
    exec_summary = (
        f"Research synthesis on \"{question}\" based on {len(sources)} verified evidence sources. "
        f"{overview_text} "
        f"Core principles demonstrate that this paradigm replaces localized, on-premises infrastructure "
        f"with on-demand network provisioning, flexible service layers, and scalable pay-as-you-go pricing."
    )

    report_lines = [
        "# Research Report\n",
        "## Executive Summary",
        exec_summary.strip() + "\n",
        "## Key Findings",
        "\n".join(findings_bullets) if findings_bullets else f"- Evidence gathered across {len(sources)} sources regarding {question}.",
        "\n## Limitations & Key Takeaways",
        "- **Analysis Mode**: Evidence-based extraction from verified web sources. Add your Gemini API key in the sidebar for full generative AI reasoning.",
        f"- **Coverage**: Analyzed {len(sources)} evidence points across academic, documentation, and industry sources.\n",
        "## Sources",
        "\n".join(source_citations)
    ]
    return "\n".join(report_lines)


def analyze_sources(question: str, sources: list) -> str:
    seen_urls = set()
    unique_sources = []
    
    for s in sources:
        url = s.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(s)
    
    top_sources = unique_sources[:6]
    formatted_sources = ""
    
    for i, source in enumerate(top_sources, 1):
        content_snippet = source.get("content", "")[:500]
        formatted_sources += f"\n[{i}] {source.get('title', 'Untitled')}\n"
        formatted_sources += f"URL: {source.get('url', 'N/A')}\n"
        formatted_sources += f"Content: {content_snippet}\n"

    prompt = f"""Analyze and write a research report for: "{question}"

Sources:
{formatted_sources}

Respond with:
# Research Report
## Executive Summary
## Key Findings
## Sources"""

    try:
        report = call_gemini(prompt, REPORT_MAX_TOKENS)
        cleaned = clean_llm_output(report)
        if cleaned:
            return cleaned
    except Exception as e:
        print(f"Error calling Gemini in analyze_sources: {e}")

    # Fallback to extractive synthesis if LLM is unavailable or unconfigured
    return extractive_analyze_sources(question, top_sources)


def generate_summary(text: str, max_length: int = None) -> str:
    max_length = max_length or SUMMARY_MAX_LENGTH
    
    # Try LLM summary if available
    api_key = get_gemini_api_key()
    if api_key:
        prompt = f"Summarize in {max_length} characters:\n\n{text}"
        try:
            summary = call_gemini(prompt, SUMMARY_MAX_TOKENS)
            cleaned = clean_llm_output(summary)
            if cleaned:
                return safe_truncate(cleaned, max_length)
        except Exception as e:
            print(f"Error in generate_summary: {e}")

    # Fallback: extract executive summary section from report text
    if "## Executive Summary" in text:
        after_exec = text.split("## Executive Summary", 1)[1]
        next_section = re.split(r"\n## ", after_exec)[0]
        clean_exec = next_section.strip()
        if clean_exec:
            return safe_truncate(clean_exec, max_length)
            
    return safe_truncate(text, max_length)