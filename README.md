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
