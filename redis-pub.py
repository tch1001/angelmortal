import redis
client = redis.Redis()
client.publish('jh', 'meow')