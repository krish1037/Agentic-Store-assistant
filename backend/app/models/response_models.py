from typing import Any, Literal
from pydantic import BaseModel, Field

class ToolCallRecord(BaseModel):
    tool_name: str = Field(..., description="The name of the tool called by the agent.")
    tool_input: dict = Field(..., description="The input parameters passed to the tool.")
    tool_output: Any = Field(..., description="The result or output returned by the tool.")
    status: Literal["success", "error"] = Field(..., description="The outcome of the tool call.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The agent's final customer-facing response.")
    session_id: str = Field(..., description="The conversation session ID.")
    reasoning_steps: list[str] = Field(default_factory=list, description="Programmatic reasoning steps indicating what actions the agent completed.")
    tool_calls: list[ToolCallRecord] = Field(default_factory=list, description="A record of tool calls and details triggered during this turn.")
    used_rag: bool = Field(..., description="Whether the store policy RAG retrieval tool was invoked during this chat turn.")

class HistoryResponse(BaseModel):
    session_id: str = Field(..., description="The conversation session ID.")
    messages: list[dict] = Field(default_factory=list, description="The sequence of messages in the session, each containing role, content, and timestamp.")
