from fastapi import FastAPI
from pydantic import BaseModel, Field
import uuid

# Import our cloud publisher!
from app.rabbitmq import publish_order

app = FastAPI(title="Real-Time Matching Engine API")

class OrderRequest(BaseModel):
    side: str = Field(..., pattern="^(buy|sell)$", description="Must be 'buy' or 'sell'")
    price: float = Field(..., gt=0, description="Price must be strictly positive")
    quantity: int = Field(..., gt=0, description="Quantity must be strictly positive")

@app.post("/orders", status_code=201)
def place_order(order_req: OrderRequest):
    """Submit a new buy or sell order to the high-speed cloud queue."""
    new_order_id = str(uuid.uuid4())[:8] 
    
    # 1. Structure the data payload
    order_payload = {
        "order_id": new_order_id,
        "side": order_req.side,
        "price": order_req.price,
        "quantity": order_req.quantity
    }
    
    # 2. Drop it into CloudAMQP
    publish_order(order_payload)
    
    # 3. Immediately respond to the client (Decoupled!)
    return {
        "message": "Order successfully queued",
        "order_id": new_order_id,
        "status": "pending"
    }