# Agentic Store Assistant

This is the basic Agentic bot which answers your query regarding the Store (Order details, Product Details, Return policy, Status, etc.).


Agentic Store Assistant is a full-stack, state-of-the-art customer support assistant dashboard powered by a LangChain agent using the `gemini-2.5-flash` model. The assistant answers customer questions regarding orders, product details, and store policies (shipping, returns, and refunds) by dynamically selecting and chaining tools or retrieving contextual policy documents using RAG (Retrieval-Augmented Generation) from a local vector database. The application features a high-fidelity React frontend that displays real-time agent transparency (reasoning steps, tool execution arguments, and raw JSON outputs) alongside a conversation sidebar with active memory tracking.

LIVE DEMO LINK :-https://agentic-store-assistant.web.app 

---

## System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                      Frontend                          │
│         (Vite + React + TS + Tailwind CSS)             │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP REST Requests
                           ▼
┌────────────────────────────────────────────────────────┐
│                  FastAPI Backend                       │
│    (Port 8080 - CORS allowed for frontend ports)       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                LangChain Orchestrator                  │
│       (RunnableWithMessageHistory / Session Memory)    │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
               ▼ (Tool Selection)         ▼ (RAG Retrieval)
┌──────────────────────────────┐  ┌──────────────────────┐
│       Agent Tools            │  │  search_store_policy │
│  (get_order, get_product,    │  │        (Tool)        │
│   search_products)           │  │                      │
└──────────────┬───────────────┘  └──────────┬───────────┘
               │                             │
               ▼                             ▼
┌──────────────────────────────┐  ┌──────────────────────┐
│     JSON Databases           │  │  FAISS Vector Store  │
│ (orders.json, products.json) │  │(gemini-embedding-001)│
└──────────────────────────────┘  └──────────────────────┘
```

---

## Setup & Running Instructions

### Prerequisites
* Python 3.10+
* Node.js v18+
* A valid Gemini API Key (`GOOGLE_API_KEY`)

### Backend Setup
1. Open a terminal and navigate to the backend directory:
   ```powershell
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install the dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Create a `.env` file in `backend/` and add your key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
5. Ingest policy documents (`shipping.txt`, `returns.txt`, `refunds.txt`) to build the FAISS vector database:
   ```powershell
   python -c "from app.rag.ingest import build_index; build_index()"
   ```
6. Start the FastAPI development server:
   ```powershell
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

### Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Install the frontend dependencies:
   ```powershell
   npm install
   ```
3. Create a `.env` file in `frontend/` to point to the backend URL:
   ```env
   VITE_API_BASE_URL=http://localhost:8080
   ```
4. Run the Vite development server:
   ```powershell
   npm run dev
   ```
   *Note: If port 5173 is in use, Vite will automatically fall back to port 5174. The backend CORS is preconfigured to accept connections from both `http://localhost:5173` and `http://localhost:5174`.*

---

## Core Engine Mechanics

### 1. Tool Selection & Chaining
The system utilizes LangChain's `create_tool_calling_agent` pattern. When a user sends a query, the `gemini-2.5-flash` model evaluates the defined functions (`get_order`, `get_product`, `search_products`, `search_store_policy`) and outputs a function call rather than text. If a query requires chaining, the model executes tools sequentially. For example, if asked *"Is there a cheaper alternative to the shoes in my order ORD-1002?"*, the agent:
1. Invokes `get_order(order_id="ORD-1002")` to retrieve Bob Jones' items.
2. Invokes `get_product(product_id="P101")` to determine the category (`shoes`) and price (`$80.00`) of the ordered item.
3. Invokes `search_products(category="shoes", max_price=79.99, exclude_product_id="P101")` to locate a cheaper alternative.
4. Synthesizes the results into a human-friendly customer response.

### 2. Conversational Memory
Conversational memory is managed using LangChain's `RunnableWithMessageHistory` and backed by a session-scoped dictionary:
* Each request includes a `session_id`.
* The server fetches or creates a `ChatMessageHistory` object for the given `session_id`.
* The history is fed into the LLM context via a `MessagesPlaceholder(variable_name="chat_history")`.
* In-memory storage resolves pronouns and references across turns. (e.g. Turn 1: *"Where is order ORD-1002?"* → Turn 2: *"Does it contain shoes?"* successfully resolves "it" to "ORD-1002" and retrieves order details).

