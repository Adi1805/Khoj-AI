# **Khoj AI**

A multi-agent research system that takes a single question and returns a fact-checked, fully-cited report — by deploying five specialized AI agents that search the web, read academic papers, cross-verify claims against each other, and write up the findings.

<img width="152" height="37" alt="image" src="https://github.com/user-attachments/assets/8878a194-3e21-49b1-89e0-6d15aafae568" />
<img width="180" height="26" alt="image" src="https://github.com/user-attachments/assets/5293b4a3-348b-4220-8c0b-59eeabe85a37" />
<img width="146" height="26" alt="image" src="https://github.com/user-attachments/assets/b141f400-bac3-4eaf-b5e6-657e6487fd31" />
<img width="127" height="28" alt="image" src="https://github.com/user-attachments/assets/930ef567-688a-440e-8ef4-eafa2c738ad8" />

## **What this is**

Ask Khoj AI something like "latest breakthroughs in fusion energy", and instead of a single LLM call producing a plausible-sounding paragraph, five agents go to work in sequence — breaking the question down, searching the live web and Wikipedia, pulling relevant academic papers from ArXiv, cross-referencing every claim across sources, and only then writing a structured report with a confidence rating attached to each finding.

Khoj (खोज) is Hindi for "search" or "quest" — which is what felt right for a system built specifically to go looking for answers rather than just generating them.

## **Meet the agents**

The pipeline runs as a proper state machine built with LangGraph, not a chain of prompts — each agent reads from and writes to a shared state object, and the graph enforces the order they run in.

| Agent | Job |
|---|---|
| 🧠<br>**Manager** | Breaks the user's question into 3–5 focused, independently-searchable sub-questions |
| 🔍<br>**Web Searcher** | Runs each sub-question through DuckDuckGo and Wikipedia, then uses an LLM to extract the actual findings from the raw results |
| 📄<br>**Paper Reader** | Searches ArXiv for relevant academic papers per sub-question and extracts structured findings — title, authors, key contribution, citation URL |
| ✅<br>**Fact Checker** | Cross-references every claim from both agents above and assigns a confidence level: **HIGH** (3+ sources or an academic paper), **MEDIUM** (2 sources), or **LOW** (single source or contradicting sources) |
| ✍️<br>**Writer** | Synthesizes everything into a structured Markdown report — executive summary, key findings with confidence badges, detailed analysis, academic insights, and a numbered source list |

## Tech Stack

- **LangGraph** — state machine orchestration for the 5-agent pipeline
- **LangChain** — LLM invocation, tool wrapping, prompt templates
- **Google Gemini** (2.5 Flash / 2.0 Flash / 2.0 Flash-Lite) — the underlying LLM, via free-tier API
- **ChromaDB** — local vector store for semantic search over collected findings
- **HuggingFace Sentence Transformers** (`all-MiniLM-L6-v2`) — local embeddings, no API calls
- **Streamlit** — the frontend, with a custom dark-mode glassmorphism UI
- **DuckDuckGo Search, Wikipedia, ArXiv** — the three free, keyless research sources
