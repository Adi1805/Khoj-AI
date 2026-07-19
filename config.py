"""Configuration and shared resources for DeepResearch AI.

Smart model fallback chain with auto-retry for rate limits.
Each Gemini model has its own separate free-tier daily quota.

Fallback: gemini-2.5-flash -> gemini-2.0-flash -> gemini-2.0-flash-lite
"""

import os
import time
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
    raise ValueError(
        "\n\n!! GOOGLE_API_KEY not configured!\n\n"
        "To fix this:\n"
        "1. Get your FREE API key from: https://aistudio.google.com/apikey\n"
        "2. Create a .env file in the project root (copy from .env.example)\n"
        "3. Paste your API key in the .env file\n"
    )

# Each model has its own separate daily quota on the free tier
MODEL_FALLBACK_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

# Track which models are known to be exhausted (daily quota)
_exhausted_models = set()


class RetryLLM:
    """Wrapper with auto-retry AND model fallback for rate limits."""

    def __init__(self, temperature=0.0, max_retries=3):
        self.temperature = temperature
        self.max_retries = max_retries

    def _create_llm(self, model_name):
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GOOGLE_API_KEY,
            temperature=self.temperature,
            max_output_tokens=8192,
        )

    def invoke(self, prompt, **kwargs):
        """Invoke with automatic retry + model fallback on rate limits."""
        global _exhausted_models

        # Build list: try non-exhausted models first, then exhausted as last resort
        models_to_try = [m for m in MODEL_FALLBACK_CHAIN if m not in _exhausted_models]
        models_to_try += [m for m in MODEL_FALLBACK_CHAIN if m in _exhausted_models]

        last_error = None

        for model_name in models_to_try:
            llm = self._create_llm(model_name)

            for attempt in range(self.max_retries):
                try:
                    result = llm.invoke(prompt, **kwargs)
                    _exhausted_models.discard(model_name)
                    if model_name != MODEL_FALLBACK_CHAIN[0]:
                        print(f"    >> Success with fallback model: {model_name}")
                    return result
                except Exception as e:
                    error_str = str(e)
                    last_error = e

                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        is_daily = "limit: 0" in error_str or "PerDay" in error_str

                        if is_daily:
                            print(f"    >> Daily quota exhausted for {model_name}. Trying next model...")
                            _exhausted_models.add(model_name)
                            break

                        wait_time = self._extract_wait_time(error_str)
                        wait_time = max(wait_time, 5) + 2

                        if attempt < self.max_retries - 1:
                            print(f"    >> Rate limited ({model_name}). Waiting {wait_time:.0f}s ({attempt+1}/{self.max_retries})...")
                            time.sleep(wait_time)
                        else:
                            print(f"    >> Retries exhausted for {model_name}. Trying next model...")
                            _exhausted_models.add(model_name)
                            break
                    elif "404" in error_str or "NOT_FOUND" in error_str:
                        print(f"    >> Model {model_name} not available. Trying next model...")
                        _exhausted_models.add(model_name)
                        break
                    else:
                        print(f"    >> Error with {model_name}: {str(e)[:80]}. Trying next model...")
                        break

        if last_error:
            raise last_error
        raise RuntimeError("All models in fallback chain failed.")

    def _extract_wait_time(self, error_str):
        match = re.search(r"retry in ([\d.]+)s", error_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
        match = re.search(r"retryDelay.*?([\d.]+)s", error_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return 10.0


def get_llm(temperature=0.0):
    """Get a configured LLM with auto-retry and model fallback."""
    return RetryLLM(temperature=temperature, max_retries=3)


def get_embeddings():
    """Get HuggingFace embeddings model (runs locally, free)."""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