### 3. Retrieval-Augmented Generation (RAG)
Policy queries are answered strictly using RAG:
* Raw policy documents (`shipping.txt`, `returns.txt`, `refunds.txt`) are chunked and embedded using `models/gemini-embedding-001` (with `output_dimensionality=768`).
* The chunks are indexed in a local `FAISS` vector store.
* The `search_store_policy` tool uses `similarity_search_with_relevance_scores` with a strict threshold of **`0.80`** to filter out irrelevant or nonsense questions, preventing hallucinated answers.

---

## Real Live Query Traces

Here are the authentic responses captured from the live agent executor:

### Scenario 1: Order Status Lookup
* **Input**: *"Where is order ORD-1002?"*
* **Response**:
  ```text
  "Your order ORD-1002 is currently shipped and is expected to be delivered by June 26, 2026."
  ```
* **Tool Call Trace**:
  ```json
  {
    "tool_name": "get_order",
    "tool_input": { "order_id": "ORD-1002" },
    "tool_output": {
      "found": true,
      "order_id": "ORD-1002",
      "customer_name": "Bob Jones",
      "status": "shipped",
      "expected_delivery_date": "2026-06-26",
      "total_amount": 130.0
    }
  }
  ```

### Scenario 2: Product Specifications Lookup
* **Input**: *"Tell me about product P101"*
* **Response**:
  ```text
  "The P101 Stride Lite Running Shoes are in the 'shoes' category. They are lightweight and breathable, with high-performance cushioning, perfect for daily training and long distances. They cost $80, are in stock, and have a customer rating of 4.6."
  ```
* **Tool Call Trace**:
  ```json
  {
    "tool_name": "get_product",
    "tool_input": { "product_id": "P101" },
    "tool_output": {
      "found": true,
      "product_id": "P101",
      "name": "Stride Lite Running Shoes",
      "price": 80.0,
      "in_stock": true
    }
  }
  ```

### Scenario 3: Cheaper Alternative Tool-Chaining
* **Input**: *"Is there a cheaper alternative to the shoes in my order ORD-1002?"*
* **Response**:
  ```text
  "Yes, I found a cheaper alternative to the Stride Lite Running Shoes (P101) from your order ORD-1002:
  
  * AeroStep Training Shoes (P102): These are cross-training athletic shoes priced at $45. They offer stability, comfort, and flexibility for gym workouts and casual wear.
  
  There are also AeroStep Comfort Insoles (P111) for $15, but these are insoles and not a full shoe."
  ```
* **Tool Call Trace**:
  1. `get_order(order_id="ORD-1002")` -> Found item P101.
  2. `get_product(product_id="P101")` -> Categorized as shoes, price is $80.00.
  3. `search_products(category="shoes", max_price=79.99, exclude_product_id="P101")` -> Found P102 ($45.00) and P111 ($15.00).

### Scenario 4: Policy Question via RAG
* **Input**: *"Can I return my shoes after 15 days?"*
* **Response**:
  ```text
  "Yes, you can return shoes after 15 days. Our standard return policy allows returns within 30 days of the delivery date, so 15 days is well within that window. Please ensure the shoes are in their original, unused, and unworn condition..."
  ```
* **Tool Call Trace**:
  ```json
  {
    "tool_name": "search_store_policy",
    "tool_input": { "query": "return window period" },
    "tool_output": {
      "found": true,
      "excerpts": [
        "Our standard returns policy allows you to return products within 30 days of the delivery date. Items returned after this 30-day window cannot be accepted..."
      ],
      "sources": ["returns.txt"]
    }
  }
  ```

### Scenario 5: Off-topic / Out-of-Range Handling
* **Input**: *"What is the capital of France?"*
* **Response**:
  ```text
  "I'm sorry, that is out of our range."
  ```

---

## Testing

To run the comprehensive test suite (including tools, RAG thresholds, and backend API integration endpoints):
```powershell
# Navigate to the backend directory
cd backend

# Run the pytest suite
.\venv\Scripts\pytest.exe -v
```

---

## Known Limitations

* **Ephemeral In-Memory Session Memory**: Conversation history and session tracking are currently stored in a local Python dictionary (`dict`) in backend memory. If the backend server restarts, crashes, or scales out across multiple instances behind a load balancer, all historical conversational context and active user sessions will be lost. For a production deployment, this in-memory store must be replaced by a persistent store like Redis or PostgreSQL.
