import datetime
from fastapi import APIRouter
from app.models.response_models import HistoryResponse
from app.agent.memory import get_session_history, store_session_history
from app.services.logger_service import get_logger

router = APIRouter()
logger = get_logger("history_api")

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    GET /history/{session_id}
    Retrieves the formatted message history for the given session_id.
    Returns a 200 response with empty messages if the session_id is not yet active.
    """
    logger.info(f"Retrieving message history for session '{session_id}'")
    
    if session_id not in store_session_history:
        logger.info(f"Session '{session_id}' not found in history store. Returning empty list.")
        return HistoryResponse(session_id=session_id, messages=[])

    history = get_session_history(session_id)
    formatted_messages = []

    # Map LangChain message objects to expected output dictionary structure
    for msg in history.messages:
        role = "user"
        if msg.type == "ai":
            role = "assistant"
        elif msg.type == "system":
            role = "system"
            
        # Get timestamp if stored in additional_kwargs, or use fallback
        timestamp = msg.additional_kwargs.get("timestamp")
        if not timestamp:
            timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        formatted_messages.append({
            "role": role,
            "content": msg.content,
            "timestamp": timestamp
        })

    return HistoryResponse(session_id=session_id, messages=formatted_messages)
