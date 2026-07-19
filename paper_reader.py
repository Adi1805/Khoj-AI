"""Paper Reader Agent - Searches ArXiv for academic papers.

This agent searches ArXiv for relevant academic papers on each
sub-question, reads abstracts, and extracts key findings with
proper citations. Includes rate-limit-friendly delays.
"""

import json
import time
from src.config import get_llm
from src.state import ResearchState
from src.tools.arxiv_tools import search_arxiv


PAPER_EXTRACTION_PROMPT = """You are an academic research assistant. Given the following ArXiv paper search results,
extract the most important academic findings and insights.

Research Question: {question}

ArXiv Papers:
{papers}

Extract key academic findings. For each finding, provide:
- title: Paper title
- authors: Author names
- key_findings: 1-2 sentence summary of the key contribution
- url: ArXiv URL
- published: Publication date

Return as a JSON array:
[{{"title": "...", "authors": "...", "key_findings": "...", "url": "...", "published": "..."}}]

If no relevant papers found, return: []

JSON array:"""


def paper_reader_node(state):
    """Search ArXiv for academic papers on each sub-question."""
    sub_questions = state.get("sub_questions", [])
    print(f"\n{'='*60}")
    print(f"PAPER READER AGENT: Searching ArXiv for {len(sub_questions)} questions...")
    print(f"{'='*60}\n")

    all_papers = []
    all_sources = []
    llm = get_llm(temperature=0.0)

    for i, question in enumerate(sub_questions, 1):
        print(f"  [{i}/{len(sub_questions)}] Searching ArXiv: {question}")

        # Rate limit delay between questions (not before first)
        if i > 1:
            print(f"    >> Pacing: waiting 5s to respect rate limits...")
            time.sleep(5)

        # Search ArXiv
        try:
            arxiv_results = search_arxiv.invoke(question)
        except Exception as e:
            print(f"    ArXiv error: {e}")
            arxiv_results = f"ArXiv search failed: {e}"

        if "No academic papers found" in arxiv_results or "error" in arxiv_results.lower():
            print(f"    No papers found for this question")
            continue

        # Use LLM to extract structured paper info (with auto-retry built in)
        try:
            response = llm.invoke(PAPER_EXTRACTION_PROMPT.format(
                question=question,
                papers=arxiv_results[:6000]
            ))
            papers = _parse_papers(response.content)
        except Exception as e:
            print(f"    LLM extraction error: {e}")
            papers = [{
                "title": "ArXiv Search Results",
                "authors": "Various",
                "key_findings": arxiv_results[:500],
                "url": "",
                "published": "",
                "source_type": "paper"
            }]

        all_papers.extend(papers)

        for p in papers:
            if p.get("url"):
                all_sources.append({
                    "source": p.get("title", "ArXiv Paper"),
                    "url": p.get("url", ""),
                    "source_type": "paper"
                })

        print(f"    Extracted {len(papers)} paper findings")

    print(f"\nPaper Reader complete: {len(all_papers)} total papers analyzed")

    return {
        "paper_results": all_papers,
        "sources": all_sources,
        "status_updates": [
            f"Paper Reader: Analyzed {len(all_papers)} academic papers"
        ],
    }


def _parse_papers(content):
    """Parse paper findings from LLM response."""
    try:
        data = json.loads(content.strip())
        if isinstance(data, list):
            for item in data:
                item["source_type"] = "paper"
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
                    item["source_type"] = "paper"
                return data
    except (json.JSONDecodeError, ValueError):
        pass

    return [{
        "title": "ArXiv Research",
        "authors": "Various",
        "key_findings": content.strip()[:1000],
        "url": "",
        "published": "",
        "source_type": "paper"
    }]
