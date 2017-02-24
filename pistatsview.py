#!/usr/bin/env python
import pika
import sys
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('-b', required=True)
parser.add_argument('-p')
parser.add_argument('-c')
parser.add_argument('-k', required=True)
args = parser.parse_args()

address = args.b
vHost = args.p
cred = args.c
key = args.k

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=address))
channel = connection.channel()

channel.exchange_declare(exchange='pi_utilization',
                         type='direct')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='pi_utilization',
                   queue=queue_name,
                   routing_key = key)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()