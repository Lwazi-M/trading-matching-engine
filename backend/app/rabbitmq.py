import pika
import json

# Paste your CloudAMQP URL between the quotes below
AMQP_URL = "amqp://wqxuhwnx:MgeCaSSzZdqwoTtno9xS0MDEJHGKRzFf@rat.rmq2.cloudamqp.com/wqxuhwnx"

def get_rabbitmq_connection():
    """Establish a connection to the CloudAMQP broker."""
    parameters = pika.URLParameters(AMQP_URL)
    return pika.BlockingConnection(parameters)

def publish_order(order_data: dict):
    """Publish an order payload to the RabbitMQ queue."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Declare the queue (this ensures the queue exists before we send to it)
    channel.queue_declare(queue='trading_orders', durable=True)
    
    # Send the message
    channel.basic_publish(
        exchange='',
        routing_key='trading_orders',
        body=json.dumps(order_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Delivery mode 2 makes the message persistent
        )
    )
    
    print(f" [x] Sent {order_data['side']} order to cloud queue")
    connection.close()