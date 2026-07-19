"""ChromaDB vector store for storing and retrieving research findings.

Uses HuggingFace embeddings (local, free) to convert text into vectors
and ChromaDB (local, free) to store and search them by semantic similarity.
"""

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from src.config import get_embeddings


class ResearchVectorStore:
    """Manages a ChromaDB vector store for caching and retrieving research data.

    Usage:
        store = ResearchVectorStore()
        store.add_findings([{"content": "...", "source": "...", "url": "..."}])
        results = store.search("quantum computing")
    """

    def __init__(self, collection_name: str = "research_findings"):
        """Initialize the vector store.

        Args:
            collection_name: Name of the ChromaDB collection to use.
        """
        self.embeddings = get_embeddings()
        self.collection_name = collection_name
        self._vectorstore = None

    @property
    def vectorstore(self) -> Chroma:
        """Lazy-initialize the ChromaDB vector store."""
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )
        return self._vectorstore

    def add_findings(self, findings: list[dict]) -> None:
        """Store research findings in the vector store.

        Args:
            findings: List of dicts with keys: content, source, url, source_type
        """
        documents = []
        for finding in findings:
            content = finding.get("content", "")
            if not content.strip():
                continue

            doc = Document(
                page_content=content,
                metadata={
                    "source": finding.get("source", "unknown"),
                    "source_type": finding.get("source_type", "web"),
                    "url": finding.get("url", ""),
                },
            )
            documents.append(doc)

        if documents:
            self.vectorstore.add_documents(documents)

    def search(self, query: str, k: int = 5) -> list[Document]:
        """Search for semantically similar findings.

        Args:
            query: The search query.
            k: Number of results to return.

        Returns:
            List of matching Document objects with content and metadata.
        """
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception:
            return []

    def clear(self) -> None:
        """Clear all stored findings and reset the vector store."""
        self._vectorstore = None