from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

# Example initial products list (from Day 4 session)
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

@app.post("/products")
def add_product(name: str, price: int, category: str, in_stock: bool):
    # Check duplicate
    for p in products:
        if p["name"].lower() == name.lower():
            raise HTTPException(status_code=400, detail="Duplicate product name")

    new_id = max([p["id"] for p in products]) + 1 if products else 1
    new_product = {"id": new_id, "name": name, "price": price, "category": category, "in_stock": in_stock}
    products.append(new_product)
    return {"message": "Product added", "product": new_product}

@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):
    for p in products:
        if p["id"] == product_id:
            if price is not None:
                p["price"] = price
            if in_stock is not None:
                p["in_stock"] = in_stock
            return {"message": "Product updated", "product": p}
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"Product '{p['name']}' deleted"}
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.get("/products/audit")
def audit_products():
    total_products = len(products)
    in_stock_items = [p for p in products if p["in_stock"]]
    out_of_stock_items = [p for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_items)
    most_expensive = max(products, key=lambda x: x["price"]) if products else None

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock_items),
        "out_of_stock_names": [p["name"] for p in out_of_stock_items],
        "total_stock_value": total_stock_value,
        "most_expensive": {"name": most_expensive["name"], "price": most_expensive["price"]} if most_expensive else None
    }

@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):
    if discount_percent < 1 or discount_percent > 99:
        raise HTTPException(status_code=400, detail="Discount percent must be between 1 and 99")

    updated = []
    for p in products:
        if p["category"].lower() == category.lower():
            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price
            updated.append({"id": p["id"], "name": p["name"], "new_price": new_price})


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

