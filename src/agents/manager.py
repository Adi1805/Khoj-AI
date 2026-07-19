"""Manager Agent — Query decomposition and orchestration.

The Manager is the first agent in the pipeline. It takes the user's
research question and decomposes it into 3-5 focused sub-questions
that the specialist agents can research independently.
"""

import json
from src.config import get_llm
from src.state import ResearchState


MANAGER_PROMPT = """You are a Research Manager AI. Your job is to analyze a user's research question 
and decompose it into 3-5 specific, focused sub-questions that can be independently researched.

Guidelines:
- Each sub-question should cover a different aspect of the topic
- Sub-questions should be specific enough to get precise search results
- Include questions about: current state, recent developments, key players, challenges, and future outlook
- Make sub-questions searchable (good for web search and academic paper search)

User's Research Question: {query}

Return ONLY a JSON array of sub-questions. Example:
["What are the latest developments in X?", "Who are the key researchers in X?", "What challenges remain in X?"]

JSON array of sub-questions:"""


def manager_node(state: ResearchState) -> dict:
    """Decompose the user's query into focused sub-questions.

    Args:
        state: The current research state with the user's query.

    Returns:
        Dict with sub_questions and status_updates.
    """
    query = state["query"]
    print(f"\n{'='*60}")
    print(f"MANAGER AGENT: Analyzing query...")
    print(f"Query: {query}")
    print(f"{'='*60}\n")

    try:
        llm = get_llm(temperature=0.0)
        response = llm.invoke(MANAGER_PROMPT.format(query=query))
        content = response.content.strip()

        # Parse the JSON response
        sub_questions = _parse_questions(content)

        # Ensure we have at least some questions
        if not sub_questions:
            sub_questions = [
                f"What is {query}?",
                f"What are the latest developments in {query}?",
                f"What are the key challenges in {query}?",
            ]

        # Limit to 5 sub-questions max
        sub_questions = sub_questions[:5]

        print(f"Manager generated {len(sub_questions)} sub-questions:")
        for i, q in enumerate(sub_questions, 1):
            print(f"  {i}. {q}")

        return {
            "sub_questions": sub_questions,
            "status_updates": [
                f"Manager: Decomposed query into {len(sub_questions)} sub-questions"
            ],
        }

    except Exception as e:
        print(f"Manager error: {e}")
        # Fallback: create basic sub-questions
        fallback = [
            f"What is {query}?",
            f"What are recent developments in {query}?",
            f"What are the main challenges and future directions for {query}?",
        ]
        return {
            "sub_questions": fallback,
            "status_updates": [
                f"Manager: Created {len(fallback)} fallback sub-questions (error: {str(e)[:50]})"
            ],
        }


def _parse_questions(content: str) -> list[str]:
    """Parse sub-questions from LLM response.

    Tries JSON parsing first, falls back to line-by-line extraction.
    """
    # Try direct JSON parse
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return [str(q).strip() for q in data if str(q).strip()]
    except json.JSONDecodeError:
        pass

    # Try to find JSON array in the response
    try:
        start = content.find("[")
        end = content.rfind("]") + 1
        if start != -1 and end > start:
            data = json.loads(content[start:end])
            if isinstance(data, list):
                return [str(q).strip() for q in data if str(q).strip()]
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: extract lines that look like questions
    lines = content.split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        # Remove numbering and bullets
        for prefix in ["- ", "* ", "1.", "2.", "3.", "4.", "5.", "1)", "2)", "3)", "4)", "5)"]:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
        # Remove quotes
        line = line.strip("\"'")
        if line and len(line) > 10 and "?" in line:
            questions.append(line)

    return questions