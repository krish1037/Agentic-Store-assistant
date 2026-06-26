import os
import json
import time
from langchain_core.tools import tool
from app.services.logger_service import get_logger

logger = get_logger("order_tool")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_PATH = os.path.join(BASE_DIR, "data", "orders.json")

# Load once at module level
try:
    with open(ORDERS_PATH, "r", encoding="utf-8") as f:
        ORDERS = json.load(f)
except Exception as e:
    logger.error(f"Failed to load orders.json: {e}")
    ORDERS = []

@tool
def get_order(order_id: str) -> dict:
    """Use this tool to retrieve details of a specific customer order by its order ID (format like ORD-XXXX, e.g. ORD-1002).
    It returns the customer's name, ordered items (product IDs, names, quantities), order status,
    order date, expected delivery date, and total amount.
    Use this when the customer asks 'Where is my order?', 'What is the status of order ORD-XXXX?', or 'Does my order contain shoes?'.
    """
    start_time = time.time()
    logger.info(f"Tool get_order invoked with order_id: {order_id}")
    
    if not order_id:
        result = {"found": False, "error": "Order ID cannot be empty."}
        latency = (time.time() - start_time) * 1000
        logger.warning(f"Tool get_order failed. Input: '{order_id}', Latency: {latency:.2f}ms, Error: Empty ID")
        return result

    clean_id = order_id.strip().upper()
    for order in ORDERS:
        if order["order_id"].upper() == clean_id:
            result = {"found": True, **order}
            latency = (time.time() - start_time) * 1000
            logger.info(f"Tool get_order success. Input: '{order_id}', Latency: {latency:.2f}ms")
            return result

    result = {"found": False, "order_id": order_id, "error": f"Order with ID '{order_id}' was not found in our database."}
    latency = (time.time() - start_time) * 1000
    logger.info(f"Tool get_order not found. Input: '{order_id}', Latency: {latency:.2f}ms")
    return result
