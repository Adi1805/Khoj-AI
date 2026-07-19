"""LangGraph Research Workflow — Orchestrates all agents.

This module defines the complete research pipeline as a LangGraph
state machine. Agents execute in sequence:
Manager -> Web Searcher -> Paper Reader -> Fact Checker -> Writer

The graph manages shared state, ensuring each agent can read
previous agents' outputs and contribute its own.
"""

from langgraph.graph import StateGraph, START, END
from src.state import ResearchState
from src.agents.manager import manager_node
from src.agents.web_searcher import web_searcher_node
from src.agents.paper_reader import paper_reader_node
from src.agents.fact_checker import fact_checker_node
from src.agents.writer import writer_node


def create_research_graph():
    """Create and compile the research agent graph.

    The workflow follows this sequence:
    1. Manager: Decomposes query into sub-questions
    2. Web Searcher: Searches DuckDuckGo and Wikipedia
    3. Paper Reader: Searches ArXiv for academic papers
    4. Fact Checker: Cross-references and verifies all findings
    5. Writer: Synthesizes a professional research report

    Returns:
        A compiled LangGraph StateGraph ready for invocation.
    """
    # Create the state graph
    workflow = StateGraph(ResearchState)

    # Add all agent nodes
    workflow.add_node("manager", manager_node)
    workflow.add_node("web_searcher", web_searcher_node)
    workflow.add_node("paper_reader", paper_reader_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("writer", writer_node)

    # Define the sequential workflow
    # START -> Manager -> Web Searcher -> Paper Reader -> Fact Checker -> Writer -> END
    workflow.add_edge(START, "manager")
    workflow.add_edge("manager", "web_searcher")
    workflow.add_edge("web_searcher", "paper_reader")
    workflow.add_edge("paper_reader", "fact_checker")
    workflow.add_edge("fact_checker", "writer")
    workflow.add_edge("writer", END)

    # Compile the graph
    graph = workflow.compile()

    print("\nResearch graph compiled successfully!")
    print("Pipeline: Manager -> Web Searcher -> Paper Reader -> Fact Checker -> Writer")

    return graph


def run_research(query: str) -> dict:
    """Run a complete research pipeline on a given query.

    This is the main entry point for the research system. It creates
    the agent graph, initializes the state, and runs the full pipeline.

    Args:
        query: The user's research question.

    Returns:
        The final ResearchState dict containing all results.
    """
    print(f"\n{'#'*60}")
    print(f"# DeepResearch AI — Starting Research")
    print(f"# Query: {query}")
    print(f"{'#'*60}\n")

    # Create the graph
    graph = create_research_graph()

    # Initialize the state with empty values
    initial_state = {
        "query": query,
        "sub_questions": [],
        "web_results": [],
        "paper_results": [],
        "verified_facts": [],
        "final_report": "",
        "status_updates": ["System: Research pipeline started"],
        "sources": [],
    }

    # Run the graph
    try:
        final_state = graph.invoke(initial_state)
        final_state["status_updates"] = final_state.get("status_updates", []) + [
            "System: Research pipeline complete!"
        ]
        print(f"\n{'#'*60}")
        print(f"# Research Complete!")
        print(f"# Sub-questions: {len(final_state.get('sub_questions', []))}")
        print(f"# Web results: {len(final_state.get('web_results', []))}")
        print(f"# Papers: {len(final_state.get('paper_results', []))}")
        print(f"# Verified facts: {len(final_state.get('verified_facts', []))}")
        print(f"# Report length: {len(final_state.get('final_report', ''))} chars")
        print(f"{'#'*60}\n")
        return final_state

    except Exception as e:
        print(f"\nERROR in research pipeline: {e}")
        return {
            **initial_state,
            "status_updates": initial_state["status_updates"] + [
                f"System Error: {str(e)}"
            ],
            "final_report": f"# Research Error\n\nAn error occurred during research: {str(e)}\n\nPlease try again.",
        }