"""Fact Checker Agent - Cross-references and verifies research findings.

This agent takes all findings from the Web Searcher and Paper Reader,
cross-references claims across multiple sources, and assigns confidence
scores based on source agreement.
"""

import json
import time
from src.config import get_llm
from src.state import ResearchState


FACT_CHECK_PROMPT = """You are a Fact Verification AI. Your job is to analyze research findings from multiple sources,
identify key claims, cross-reference them, and assign confidence levels.

Original Research Question: {query}

=== Web Research Findings ===
{web_findings}

=== Academic Paper Findings ===
{paper_findings}

Instructions:
1. Identify the 5-10 most important factual claims from all findings
2. For each claim, check if multiple sources support it
3. Assign confidence levels:
   - HIGH: Supported by 3+ sources OR confirmed by academic paper
   - MEDIUM: Supported by 2 sources
   - LOW: Only 1 source OR sources contradict each other
4. Note any contradictions between sources

Return as a JSON array:
[{{
    "claim": "The factual claim statement",
    "confidence": "HIGH" or "MEDIUM" or "LOW",
    "supporting_sources": ["source1", "source2"],
    "contradictions": ["any contradicting info or empty string"]
}}]

JSON array of verified facts:"""


def fact_checker_node(state):
    """Cross-reference findings and assign confidence scores."""
    web_results = state.get("web_results", [])
    paper_results = state.get("paper_results", [])
    query = state.get("query", "")

    print(f"\n{'='*60}")
    print(f"FACT CHECKER AGENT: Verifying {len(web_results)} web + {len(paper_results)} paper findings...")
    print(f"{'='*60}\n")

    # Pace between agents
    print("  >> Pacing: waiting 5s before fact-checking...")
    time.sleep(5)

    web_text = _format_findings(web_results, "web")
    paper_text = _format_findings(paper_results, "paper")

    try:
        llm = get_llm(temperature=0.0)
        response = llm.invoke(FACT_CHECK_PROMPT.format(
            query=query,
            web_findings=web_text[:4000],
            paper_findings=paper_text[:4000]
        ))

        verified_facts = _parse_facts(response.content)

    except Exception as e:
        print(f"  Fact checker error: {e}")
        verified_facts = _create_fallback_facts(web_results, paper_results)

    high = sum(1 for f in verified_facts if f.get("confidence") == "HIGH")
    medium = sum(1 for f in verified_facts if f.get("confidence") == "MEDIUM")
    low = sum(1 for f in verified_facts if f.get("confidence") == "LOW")

    print(f"\nFact Checker complete: {len(verified_facts)} facts verified")
    print(f"  HIGH: {high} | MEDIUM: {medium} | LOW: {low}")

    return {
        "verified_facts": verified_facts,
        "status_updates": [
            f"Fact Checker: Verified {len(verified_facts)} facts ({high} high, {medium} medium, {low} low confidence)"
        ],
    }


def _format_findings(findings, finding_type):
    if not findings:
        return "No findings available."
    parts = []
    for i, f in enumerate(findings, 1):
        if finding_type == "paper":
            text = (
                f"{i}. Title: {f.get('title', 'N/A')}\n"
                f"   Authors: {f.get('authors', 'N/A')}\n"
                f"   Findings: {f.get('key_findings', f.get('content', 'N/A'))}\n"
                f"   URL: {f.get('url', 'N/A')}"
            )
        else:
            text = (
                f"{i}. {f.get('content', 'N/A')}\n"
                f"   Source: {f.get('source', 'N/A')}\n"
                f"   URL: {f.get('url', 'N/A')}"
            )
        parts.append(text)
    return "\n\n".join(parts)


def _parse_facts(content):
    try:
        data = json.loads(content.strip())
        if isinstance(data, list):
            return _validate_facts(data)
    except json.JSONDecodeError:
        pass

    try:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start != -1 and end > start:
            data = json.loads(content[start:end])
            if isinstance(data, list):
                return _validate_facts(data)
    except (json.JSONDecodeError, ValueError):
        pass

    return [{
        "claim": content.strip()[:500],
        "confidence": "MEDIUM",
        "supporting_sources": ["LLM Analysis"],
        "contradictions": []
    }]


def _validate_facts(facts):
    validated = []
    for fact in facts:
        validated.append({
            "claim": fact.get("claim", "Unknown claim"),
            "confidence": fact.get("confidence", "MEDIUM").upper(),
            "supporting_sources": fact.get("supporting_sources", []),
            "contradictions": fact.get("contradictions", [])
        })
    return validated


def _create_fallback_facts(web_results, paper_results):
    facts = []
    for r in web_results[:5]:
        content = r.get("content", "")
        if content:
            facts.append({
                "claim": content[:200],
                "confidence": "MEDIUM",
                "supporting_sources": [r.get("source", "Web")],
                "contradictions": []
            })
    return facts
