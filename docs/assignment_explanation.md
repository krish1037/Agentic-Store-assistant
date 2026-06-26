# Assignment Requirements Mapping

This document maps the original assignment specifications and evaluation criteria directly to the files and code blocks in this repository.

---

## 1. Assignment Requirements Mapping

### Requirement: Order Status Query
* **Goal**: Retrieve status for a valid order ID.
* **Code Location**: 
  - [tools.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/tools.py#L11-L40): The `get_order` tool loads `orders.json` and finds the order case-insensitively.
  - [agent_executor.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/agent_executor.py#L97-L130): The agent catches the lookup, records the reasoning step, and parses it.

### Requirement: Product Info Query
* **Goal**: Retrieve specifications for a valid product ID.
* **Code Location**:
  - [tools.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/tools.py#L42-L71): The `get_product` tool queries `products.json` by ID.
  - [agent_executor.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/agent_executor.py#L131-L133): The agent logs product lookup steps and synthesizes info.

### Requirement: Cheaper Alternative Query (Multi-Tool Chaining)
* **Goal**: Find cheaper alternatives in the same category excluding the original item.
* **Code Location**:
  - [tools.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/tools.py#L73-L113): The `search_products` tool handles category filtering, price bounds, and exclusions.
  - [prompts.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/prompts.py#L7-L11): System prompt trains the LLM on chaining `get_order` → `get_product` → `search_products`.

### Requirement: Policy Questions (RAG)
* **Goal**: Answer policy questions (shipping, returns, refunds) via document retrieval.
* **Code Location**:
  - [ingest.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/rag/ingest.py): Chunks and indexes policy text files using `gemini-embedding-001`.
  - [retriever.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/rag/retriever.py#L21-L90): `search_store_policy` performs similarity search with a strict `0.80` relevance score cutoff.

---

## 2. Weighted Evaluation Criteria Mapping

### Tool Selection (30% Weight)
* **How It is Satisfied**: Built via LangChain's function-calling agent interface using the `gemini-2.5-flash` model ([agent_executor.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/agent_executor.py#L29-L38)). The model automatically selects functions based on description docstrings instead of utilizing rigid regex or router classification.

### Reasoning and Chaining (25% Weight)
* **How It is Satisfied**: The system prompt instructs the agent on multi-tool sequence lookup ([prompts.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/prompts.py#L4-L12)). The React frontend renders a dedicated collapsible transparency panel displaying the exact execution sequence ([ToolCallPanel.tsx](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/frontend/src/components/ToolCallPanel.tsx)).

### Error Handling (20% Weight)
* **How It is Satisfied**: Tools return safe status states (`found: False`) rather than crashing ([tools.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/tools.py#L32)). Prompt rules enforce strict factual compliance ([prompts.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/prompts.py#L17-L20)), and we've added a strict `0.80` RAG threshold to handle off-topic/nonsense queries gracefully.

### Code Quality and Documentation (15% Weight)
* **How It is Satisfied**: Code is highly structured, modular, and type-checked (both python typings and TypeScript interfaces). Covered by full automated testing suites ([test_tools.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/tests/test_tools.py) and [test_rag.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/tests/test_rag.py)) alongside detailed documentation.

### UX of Responses (10% Weight)
* **How It is Satisfied**: Responses are translated from raw JSON dictionaries into polite, natural customer service sentences ([prompts.py](file:///c:/Users/Krish%20Sharma/Desktop/Task/agentic-store-assistant/backend/app/agent/prompts.py#L26-L29)). The UI renders reasoning logs, active database state tables, and collapsible transparency panels to provide a premium user experience.
