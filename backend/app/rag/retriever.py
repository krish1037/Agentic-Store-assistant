import time
from langchain_core.tools import tool
from app.rag.vectorstore import load_vectorstore
from app.services.logger_service import get_logger

logger = get_logger("retriever")

# Load vectorstore once at module load
try:
    db = load_vectorstore()
except Exception as e:
    logger.error(f"Failed to initialize vectorstore at module load: {e}")
    db = None

def get_policy_retriever(k=3):
    """Returns a basic LangChain retriever wrapper from the vector store."""
    if db is None:
        raise ValueError("FAISS vectorstore is not loaded or initialized.")
    return db.as_retriever(search_kwargs={"k": k})

@tool
def search_store_policy(query: str) -> dict:
    """Use this tool to search the store's policies regarding shipping, returns, and refunds.
    It performs a similarity search over the shipping.txt, returns.txt, and refunds.txt policy files
    and returns relevant policy excerpts and their source filenames.
    Use this when the customer asks general policy questions, such as:
    - 'Can I return my shoes after 15 days?'
    - 'What is the return window?'
    - 'How long do refunds take?'
    - 'Do you charge for shipping?'
    - 'Which shipping carriers do you use?'
    Do not call this tool when the customer asks for order status (ORD-XXXX) or product information (P1XX).
    """
    start_time = time.time()
    logger.info(f"Tool search_store_policy invoked with query: '{query}'")
    
    if db is None:
        result = {"found": False, "error": "Store policy search is currently unavailable."}
        latency = (time.time() - start_time) * 1000
        logger.error(f"Tool search_store_policy failed. Database not initialized. Latency: {latency:.2f}ms")
        return result

    try:
        # Perform similarity search with relevance scores to establish relevance thresholds
        # standard FAISS index returns L2 distance or normalized scores.
        # similarity_search_with_relevance_scores returns (doc, score) where score is in [0, 1].
        # Higher score means higher similarity.
        docs_and_scores = db.similarity_search_with_relevance_scores(query, k=3)
        
        # Relevance threshold - below this, documents are considered irrelevant
        threshold = 0.80
        
        excerpts = []
        sources = []
        
        for doc, score in docs_and_scores:
            logger.info(f"Policy match in '{doc.metadata.get('source')}'. Relevance score: {score:.4f}")
            if score >= threshold:
                excerpts.append(doc.page_content)
                sources.append(doc.metadata.get("source", "unknown"))

        latency = (time.time() - start_time) * 1000
        
        if excerpts:
            # Deduplicate sources
            unique_sources = list(set(sources))
            result = {
                "found": True,
                "excerpts": excerpts,
                "sources": unique_sources
            }
            logger.info(f"Tool search_store_policy success. Found {len(excerpts)} matching policy excerpts. Latency: {latency:.2f}ms")
            return result
        else:
            result = {
                "found": False,
                "excerpts": [],
                "sources": [],
                "error": "No relevant policies found matching the query."
            }
            logger.info(f"Tool search_store_policy finished. No matching policies found above threshold. Latency: {latency:.2f}ms")
            return result

    except Exception as e:
        latency = (time.time() - start_time) * 1000
        logger.error(f"Error executing similarity search: {e}. Latency: {latency:.2f}ms")
        return {
            "found": False,
            "error": f"An error occurred while retrieving policies: {str(e)}"
        }
