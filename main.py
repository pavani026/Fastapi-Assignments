from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# -----------------------------
# Sample Product Data
# -----------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

feedback_list = []
orders = []
order_counter = 0

# -----------------------------
# Q1: Filter Products by min_price
# -----------------------------
@app.get("/products/filter")
def filter_products(
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    category: Optional[str] = Query(None)
):
    result = products
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    if category is not None:
        result = [p for p in result if p["category"].lower() == category.lower()]
    return result

# -----------------------------
# Q2: Get Only Price of Product
# -----------------------------
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int = Path(...)):
    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}
    return {"error": "Product not found"}

# -----------------------------
# Q3: Customer Feedback
# -----------------------------
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(feedback: CustomerFeedback):
    feedback_list.append(feedback.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": feedback.dict(),
        "total_feedback": len(feedback_list)
    }

# -----------------------------
# Q4: Product Summary Dashboard
# -----------------------------
@app.get("/products/summary")
def product_summary():
    total = len(products)
    in_stock = sum(1 for p in products if p["in_stock"])
    out_stock = total - in_stock
    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total,
        "in_stock_count": in_stock,
        "out_of_stock_count": out_stock,
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }

# -----------------------------
# Q5: Bulk Order
# -----------------------------
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)   # simplified to str
    items: List[OrderItem]

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
            grand_total += subtotal

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# -----------------------------
# BONUS: Order Status Tracker
# -----------------------------
class SimpleOrder(BaseModel):
    product_id: int
    quantity: int

@app.post("/orders")
def create_order(order: SimpleOrder):
    global order_counter
    order_counter += 1
    new_order = {
        "id": order_counter,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }
    orders.append(new_order)
    return new_order

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for o in orders:
        if o["id"] == order_id:
            return o
    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for o in orders:
        if o["id"] == order_id:
            o["status"] = "confirmed"
            return o
    return {"error": "Order not found"}