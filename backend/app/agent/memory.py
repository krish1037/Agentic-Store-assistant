from langchain_community.chat_message_histories import ChatMessageHistory

# Simple module-level dictionary to store session histories in memory.
#
# IMPORTANT PRODUCTION NOTE:
# This in-memory storage is suitable ONLY for single-instance, local demonstration purposes.
# In a production cloud deployment (e.g., Google Cloud Run, Kubernetes, or multi-instance environments),
# this dictionary will NOT persist across container restarts and will NOT be shared among multiple scaled instances.
# For production, replace this with a Redis-backed message history (e.g., RedisChatMessageHistory)
# or a database-backed history store (e.g., PostgreSQL or Firestore).
store_session_history = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    """
    Retrieves or initializes the chat message history for the given session_id.
    """
    if session_id not in store_session_history:
        store_session_history[session_id] = ChatMessageHistory()
    return store_session_history[session_id]
