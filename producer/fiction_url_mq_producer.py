import pika
import json
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()


sql_connection = sqlite3.connect('../db/biquge.db')
cursor = sql_connection.cursor()

rabbitmq_queue = os.getenv('RABBITMQ_QUEUE', 'default_queue')
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = os.getenv('RABBITMQ_PORT', '5672')
virtual_host = os.getenv('RABBITMQ_VHOST', '/')
username = os.getenv('RABBITMQ_USERNAME', 'guest')
password = os.getenv('RABBITMQ_PASSWORD', 'guest')

credentials = pika.PlainCredentials(
    username,
    password
)

connection_params_result = {
    'host': rabbitmq_host,
    'port': rabbitmq_port,
    'virtual_host': '/',
    'credentials': credentials,
}
mq_connection = pika.BlockingConnection(pika.ConnectionParameters(**connection_params_result))
channel = mq_connection.channel()
channel.queue_declare(queue=rabbitmq_queue, durable=True)


sql = """
SELECT each_href FROM biquge_list
"""
cursor.execute(sql)
results = cursor.fetchall()
for row in results:
    each_href = row[0]
    print(each_href)
    message = json.dumps({
        'url': each_href,
    })
    channel.basic_publish(
        exchange='',
        routing_key=rabbitmq_queue,
        body=message.encode('utf-8'),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"Send MQ: {message}")

mq_connection.close()
sql_connection.close()
