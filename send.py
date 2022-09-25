#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='127.0.0.1'))
channel = connection.channel()

channel.queue_declare(queue='bye')

channel.basic_publish(exchange='', routing_key='bye', body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()