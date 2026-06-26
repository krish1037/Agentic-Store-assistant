import os
import pytest
import httpx
from app.main import app

# Check for API key to skip integration tests if missing
has_api_key = bool(os.getenv("GOOGLE_API_KEY"))

@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Run integration tests only if GOOGLE_API_KEY is present
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not has_api_key, reason="GOOGLE_API_KEY environment variable is not set. Skipping integration tests.")
]

import time

@pytest.fixture(autouse=True)
def rate_limit_delay():
    yield
    if has_api_key:
        time.sleep(12)

@pytest.mark.asyncio
async def test_agent_order_status():
    payload = {
        "message": "Where is order ORD-1002?",
        "session_id": "test-session-1"
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "response" in data
    assert data["session_id"] == "test-session-1"
    assert len(data["reasoning_steps"]) > 0
    assert data["used_rag"] is False
    
    # Verify tool calls
    tool_names = [tc["tool_name"] for tc in data["tool_calls"]]
    assert "get_order" in tool_names
    
    # Verify order id in input
    order_inputs = [tc["tool_input"].get("order_id", "").upper() for tc in data["tool_calls"] if tc["tool_name"] == "get_order"]
    assert "ORD-1002" in order_inputs

@pytest.mark.asyncio
async def test_agent_product_info():
    payload = {
        "message": "Tell me about product P101",
        "session_id": "test-session-2"
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "response" in data
    assert data["used_rag"] is False
    
    tool_names = [tc["tool_name"] for tc in data["tool_calls"]]
    assert "get_product" in tool_names

@pytest.mark.asyncio
async def test_agent_cheaper_alternative():
    payload = {
        "message": "Is there a cheaper alternative to the shoes in order ORD-1002?",
        "session_id": "test-session-3"
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "response" in data
    tool_names = [tc["tool_name"] for tc in data["tool_calls"]]
    
    # Should call get_order, get_product, and search_products in a chain
    assert "get_order" in tool_names
    assert "get_product" in tool_names
    assert "search_products" in tool_names
    assert "aerostep" in data["response"].lower() or "cheaper" in data["response"].lower()

@pytest.mark.asyncio
async def test_agent_policy_question():
    payload = {
        "message": "Can I return my shoes after 15 days?",
        "session_id": "test-session-4"
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "response" in data
    assert data["used_rag"] is True
    
    tool_names = [tc["tool_name"] for tc in data["tool_calls"]]
    assert "search_store_policy" in tool_names

@pytest.mark.asyncio
async def test_agent_conversational_memory():
    session_id = "test-session-5"
    
    payload1 = {
        "message": "Where is order ORD-1002?",
        "session_id": session_id
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response1 = await ac.post("/chat", json=payload1)
        assert response1.status_code == 200
        
        payload2 = {
            "message": "Does it contain shoes?",
            "session_id": session_id
        }
        response2 = await ac.post("/chat", json=payload2)
        assert response2.status_code == 200
        data2 = response2.json()
        
    tool_names = [tc["tool_name"] for tc in data2["tool_calls"]]
    assert "get_order" in tool_names
    order_inputs = [tc["tool_input"].get("order_id", "").upper() for tc in data2["tool_calls"] if tc["tool_name"] == "get_order"]
    assert "ORD-1002" in order_inputs

@pytest.mark.asyncio
async def test_agent_invalid_order():
    payload = {
        "message": "Where is order ORD-9999?",
        "session_id": "test-session-6"
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "response" in data
    assert "could not be found" in data["response"].lower() or "not found" in data["response"].lower() or "sorry" in data["response"].lower()
    tool_names = [tc["tool_name"] for tc in data["tool_calls"]]
    assert "get_order" in tool_names

@pytest.mark.asyncio
async def test_history_endpoint():
    session_id = "test-session-7"
    payload = {
        "message": "Hello, who are you?",
        "session_id": session_id
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/chat", json=payload)
        response = await ac.get(f"/history/{session_id}")
        
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert len(data["messages"]) >= 2
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][1]["role"] == "assistant"
