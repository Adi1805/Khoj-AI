"""Web Searcher Agent - Searches the web and Wikipedia for information.

This agent takes the sub-questions from the Manager and searches
DuckDuckGo and Wikipedia for relevant information, then uses the
LLM to extract and summarize key findings.

Includes rate-limit-friendly delays between requests.
"""

import json
import time
from src.config import get_llm
from src.state import ResearchState
from src.tools.search_tools import web_search, wikipedia_search
from src.vectorstore.store import ResearchVectorStore


EXTRACTION_PROMPT = """You are a research assistant. Given the following search results for a specific question, 
extract the most important and relevant findings.

Research Question: {question}

Search Results:
{results}

Extract 3-5 key findings. For each finding, provide:
- A clear, factual statement (the "content")
- The source name 
- The source URL (if available)

Return as a JSON array of objects like:
[{{"content": "key finding here", "source": "source name", "url": "https://..."}}]

If the results are not useful, return an empty array: []

JSON array:"""


def web_searcher_node(state):
    """Search the web and Wikipedia for information on each sub-question."""
    sub_questions = state.get("sub_questions", [])
    print(f"\n{'='*60}")
    print(f"WEB SEARCHER AGENT: Searching for {len(sub_questions)} questions...")
    print(f"{'='*60}\n")

    all_results = []
    all_sources = []
    llm = get_llm(temperature=0.0)

    for i, question in enumerate(sub_questions, 1):
        print(f"  [{i}/{len(sub_questions)}] Searching: {question}")

        # Rate limit delay between questions (not before first)
        if i > 1:
            print(f"    >> Pacing: waiting 5s to respect rate limits...")
            time.sleep(5)

        # Search DuckDuckGo
        try:
            ddg_results = web_search.invoke(question)
        except Exception as e:
            ddg_results = f"Search failed: {e}"
            print(f"    DuckDuckGo error: {e}")

        # Search Wikipedia
        try:
            wiki_results = wikipedia_search.invoke(question)
        except Exception as e:
            wiki_results = f"Wikipedia search failed: {e}"
            print(f"    Wikipedia error: {e}")

        # Combine results
        combined = f"=== Web Search Results ===\n{ddg_results}\n\n=== Wikipedia Results ===\n{wiki_results}"

        # Use LLM to extract key findings (with auto-retry built into RetryLLM)
        try:
            response = llm.invoke(EXTRACTION_PROMPT.format(
                question=question,
                results=combined[:6000]
            ))
            findings = _parse_findings(response.content, "web")
        except Exception as e:
            print(f"    LLM extraction error: {e}")
            findings = [{
                "content": ddg_results[:500] if ddg_results else "No results found",
                "source": "DuckDuckGo",
                "url": "",
                "source_type": "web"
            }]

        all_results.extend(findings)

        for f in findings:
            if f.get("url"):
                all_sources.append({
                    "source": f.get("source", "Web"),
                    "url": f.get("url", ""),
                    "source_type": "web"
                })

        print(f"    Found {len(findings)} findings")

    # Store findings in vector store for fact-checking
    try:
        store = ResearchVectorStore()
        store.add_findings(all_results)
    except Exception as e:
        print(f"  Vector store error (non-critical): {e}")

    print(f"\nWeb Searcher complete: {len(all_results)} total findings")

    return {
        "web_results": all_results,
        "sources": all_sources,
        "status_updates": [
            f"Web Searcher: Found {len(all_results)} results across {len(sub_questions)} sub-questions"
        ],
    }


def _parse_findings(content, source_type="web"):
    """Parse findings from LLM response."""
    try:
        data = json.loads(content.strip())
        if isinstance(data, list):
            for item in data:
                item["source_type"] = source_type
            return data
    except json.JSONDecodeError:
        pass

    try:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start != -1 and end > start:
            data = json.loads(content[start:end])
            if isinstance(data, list):
                for item in data:
                    item["source_type"] = source_type
                return data
    except (json.JSONDecodeError, ValueError):
        pass

    return [{
        "content": content.strip()[:1000],
        "source": "Web Search",
        "url": "",
        "source_type": source_type
    }]
