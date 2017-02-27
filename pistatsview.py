#!/usr/bin/env python
import pika
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import argparse

firstInsert = True

# Initialize database
client = MongoClient('localhost', 27017)
db = client.database
posts = db.posts

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

print('Waiting for logs.')

hiLo = {}

def callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))

    # Store data in db
    global firstInsert
    if firstInsert:
        global hiLo
        hiLo = {
            '_id': '0',
            'cpuHi': data["cpu"],
            'cpuLo': data["cpu"],
            'lorxHi': data["net"]["lo"]["rx"],
            'lorxLo': data["net"]["lo"]["rx"],
            'lotxHi': data["net"]["lo"]["tx"],
            'lotxLo': data["net"]["lo"]["tx"],
            'ethrxHi': data["net"]["eth0"]["rx"],
            'ethrxLo': data["net"]["eth0"]["rx"],
            'ethtxHi': data["net"]["eth0"]["tx"],
            'ethtxLo': data["net"]["eth0"]["tx"],
            'wlanrxHi': data["net"]["wlan0"]["rx"],
            'wlanrxLo': data["net"]["wlan0"]["rx"],
            'wlantxHi': data["net"]["wlan0"]["tx"],
            'wlantxLo': data["net"]["wlan0"]["tx"]
        }
        firstInsert = False
        posts.insert(hiLo)
    else:
        thing = db.posts.find_one({'_id': '0'})
        if data["cpu"] > thing['cpuHi']:
            posts.update({'_id': '0'}, {"$set": {'cpuHi': data["cpu"]}})
        if data["cpu"] < thing['cpuLo']:
            posts.update({'_id': '0'}, {"$set": {'cpuLo': data["cpu"]}})
        if data["net"]["lo"]["rx"] > thing['lorxHi']:
            posts.update({'_id': '0'}, {"$set": {'lorxHi': data["net"]["lo"]["rx"]}})
        if data["net"]["lo"]["rx"] < thing['lorxLo']:
            posts.update({'_id': '0'}, {"$set": {'lorxLo': data["net"]["lo"]["rx"]}})
        if data["net"]["lo"]["tx"] > thing['lotxHi']:
            posts.update({'_id': '0'}, {"$set": {'lotxHi': data["net"]["lo"]["tx"]}})
        if data["net"]["lo"]["tx"] < thing['lotxLo']:
            posts.update({'_id': '0'}, {"$set": {'lotxLo': data["net"]["lo"]["tx"]}})
        if data["net"]["eth0"]["rx"] > thing['ethrxHi']:
            posts.update({'_id': '0'}, {"$set": {'ethrxHi': data["net"]["eth0"]["rx"]}})
        if data["net"]["eth0"]["rx"] < thing['ethrxLo']:
            posts.update({'_id': '0'}, {"$set": {'ethrxLo': data["net"]["eth0"]["rx"]}})
        if data["net"]["eth0"]["tx"] > thing['ethtxHi']:
            posts.update({'_id': '0'}, {"$set": {'ethtxHi': data["net"]["eth0"]["tx"]}})
        if data["net"]["eth0"]["tx"] < thing['ethtxLo']:
            posts.update({'_id': '0'}, {"$set": {'ethtxLo': data["net"]["eth0"]["tx"]}})
        if data["net"]["wlan0"]["rx"] > thing['wlanrxHi']:
            posts.update({'_id': '0'}, {"$set": {'wlanrxHi': data["net"]["wlan0"]["rx"]}})
        if data["net"]["wlan0"]["rx"] < thing['wlanrxLo']:
            posts.update({'_id': '0'}, {"$set": {'wlanrxLo': data["net"]["wlan0"]["rx"]}})
        if data["net"]["wlan0"]["tx"] > thing['wlantxHi']:
            posts.update({'_id': '0'}, {"$set": {'wlantxHi': data["net"]["wlan0"]["tx"]}})
        if data["net"]["wlan0"]["tx"] < thing['wlantxLo']:
            posts.update({'_id': '0'}, {"$set": {'wlantxLo': data["net"]["wlan0"]["tx"]}})

    # Echo utilization stats
    rec = posts.find_one({'_id': '0'})
    print("cpu:", data["cpu"], " [Hi:", rec['cpuHi'], ", Lo:", rec['cpuLo'], "]")
    print("lo: rx=", data["net"]["lo"]["rx"], "B/s [Hi:", rec['lorxHi'], "B/s, Lo:", rec['lorxLo'], "B/s], tx=",
          data["net"]["lo"]["tx"], "B/s [Hi: ", rec['lotxHi'], "B/s, Lo:", rec['lotxLo'], "B/s]")
    print("eth0: rx=", data["net"]["eth0"]["rx"], "B/s [Hi:", rec['ethrxHi'], "B/s, Lo:", rec['ethrxLo'],
          "B/s], tx=", data["net"]["eth0"]["tx"], "B/s [Hi:", rec['ethtxHi'], "B/s, Lo:", rec['ethtxLo'], "B/s]")
    print("wlan0: rx=", data["net"]["wlan0"]["rx"], "B/s [Hi:", rec['wlanrxHi'], "B/s, Lo:", rec['wlanrxLo'],
          "B/s], tx=", data["net"]["wlan0"]["tx"], "B/s [Hi:", rec['wlantxHi'], "B/s, Lo:", rec['wlantxLo'],
          "B/s]\n")

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()