"""ArXiv academic paper search tools.

Provides free access to the ArXiv API for searching and retrieving
academic research papers. No API key required.
"""

import arxiv
from langchain_core.tools import tool


@tool
def search_arxiv(query: str) -> str:
    """Search ArXiv for academic research papers on a given topic.

    Args:
        query: The research topic or keywords to search for.

    Returns:
        Formatted list of relevant papers with metadata and abstracts.
    """
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers = []
        for result in client.results(search):
            authors = ", ".join(a.name for a in result.authors[:3])
            if len(result.authors) > 3:
                authors += " et al."

            categories = ", ".join(result.categories[:3])

            papers.append(
                f"**{result.title}**\n"
                f"Authors: {authors}\n"
                f"Published: {result.published.strftime('%Y-%m-%d')}\n"
                f"Categories: {categories}\n"
                f"URL: {result.entry_id}\n"
                f"Abstract: {result.summary[:800]}\n"
            )

        if not papers:
            return f"No academic papers found on ArXiv for: {query}"

        return "\n---\n".join(papers)

    except Exception as e:
        return f"ArXiv search error: {str(e)}"


def get_arxiv_tools() -> list:
    """Get all ArXiv-related tools for use by research agents."""
    return [search_arxiv]