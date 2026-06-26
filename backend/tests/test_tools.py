import pytest
from app.tools.order_tool import get_order
from app.tools.product_tool import get_product
from app.tools.search_tool import search_products

def test_get_order_existing():
    # Call order tool as a function or invoking tool run
    # Since they are wrapped in @tool, we can call them using .invoke() or directly by calling the function
    # Let's call using .invoke() which is the standard LangChain interface
    result = get_order.invoke({"order_id": "ORD-1002"})
    assert result["found"] is True
    assert result["customer_name"] == "Bob Jones"
    assert len(result["items"]) == 2
    # Ensure one item is the shoe P101
    product_ids = [item["product_id"] for item in result["items"]]
    assert "P101" in product_ids

def test_get_order_missing():
    result = get_order.invoke({"order_id": "ORD-9999"})
    assert result["found"] is False
    assert "error" in result
    assert result["order_id"] == "ORD-9999"

def test_get_product_existing():
    result = get_product.invoke({"product_id": "P101"})
    assert result["found"] is True
    assert result["name"] == "Stride Lite Running Shoes"
    assert result["category"] == "shoes"
    assert result["price"] == 80.00

def test_get_product_missing():
    result = get_product.invoke({"product_id": "P999"})
    assert result["found"] is False
    assert "error" in result
    assert result["product_id"] == "P999"

def test_search_products_by_category():
    result = search_products.invoke({"query": "shoes", "category": "shoes"})
    assert result["found"] is True
    assert len(result["results"]) >= 3
    for p in result["results"]:
        assert p["category"] == "shoes"

def test_search_products_price_filter():
    # Search for shoes cheaper than or equal to $50.00
    # Should find P102 AeroStep ($45.00) but not P101 Stride ($80.00) or P103 Summit ($120.00)
    result = search_products.invoke({"query": "", "max_price": 50.00, "category": "shoes"})
    assert result["found"] is True
    prices = [p["price"] for p in result["results"]]
    assert all(price <= 50.00 for price in prices)
    product_ids = [p["product_id"] for p in result["results"]]
    assert "P102" in product_ids
    assert "P101" not in product_ids
    assert "P103" not in product_ids

def test_search_products_exclude_id():
    # Search for shoes, but exclude P101
    result = search_products.invoke({"query": "", "category": "shoes", "exclude_product_id": "P101"})
    assert result["found"] is True
    product_ids = [p["product_id"] for p in result["results"]]
    assert "P101" not in product_ids
    assert "P102" in product_ids
    assert "P103" in product_ids
