from fastapi import FastAPI

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Monitor", "price": 8999, "category": "Electronics", "in_stock": False},

    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

@app.get("/products/category/{category_name}")
def get_category(category_name: str):
    result = [p for p in products if p["category"].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}

@app.get("/products/instock")
def instock():
    available = [p for p in products if p["in_stock"]]
    return {"in_stock_products": available, "count": len(available)}

@app.get("/store/summary")
def summary():
    instock_count = len([p for p in products if p["in_stock"]])
    outstock = len(products) - instock_count
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": instock_count,
        "out_of_stock": outstock,
        "categories": categories
    }

@app.get("/products/search/{keyword}")
def search(keyword: str):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}

@app.get("/products/deals")
def deals():
    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])
    return {"best_deal": cheapest, "premium_pick": expensive}



from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
 
app = FastAPI()
 
# ── Pydantic model ───────────────────────────────────────────────────────────
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
 
# ── Data ────────────────────────────────────────────────────────────────────
products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','in_stock':True},
    {'id':2,'name':'Notebook',      'price': 99,'category':'Stationery', 'in_stock':True},
    {'id':3,'name':'USB Hub',        'price':799,'category':'Electronics','in_stock':False},
    {'id':4,'name':'Pen Set',         'price': 49,'category':'Stationery', 'in_stock':True},
]
orders = []
order_counter = 1
 
# ── Endpoints ───────────────────────────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
 
@app.get('/products/filter')   # NOTE: must come BEFORE /products/{product_id}
def filter_products(
    category:  str  = Query(None),
    max_price: int  = Query(None),
    in_stock:  bool = Query(None)
):
    result = products
    if category:             result = [p for p in result if p['category']==category]
    if max_price:            result = [p for p in result if p['price']<=max_price]
    if in_stock is not None: result = [p for p in result if p['in_stock']==in_stock]
    return {'filtered_products': result, 'count': len(result)}
 
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}
 
@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    product = next((p for p in products if p['id']==order_data.product_id), None)
    if product is None:          return {'error': 'Product not found'}
    if not product['in_stock']:  return {'error': f"{product['name']} is out of stock"}
    total_price = product['price'] * order_data.quantity
    order = {'order_id': order_counter, 'customer_name': order_data.customer_name,
'product': product['name'], 'quantity': order_data.quantity,
'delivery_address': order_data.delivery_address,
'total_price': total_price, 'status': 'confirmed'}
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}
 
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}




from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
 
app = FastAPI()
 
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
 
products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','in_stock':True},
    {'id':2,'name':'Notebook',      'price': 99,'category':'Stationery', 'in_stock':True},
    {'id':3,'name':'USB Hub',        'price':799,'category':'Electronics','in_stock':False},
    {'id':4,'name':'Pen Set',         'price': 49,'category':'Stationery', 'in_stock':True},
]
orders = []
order_counter = 1
 
# ══ HELPER FUNCTIONS ═══════════════════════════════════════
def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None
 
def calculate_total(product: dict, quantity: int) -> int:
    return product['price'] * quantity
 
def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    result = products
    if category  is not None: result = [p for p in result if p['category']==category]
    if min_price is not None: result = [p for p in result if p['price']>=min_price]
    if max_price is not None: result = [p for p in result if p['price']<=max_price]
    if in_stock  is not None: result = [p for p in result if p['in_stock']==in_stock]
    return result
 
# ══ ENDPOINTS ════════════════════════════════════════════
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
 
# NOTE: /filter, /compare, /summary must come BEFORE /{product_id}
@app.get('/products/filter')
def filter_products(category:str=Query(None), min_price:int=Query(None),
                    max_price:int=Query(None), in_stock:bool=Query(None)):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {'filtered_products': result, 'count': len(result)}
 
@app.get('/products/compare')
def compare_products(product_id_1:int=Query(...), product_id_2:int=Query(...)):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1: return {'error': f'Product {product_id_1} not found'}
    if not p2: return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {'product_1':p1,'product_2':p2,
'better_value':cheaper['name'],
'price_diff':abs(p1['price']-p2['price'])}
 
@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        return {'error': 'Product not found'}
    return {'product': product}
 
@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    product = find_product(order_data.product_id)
    if not product:
        return {'error': 'Product not found'}
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
    total = calculate_total(product, order_data.quantity)
    order = {'order_id':order_counter,'customer_name':order_data.customer_name,
'product':product['name'],'quantity':order_data.quantity,
'delivery_address':order_data.delivery_address,
'total_price':total,'status':'confirmed'}
    orders.append(order)
    order_counter += 1
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
 
app = FastAPI()
 
# ══ PYDANTIC MODEL ════════════════════════════════════════════════
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
 
# ══ DATA ══════════════════════════════════════════════════════════
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price':  99, 'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',        'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':  49, 'category': 'Stationery',  'in_stock': True},
]
 
orders        = []
order_counter = 1
 
# ══ HELPER FUNCTIONS ══════════════════════════════════════════════
 
def find_product(product_id: int):
    """Search products list by ID. Returns product dict or None."""
    for p in products:
        if p['id'] == product_id:
            return p
    return None
 
def calculate_total(product: dict, quantity: int) -> int:
    """Multiply price by quantity and return total."""
    return product['price'] * quantity
 
def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    """Apply filters and return matching products."""
    result = products
    if category  is not None:
        result = [p for p in result if p['category'] == category]
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock  is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return result
 
# ══ ENDPOINTS ═════════════════════════════════════════════════════
# ROUTE ORDER RULE:
#   Fixed routes  (/filter, /compare)  must come BEFORE
#   Variable route (/products/{product_id})
# ═════════════════════════════════════════════════════════════════
 
# ── Day 1 ─────────────────────────────────────────────────────────
 
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
 
# ── Day 2: Query Parameters ────────────────────────────────────────
 
@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    min_price: int  = Query(None, description='Minimum price'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only'),
):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {'filtered_products': result, 'count': len(result)}
 
# ── Day 3: Compare (fixed route — must stay BEFORE /{product_id}) ─
 
@app.get('/products/compare')
def compare_products(
    product_id_1: int = Query(..., description='First product ID'),
    product_id_2: int = Query(..., description='Second product ID'),
):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1:
        return {'error': f'Product {product_id_1} not found'}
    if not p2:
        return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {
        'product_1':    p1,
        'product_2':    p2,
        'better_value': cheaper['name'],
        'price_diff':   abs(p1['price'] - p2['price']),
    }
 
# ── Day 1: Path Parameter (variable — always AFTER all fixed routes)
 
@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        return {'error': 'Product not found'}
    return {'product': product}
 
# ── Day 2: POST + Pydantic ─────────────────────────────────────────
 
@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
 
    product = find_product(order_data.product_id)
    if not product:
        return {'error': 'Product not found'}
 
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
 
    total = calculate_total(product, order_data.quantity)
 
    order = {
        'order_id':         order_counter,
        'customer_name':    order_data.customer_name,
        'product':          product['name'],
        'quantity':         order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'total_price':      total,
        'status':           'confirmed',
    }
    orders.append(order)
    order_counter = order_counter + 1
    return {'message': 'Order placed successfully', 'order': order}
 
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}
 
    return {'message':'Order placed successfully','order':order}
 
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}





from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field, EmailStr
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
    contact_email: EmailStr
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