from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid

# Import your engine
from app.engine import Order, OrderBook

# Initialize the API and the in-memory Order Book
app = FastAPI(title="Real-Time Matching Engine API")
book = OrderBook()

# Pydantic model for strict input validation
class OrderRequest(BaseModel):
    side: str = Field(..., pattern="^(buy|sell)$", description="Must be 'buy' or 'sell'")
    price: float = Field(..., gt=0, description="Price must be strictly positive")
    quantity: int = Field(..., gt=0, description="Quantity must be strictly positive")

@app.post("/orders", status_code=201)
def place_order(order_req: OrderRequest):
    """Submit a new buy or sell order to the engine."""
    # Generate a unique ID for the order
    new_order_id = str(uuid.uuid4())[:8] 
    
    # Create the engine Order object
    new_order = Order(
        order_id=new_order_id,
        side=order_req.side,
        price=order_req.price,
        quantity=order_req.quantity
    )
    
    # Push it to the matching engine
    book.add_order(new_order)
    
    return {
        "message": "Order processed",
        "order_id": new_order_id,
        "current_bids": len(book.bids),
        "current_asks": len(book.asks),
        "total_trades_executed": len(book.trades)
    }

@app.get("/book")
def get_order_book():
    """View the current open bids and asks."""
    return {
        "bids": book.bids,
        "asks": book.asks
    }

@app.get("/trades")
def get_trade_history():
    """View all executed trades."""
    return {"trades": book.trades}