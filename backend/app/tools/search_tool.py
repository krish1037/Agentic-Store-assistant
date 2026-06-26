import os
import json
import time
from typing import Optional
from langchain_core.tools import tool
from app.services.logger_service import get_logger

logger = get_logger("search_tool")

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
def search_products(
    query: str,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
    exclude_product_id: Optional[str] = None
) -> dict:
    """Use this tool to search for products in the catalog by keywords (e.g. searching name, description, or category).
    It supports filtering by category, setting a maximum price ceiling (max_price), and excluding a specific product_id (exclude_product_id).
    This is extremely useful for finding alternatives or cheaper options. For example, if a user wants a cheaper shoe alternative,
    you can fetch their original order, get the shoe product, and then call this tool with category='shoes', max_price=original_shoe_price, and exclude_product_id=original_shoe_id.
    """
    start_time = time.time()
    logger.info(f"Tool search_products invoked. Query: '{query}', max_price: {max_price}, category: {category}, exclude: {exclude_product_id}")

    results = []
    query_clean = query.strip().lower() if query else ""

    for product in PRODUCTS:
        # 1. Exclude original product if specified
        if exclude_product_id and product["product_id"].upper() == exclude_product_id.strip().upper():
            continue
        
        # 2. Filter by category if specified
        if category and product["category"].strip().lower() != category.strip().lower():
            continue
            
        # 3. Filter by max price if specified
        if max_price is not None and product["price"] > max_price:
            continue
            
        # 4. Check keyword match if query is provided
        if query_clean:
            name_match = query_clean in product["name"].lower()
            desc_match = query_clean in product["description"].lower()
            cat_match = query_clean in product["category"].lower()
            if not (name_match or desc_match or cat_match):
                continue

        results.append(product)

    latency = (time.time() - start_time) * 1000
    
    if results:
        result = {"found": True, "results": results}
        logger.info(f"Tool search_products success. Found {len(results)} items. Latency: {latency:.2f}ms")
        return result
    else:
        result = {"found": False, "results": [], "message": "No products matched the search criteria."}
        logger.info(f"Tool search_products empty results. Latency: {latency:.2f}ms")
        return result
