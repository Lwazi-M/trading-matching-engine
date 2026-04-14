from app.engine import Order, OrderBook

def test_order_matching():
    book = OrderBook()
    
    # 1. Add a Sell order (Ask) for 10 units at R100
    sell_order = Order(order_id="s1", side="sell", price=100.0, quantity=10)
    book.add_order(sell_order)
    
    # Verify it's sitting in the book
    assert len(book.asks) == 1
    assert len(book.trades) == 0

    # 2. Add a Buy order (Bid) for 5 units at R105 (This should trigger a match!)
    buy_order = Order(order_id="b1", side="buy", price=105.0, quantity=5)
    book.add_order(buy_order)

    # 3. Verify the match occurred correctly
    assert len(book.trades) == 1
    assert book.trades[0]["quantity"] == 5
    assert book.trades[0]["price"] == 100.0  # Matches at the resting ask price
    
    # The buy order should be completely filled and removed
    assert len(book.bids) == 0
    
    # The sell order should have 5 units remaining
    assert len(book.asks) == 1
    assert book.asks[0].quantity == 5