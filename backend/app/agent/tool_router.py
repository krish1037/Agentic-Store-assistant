from app.tools.order_tool import get_order
from app.tools.product_tool import get_product
from app.tools.search_tool import search_products
from app.rag.retriever import search_store_policy

def get_all_tools() -> list:
    """
    Returns the complete list of tools available to the customer service agent.
    Tool selection is delegated to the LLM via tool-calling.
    """
    return [
        get_order,
        get_product,
        search_products,
        search_store_policy
    ]
