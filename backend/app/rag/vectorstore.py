import os
from langchain_community.vectorstores import FAISS
from app.services.gemini_service import embeddings
from app.services.logger_service import get_logger
from app.rag.ingest import build_index

logger = get_logger("vectorstore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_INDEX_DIR = os.path.join(BASE_DIR, "data", "faiss_index")

def load_vectorstore():
    """Loads the FAISS index from disk. Rebuilds it using build_index() if missing."""
    faiss_file = os.path.join(FAISS_INDEX_DIR, "index.faiss")
    pkl_file = os.path.join(FAISS_INDEX_DIR, "index.pkl")
    
    if not (os.path.exists(faiss_file) and os.path.exists(pkl_file)):
        logger.info("Local FAISS files not found. Initiating ingestion on startup...")
        return build_index()

    try:
        logger.info(f"Loading local FAISS vector store from {FAISS_INDEX_DIR}...")
        # Since LangChain 0.1.0, loading local pickle files requires allow_dangerous_deserialization=True
        db = FAISS.load_local(
            FAISS_INDEX_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info("FAISS vector store loaded successfully.")
        return db
    except Exception as e:
        logger.warning(f"Error loading local FAISS index: {e}. Rebuilding from policy files...")
        return build_index()
