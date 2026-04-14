import time
from dataclasses import dataclass
from typing import List

@dataclass
class Order:
    order_id: str
    side: str  # "buy" or "sell"
    price: float
    quantity: int
    timestamp: int = None

    def __post_init__(self):
        if self.timestamp is None:
            # Use nanoseconds for trading engine precision
            self.timestamp = time.time_ns()

class OrderBook:
    def __init__(self):
        self.bids: List[Order] = []  # Buy orders
        self.asks: List[Order] = []  # Sell orders
        self.trades: List[dict] = [] # Record of executed trades

    def add_order(self, order: Order):
        if order.side == "buy":
            self.bids.append(order)
            # Sort bids highest price first (price-time priority)
            self.bids.sort(key=lambda x: (-x.price, x.timestamp))
        elif order.side == "sell":
            self.asks.append(order)
            # Sort asks lowest price first
            self.asks.sort(key=lambda x: (x.price, x.timestamp))
        
        self.match_orders()

    def match_orders(self):
        # Keep matching as long as the highest bid is >= the lowest ask
        while self.bids and self.asks and self.bids[0].price >= self.asks[0].price:
            top_bid = self.bids[0]
            top_ask = self.asks[0]

            # Determine the trade quantity
            trade_qty = min(top_bid.quantity, top_ask.quantity)
            
            # The resting order (maker) determines the price. 
            # If timestamps are perfectly identical, we default to the ask.
            trade_price = top_ask.price if top_ask.timestamp <= top_bid.timestamp else top_bid.price

            # Record the trade
            self.trades.append({
                "bid_order_id": top_bid.order_id,
                "ask_order_id": top_ask.order_id,
                "price": trade_price,
                "quantity": trade_qty,
                "timestamp": time.time_ns()
            })

            # Reduce quantities
            top_bid.quantity -= trade_qty
            top_ask.quantity -= trade_qty

            # Remove filled orders from the book
            if top_bid.quantity == 0:
                self.bids.pop(0)
            if top_ask.quantity == 0:
                self.asks.pop(0)