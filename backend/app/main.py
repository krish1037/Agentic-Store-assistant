import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.chat import router as chat_router
from app.api.history import router as history_router
from app.api.health import router as health_router
from app.rag.vectorstore import load_vectorstore
from app.services.logger_service import get_logger

# Load env variables at main module load
load_dotenv()

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Executes load_vectorstore on startup to prep FAISS vector search and verify connection/keys,
    crashing the boot process immediately if dependencies are misconfigured.
    """
    logger.info("Initializing Agentic Store Assistant application lifespan...")
    try:
        # Load or generate FAISS index on startup to verify setup and prevent cold start request delay
        logger.info("Verifying store policy database index...")
        load_vectorstore()
        logger.info("Policy database verification completed successfully. Service is ready.")
    except Exception as e:
        logger.critical(f"App startup verification failed: {e}. Fail-fast triggered.", exc_info=True)
        # Propagate startup error to crash the container/process
        raise e
    yield
    logger.info("Shutting down Agentic Store Assistant application lifespan...")

app = FastAPI(
    title="Agentic Store Assistant Backend",
    description="FastAPI backend orchestration for customer support LLM agent.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

allowed_origin = os.getenv("ALLOWED_ORIGIN")

if allowed_origin:
    origins.append(allowed_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
app.include_router(chat_router, tags=["chat"])
app.include_router(history_router, tags=["history"])
app.include_router(health_router, tags=["health"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Running FastAPI app locally on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
