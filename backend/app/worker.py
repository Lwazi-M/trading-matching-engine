import pika
import json
import sys
import os

# Ensure the app module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.engine import Order, OrderBook

# Paste your CloudAMQP URL here (same as in rabbitmq.py)
AMQP_URL = "amqp://wqxuhwnx:MgeCaSSzZdqwoTtno9xS0MDEJHGKRzFf@rat.rmq2.cloudamqp.com/wqxuhwnx"

# Initialize the Matching Engine inside the worker
book = OrderBook()

def get_rabbitmq_connection():
    parameters = pika.URLParameters(AMQP_URL)
    return pika.BlockingConnection(parameters)

def process_order(ch, method, properties, body):
    """This function runs every time a new order arrives from the cloud."""
    order_data = json.loads(body)
    print(f" [↓] Received Order: {order_data['side'].upper()} {order_data['quantity']} @ R{order_data['price']}")
    
    # Convert the JSON payload into an Engine Order object
    new_order = Order(
        order_id=order_data["order_id"],
        side=order_data["side"],
        price=order_data["price"],
        quantity=order_data["quantity"]
    )
    
    # Push it into the order book to be matched
    book.add_order(new_order)
    
    # Print the live state of the engine
    print(f" [✓] Engine State -> Bids: {len(book.bids)} | Asks: {len(book.asks)} | Total Trades Executed: {len(book.trades)}")
    print("-" * 50)
    
    # Acknowledge the message so CloudAMQP deletes it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    """Connect to the cloud and start listening."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Ensure the queue exists
    channel.queue_declare(queue='trading_orders', durable=True)
    
    # Don't give more than 1 message to a worker at a time (Load balancing)
    channel.basic_qos(prefetch_count=1)
    
    # Start consuming
    channel.basic_consume(queue='trading_orders', on_message_callback=process_order)
    
    print(' [*] Trading Worker started. Listening to cloud queue... (Press CTRL+C to exit)')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        start_worker()
    except KeyboardInterrupt:
        print('\nWorker shut down manually.')