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

# 按照页查询小说 (不然一次性太多了)
page_info = '1/1391'
sql = """
SELECT each_code FROM biquge_list WHERE page_info = ?
"""
cursor.execute(sql, (page_info, ))
results = cursor.fetchall()
for each_fiction in results:
    fiction_code = each_fiction[0]
    print(f"fiction code: {fiction_code}")
    # 根据 小说编码 查询 小说章节编码
    sql = """
    SELECT chapter_code FROM chapter_list WHERE fiction_code = ?
    """
    cursor.execute(sql, (fiction_code,))
    chapter_results = cursor.fetchall()
    for each_chapter in chapter_results:
        chapter_code = each_chapter[0]
        chapter_url = f"https://www.xbiqugew.com/book/{fiction_code}/{chapter_code}.html"
        message = json.dumps({
            'url': chapter_url,
        })
        channel.basic_publish(
            exchange='',
            routing_key=rabbitmq_queue,
            body=message.encode('utf-8'),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Send MQ: {message}")
    # i = input("======")
mq_connection.close()
sql_connection.close()
