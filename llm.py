import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5")


def create_research_plan(question: str, num_queries: int = 4) -> dict:
    prompt = f"""You are an expert research planner. The user wants to research:

"{question}"

Generate exactly {num_queries} diverse web search queries that explore different aspects of this question.
Each query should be:
- Specific and focused
- Different from the others
- Likely to return relevant results

Return ONLY valid JSON with no additional text:
{{
    "queries": [
        "query 1",
        "query 2",
        "query 3",
        "query 4"
    ]
}}
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        plan = json.loads(response_text)
        return plan
    
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        return {"queries": [question]}
    except Exception as e:
        print(f"Error creating research plan: {e}")
        return {"queries": [question]}


def analyze_sources(question: str, sources: list) -> str:
    formatted_sources = ""
    for i, source in enumerate(sources, 1):
        formatted_sources += f"\n[{i}] **{source.get('title', 'Untitled')}**\n"
        formatted_sources += f"URL: {source.get('url', 'N/A')}\n"
        formatted_sources += f"Content: {source.get('content', 'No content available')}\n"
        formatted_sources += "-" * 50 + "\n"
    
    prompt = f"""You are an expert research analyst. Your task is to create a comprehensive research report.

Research Question:
{question}

Below are web sources collected by the research agent:

{formatted_sources}

Create a well-structured research report following these requirements:

1. **Executive Summary** - Brief overview of key findings (2-3 sentences)
2. **Key Findings** - Main discoveries organized by theme (use numbered citations)
3. **Important Details** - Supporting details and context
4. **Limitations & Contradictions** - Areas of disagreement or insufficient data
5. **Conclusion** - Summary and implications

Guidelines:
- ONLY cite facts that are clearly in the sources
- Use [1], [2], [3] etc. to reference sources
- Do NOT invent information
- Be objective and balanced
- Use markdown formatting
- Include a **Sources** section at the end listing [1] through [n]

Format your response as clean markdown:

# Research Report

## Executive Summary
...

## Key Findings
...

## Important Details
...

## Limitations & Contradictions
...

## Conclusion
...

## Sources
[1] [Source Title](URL)
[2] [Source Title](URL)
...
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        report = response.choices[0].message.content.strip()
        return report
    
    except Exception as e:
        print(f"Error analyzing sources: {e}")
        return f"Error generating report: {e}"


def generate_summary(text: str, max_length: int = 200) -> str:
    prompt = f"""Summarize the following text in {max_length} characters or less:

{text}

Return ONLY the summary, no additional text."""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return text[:max_length]