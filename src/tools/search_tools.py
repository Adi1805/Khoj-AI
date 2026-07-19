"""Web search and Wikipedia tools for research agents.

Provides free, unlimited search capabilities:
- DuckDuckGo: General web search (no API key needed)
- Wikipedia: Encyclopedia knowledge base (no API key needed)
"""

from langchain_core.tools import tool
from duckduckgo_search import DDGS
import wikipedia


@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo for current information on any topic.

    Args:
        query: The search query to look up on the web.

    Returns:
        Formatted search results with titles, URLs, and snippets.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return f"No web results found for: {query}"

        formatted = []
        for r in results:
            formatted.append(
                f"**{r.get('title', 'No Title')}**\n"
                f"URL: {r.get('href', 'N/A')}\n"
                f"Snippet: {r.get('body', 'No description')}\n"
            )
        return "\n---\n".join(formatted)

    except Exception as e:
        return f"Web search error: {str(e)}"


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for detailed, encyclopedic information on a topic.

    Args:
        query: The topic to look up on Wikipedia.

    Returns:
        Summaries of relevant Wikipedia articles with URLs.
    """
    try:
        search_results = wikipedia.search(query, results=3)

        if not search_results:
            return f"No Wikipedia articles found for: {query}"

        summaries = []
        for title in search_results[:2]:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                summary = page.summary[:1500]
                summaries.append(
                    f"**{page.title}**\n"
                    f"URL: {page.url}\n"
                    f"Summary: {summary}\n"
                )
            except wikipedia.DisambiguationError as e:
                if e.options:
                    try:
                        page = wikipedia.page(e.options[0], auto_suggest=False)
                        summaries.append(
                            f"**{page.title}**\n"
                            f"URL: {page.url}\n"
                            f"Summary: {page.summary[:1500]}\n"
                        )
                    except Exception:
                        continue
            except wikipedia.PageError:
                continue

        return "\n---\n".join(summaries) if summaries else f"Could not retrieve articles for: {query}"

    except Exception as e:
        return f"Wikipedia search error: {str(e)}"


def get_all_search_tools() -> list:
    """Get all web search tools for use by research agents."""
    return [web_search, wikipedia_search]