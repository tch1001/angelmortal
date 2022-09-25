import redis

client = redis.Redis()
p = client.pubsub()
p.subscribe('jh')

while True:
    message = p.get_message()
    if message:
        print(message['data'])