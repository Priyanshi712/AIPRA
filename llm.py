import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
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
            params={"key": GEMINI_API_KEY},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text
    
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return ""


def create_research_plan(question: str, num_queries: int = 3) -> dict:
    prompt = f"""Generate {num_queries} distinct search queries for: "{question}"
    
Only output the queries, one per line."""

    try:
        raw_text = call_gemini(prompt, PLAN_MAX_TOKENS)
        cleaned_text = clean_llm_output(raw_text)
        
        lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
        queries = [q for q in lines if len(q) > 3]
        
        return {"queries": queries[:num_queries] if queries else [question]}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"queries": [question]}


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
        return clean_llm_output(report)
    
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"


def generate_summary(text: str, max_length: int = None) -> str:
    max_length = max_length or SUMMARY_MAX_LENGTH
    prompt = f"Summarize in {max_length} characters:\n\n{text}"
    
    try:
        summary = call_gemini(prompt, SUMMARY_MAX_TOKENS)
        return clean_llm_output(summary)[:max_length]
    
    except Exception as e:
        print(f"Error: {e}")
        return text[:max_length]