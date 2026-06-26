import os
import pytest
from app.rag.vectorstore import load_vectorstore
from app.rag.retriever import search_store_policy

# Automatically skip RAG tests if Gemini API key is missing
pytestmark = pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY environment variable is not set. Skipping RAG tests."
)

def test_load_and_query_vectorstore():
    # Load vector store (should build index if missing)
    db = load_vectorstore()
    assert db is not None

    # Search for return policy content
    docs_and_scores = db.similarity_search_with_relevance_scores("return policy", k=2)
    assert len(docs_and_scores) > 0
    # The score should be reasonable (e.g. > 0.1)
    doc, score = docs_and_scores[0]
    assert doc.metadata["source"] in ["returns.txt", "refunds.txt", "shipping.txt"]

def test_search_store_policy_tool_found():
    # Call the tool with a query that should yield matches
    result = search_store_policy.invoke({"query": "return window period"})
    assert result["found"] is True
    assert len(result["excerpts"]) > 0
    assert "returns.txt" in result["sources"]

def test_search_store_policy_tool_not_found():
    # Call the tool with a gibberish query that should fall below the threshold
    result = search_store_policy.invoke({"query": "qwertyuiopasdfghjklzxcvbnm quantum physics"})
    assert result["found"] is False
    assert result["excerpts"] == []
    assert "error" in result
