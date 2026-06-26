# System Design & Architectural Decisions

**Author**: Krish Sharma  
**Project**: Agentic Store Assistant Backend & Frontend  

This document outlines the core design decisions, architectural tradeoffs, and implementation rationales behind the Agentic Store Assistant application.

---

## 1. Tool Selection: LangChain's Tool-Calling Agent Pattern

Instead of building a hardcoded `if/else` query classifier or regex-based router, we selected LangChain's **Tool-Calling Agent pattern** (`create_tool_calling_agent` utilizing the `gemini-2.5-flash` model).

### Rationale
* **Dynamic Chaining & Reasoning**: A hardcoded dispatcher cannot handle multi-step reasoning. For example, if a customer asks, *"Is there a cheaper alternative to the shoes in my order ORD-1002?"*, a rigid router would fail because the system needs to dynamically execute a chain of calls:
  1. Retrieve order content (`get_order`).
  2. Inspect the product details (`get_product`) to identify category and price.
  3. Search the catalog (`search_products`) with filters.
  4. Synthesize the final comparison.
  The tool-calling model allows the LLM to output structured function calls sequentially, inspect outputs from previous steps, and decide the next tool to call until it is ready to formulate the final answer.
* **Flexible Parameter Resolution**: The agent translates natural language queries into exact function schemas (e.g., extracting and capitalizing order IDs like `ORD-1002` or applying `max_price=80` from context).

---

## 2. RAG Layer: FAISS + Gemini Embeddings

For retrieving store policies, we implemented a Retrieval-Augmented Generation (RAG) system using `FAISS` and the `models/gemini-embedding-001` model.

### Relevance Score Thresholding
* **Strict Factuality Constraint**: A key requirement of the assignment is that the agent **must not fabricate data**. By default, vector similarity searches (such as Euclidean L2 distance in FAISS) will return the closest match regardless of whether it actually answers the user's question. For example, asking *"What is the capital of France?"* will still pull chunks from returns or shipping policy files with a high score (around `0.79`).
* **The Threshold Solution**: We introduced a strict relevance threshold of **`0.80`** in `search_store_policy`. If the highest similarity score falls below `0.80` (as nonsense or off-topic queries do), the tool returns `found: False`. This prevents the agent from attempting to synthesize policy answers from irrelevant text chunks.

---

## 3. Graceful Error Handling & Factuality Guardrails

To address the requirements of **"handling invalid orders/products gracefully"** and **"not fabricating data"**, we designed a two-tiered guardrail system:

### Structured Tool Return Design
Rather than throwing Python exceptions (which could crash the thread or result in a generic 500 error), all lookups (`get_order`, `get_product`, `search_products`) return a standardized dictionary structured as:
```json
{
  "found": false,
  "error": "Reason description"
}
```
This structured feedback communicates the exact state back to the LLM agent.

### System Prompt Reinforcement
The LLM is strictly instructed in the system prompt:
* *"NEVER fabricate or make up any order details, product information, or policies."*
* *"If a tool search returns no results or indicates that the item was not found (`found: False`), state that clearly and apologize. Do not invent products, orders, or facts."*

By pairing structured tool outputs with explicit prompt constraints, the agent gracefully responds with a friendly apology (e.g., *"I'm sorry, I couldn't find order ORD-9999 in our system."*) rather than hallucinating details.

---

## 4. Memory Management: RunnableWithMessageHistory

Conversational memory is supported via `RunnableWithMessageHistory` and session identifiers:
* **Session Isolation**: Each conversation is bound to a unique `session_id`. Messages are appended to an in-memory session repository.
* **Contextual Resolution**: The agent can resolve relative pronouns in follow-up queries (e.g., turn 1: *"Where is order ORD-1002?"* → turn 2: *"Does it contain shoes?"*).
* **Limitations**: Currently, history is stored in an ephemeral, single-process python dictionary. If the application server restarts, or if it is scaled horizontally, session state is lost.

---

## 5. UI Enhancements: Transparency & Memory Panels

To go beyond the base requirements, two advanced dashboard features were designed:
1. **Agent Transparency Panel (ToolCallPanel)**: A collapsible layout that displays the raw step-by-step reasoning of the agent (Question → Thought → Tool Execution → Output). It renders the exact arguments passed to the functions and the raw JSON returned from the backend. 
2. **Memory Badge Notification**: An active marker that signals to the user when conversational memory is actively carrying context over to resolve follow-up questions.

### Rationale
These were added to make the underlying agentic behavior (tool selection, chaining, RAG, and memory) **directly visible and verifiable** to the user. Rather than having the user blind-trust the final text answer, they can visually inspect the execution chain to confirm that the RAG tool retrieved the correct file or that the correct SQL-like catalog search filters were applied.

---

## 6. Tradeoffs & Production Considerations

If scaling this system to production, the following architecture tradeoffs would be made:
* **Persistent Session Store**: Replace the in-memory session dictionary with a Redis or DynamoDB backed LangChain history store to support horizontal scaling.
* **Persistent Relational Databases**: Transition the mock `orders.json` and `products.json` databases into a transactional relational database (e.g., PostgreSQL) with proper foreign keys and index lookup schemas.
* **User Authentication & Authorization**: Add authentication tokens (JWT) to secure endpoints and ensure customers can only query orders matching their authenticated account ID.
