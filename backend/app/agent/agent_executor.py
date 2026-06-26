import time
from typing import Any
try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    # pyrefly: ignore [missing-import]
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.services.gemini_service import llm
from app.services.logger_service import get_logger
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tool_router import get_all_tools
from app.agent.memory import get_session_history

logger = get_logger("agent_executor")

# Load tools
tools = get_all_tools()

# Setup ChatPromptTemplate
# The history variable name MUST match what is passed to RunnableWithMessageHistory config
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create AgentExecutor with intermediate steps enabled
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True
)

# Post-processing helper to convert list-type outputs (text blocks) to plain strings.
# This prevents Pydantic validation errors and history message coercion failures.
from langchain_core.runnables import RunnableLambda

def clean_agent_output(res: dict) -> dict:
    output = res.get("output", "")
    if isinstance(output, list):
        texts = []
        for block in output:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
            elif isinstance(block, str):
                texts.append(block)
        res["output"] = "\n".join(texts)
    elif not isinstance(output, str):
        res["output"] = str(output)
    return res

agent_chain = agent_executor | RunnableLambda(clean_agent_output)

# Bind conversation history using the processed agent chain
agent_with_chat_history = RunnableWithMessageHistory(
    agent_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="output"
)

def run_agent(question: str, session_id: str) -> dict:
    """
    Main entrypoint to run the customer service assistant agent.
    
    Args:
        question: The user's input query.
        session_id: Session identifier for conversational memory.
        
    Returns:
        dict: Containing the final response text, reasoning steps, tool calls made, and if RAG was used.
    """
    start_time = time.time()
    logger.info(f"Agent invocation started. Session: '{session_id}', Question: '{question}'")

    try:
        config = {"configurable": {"session_id": session_id}}
        result = agent_with_chat_history.invoke(
            {"input": question},
            config=config
        )

        final_output = result.get("output", "")
        intermediate_steps = result.get("intermediate_steps", [])

        tool_calls = []
        reasoning_steps = []
        used_rag = False

        for action, observation in intermediate_steps:
            tool_name = getattr(action, "tool", "Unknown Tool")
            tool_input = getattr(action, "tool_input", {})
            
            # Normalize tool_input to dict if it's parsed as a string
            if isinstance(tool_input, str):
                tool_input = {"input": tool_input}
            elif not isinstance(tool_input, dict):
                tool_input = {"input": str(tool_input)}

            tool_output = observation
            
            if tool_name == "search_store_policy":
                used_rag = True

            # Determine success/failure status of tool call
            status = "success"
            # If the tool returned an exception or an explicit error dictionary with no found flag, mark as error
            if isinstance(observation, Exception) or (
                isinstance(observation, dict) and "error" in observation and "found" not in observation
            ):
                status = "error"

            tool_calls.append({
                "tool_name": tool_name,
                "tool_input": tool_input,
                "tool_output": tool_output,
                "status": status
            })

            # Programmatically construct human-readable reasoning steps
            if tool_name == "get_order":
                order_id = tool_input.get("order_id", "unknown")
                reasoning_steps.append(f"Looked up details for order '{order_id}'.")
            elif tool_name == "get_product":
                product_id = tool_input.get("product_id", "unknown")
                reasoning_steps.append(f"Retrieved specifications for product '{product_id}'.")
            elif tool_name == "search_products":
                q = tool_input.get("query", "")
                reasoning_steps.append(f"Searched catalog for products matching query '{q}'.")
            elif tool_name == "search_store_policy":
                q = tool_input.get("query", "")
                reasoning_steps.append(f"Retrieved store policies matching query '{q}'.")
            else:
                reasoning_steps.append(f"Called tool '{tool_name}' with input: {tool_input}.")

        if not tool_calls:
            reasoning_steps.append("Resolved query using conversation context and chat history.")

        latency = (time.time() - start_time) * 1000
        logger.info(f"Agent invocation completed. Session: '{session_id}', Tool calls: {len(tool_calls)}, Latency: {latency:.2f}ms")

        return {
            "response": final_output,
            "session_id": session_id,
            "reasoning_steps": reasoning_steps,
            "tool_calls": tool_calls,
            "used_rag": used_rag
        }

    except Exception as e:
        latency = (time.time() - start_time) * 1000
        logger.error(f"Agent invocation failed. Session: '{session_id}', Error: {e}, Latency: {latency:.2f}ms", exc_info=True)
        raise e
