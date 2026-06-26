import os
import json
import time
from langchain_core.tools import tool
from app.services.logger_service import get_logger

logger = get_logger("product_tool")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "products.json")

# Load once at module level
try:
    with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
        PRODUCTS = json.load(f)
except Exception as e:
    logger.error(f"Failed to load products.json: {e}")
    PRODUCTS = []

@tool
def get_product(product_id: str) -> dict:
    """Use this tool to retrieve technical or catalog details of a specific product by its product ID (format like P1XX, e.g. P101).
    It returns the product name, category, price, description, in-stock status, and customer rating.
    Use this when the customer asks 'Tell me about product P101' or asks for description/details of a specific product ID.
    """
    start_time = time.time()
    logger.info(f"Tool get_product invoked with product_id: {product_id}")

    if not product_id:
        result = {"found": False, "error": "Product ID cannot be empty."}
        latency = (time.time() - start_time) * 1000
        logger.warning(f"Tool get_product failed. Input: '{product_id}', Latency: {latency:.2f}ms, Error: Empty ID")
        return result

    clean_id = product_id.strip().upper()
    for product in PRODUCTS:
        if product["product_id"].upper() == clean_id:
            result = {"found": True, **product}
            latency = (time.time() - start_time) * 1000
            logger.info(f"Tool get_product success. Input: '{product_id}', Latency: {latency:.2f}ms")
            return result

    result = {"found": False, "product_id": product_id, "error": f"Product with ID '{product_id}' was not found in our catalog."}
    latency = (time.time() - start_time) * 1000
    logger.info(f"Tool get_product not found. Input: '{product_id}', Latency: {latency:.2f}ms")
    return result
