"""Shared state definition for the DeepResearch AI agent graph.

This module defines the ResearchState TypedDict that is passed between
all agents in the LangGraph workflow. Each agent reads from and writes
to specific fields in this shared state.
"""

from __future__ import annotations

from typing import TypedDict, Annotated
import operator


class ResearchState(TypedDict):
    """Shared state passed between all agents in the research graph.

    Attributes:
        query: The original user research question.
        sub_questions: Decomposed sub-questions from the Manager agent.
        web_results: Findings from the Web Searcher.
        paper_results: Academic paper findings from Paper Reader.
        verified_facts: Fact-checked claims with confidence scores.
        final_report: The synthesized markdown research report.
        status_updates: Live progress messages for the UI.
        sources: All collected source citations.
    """

    # Input
    query: str

    # Manager output
    sub_questions: list[str]

    # Research outputs (Annotated with operator.add for parallel merging)
    web_results: Annotated[list[dict], operator.add]
    paper_results: Annotated[list[dict], operator.add]

    # Fact checker output
    verified_facts: list[dict]

    # Writer output
    final_report: str

    # Metadata (Annotated with operator.add for parallel merging)
    status_updates: Annotated[list[str], operator.add]
    sources: Annotated[list[dict], operator.add]