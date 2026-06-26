from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse
from app.agent.agent_executor import run_agent
from app.services.logger_service import get_logger

router = APIRouter()
logger = get_logger("chat_api")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    POST /chat
    Takes ChatRequest, runs the AI agent executor, and returns a ChatResponse.
    Catches any internal errors to return a user-friendly 500 JSON message.
    """
    logger.info(f"Received chat request for session '{request.session_id}'")
    if not request.message or not request.message.strip():
        logger.warning(f"Received empty or whitespace-only message for session '{request.session_id}'")
        return ChatResponse(
            response="Please enter a message. I cannot process an empty question.",
            session_id=request.session_id,
            reasoning_steps=["Received empty or whitespace-only input message. Aborted processing."],
            tool_calls=[],
            used_rag=False
        )
    try:
        # Run agent executor synchronously
        result = run_agent(question=request.message, session_id=request.session_id)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Internal error processing chat request for session '{request.session_id}': {e}", exc_info=True)
        # Return a clean 500 without leaking stack traces
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "response": "I'm sorry, I'm having some trouble processing your request right now. Please try again later.",
                "session_id": request.session_id,
                "reasoning_steps": ["An unexpected error occurred during request processing."],
                "tool_calls": [],
                "used_rag": False
            }
        )
