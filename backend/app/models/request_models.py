from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's query or message for the support agent.")
    session_id: str = Field(..., description="The session identifier to maintain conversation history.")
