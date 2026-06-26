import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.services.gemini_service import embeddings
from app.services.logger_service import get_logger

logger = get_logger("rag_ingest")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICIES_DIR = os.path.join(BASE_DIR, "data", "store_policies")
FAISS_INDEX_DIR = os.path.join(BASE_DIR, "data", "faiss_index")

def build_index():
    """Reads store policy text files, chunks them, computes embeddings, and builds a local FAISS index."""
    logger.info("Starting FAISS vector index building process...")
    
    if not os.path.exists(POLICIES_DIR):
        err_msg = f"Store policies directory not found at {POLICIES_DIR}"
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)
        
    policy_files = ["shipping.txt", "returns.txt", "refunds.txt"]
    documents = []
    
    for filename in policy_files:
        filepath = os.path.join(POLICIES_DIR, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Expected policy file missing: {filepath}")
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Keep metadata describing which policy file it came from
            documents.append({
                "page_content": content,
                "metadata": {"source": filename}
            })
            logger.info(f"Loaded document: {filename} ({len(content)} characters)")
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            
    if not documents:
        err_msg = "No policy documents loaded. Ingestion cannot proceed."
        logger.error(err_msg)
        raise ValueError(err_msg)

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunked_docs = []
    
    for doc in documents:
        chunks = text_splitter.split_text(doc["page_content"])
        for chunk in chunks:
            # We create structured mock objects that match LangChain document structures
            # or just pass strings and metadata to the FAISS from_texts function.
            chunked_docs.append({
                "text": chunk,
                "metadata": doc["metadata"]
            })
            
    logger.info(f"Split {len(documents)} document(s) into {len(chunked_docs)} chunks.")

    texts = [c["text"] for c in chunked_docs]
    metadatas = [c["metadata"] for c in chunked_docs]

    # Create and save FAISS index
    try:
        os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
        db = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
        db.save_local(FAISS_INDEX_DIR)
        logger.info(f"FAISS index successfully built and saved to {FAISS_INDEX_DIR}")
        return db
    except Exception as e:
        logger.error(f"Failed to generate FAISS index: {e}")
        raise e

if __name__ == "__main__":
    build_index()
