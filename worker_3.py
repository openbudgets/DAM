import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_url_uep = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_url_dm = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)
conn_dm = redis.from_url(redis_url_dm)
conn_uep = redis.from_url(redis_url_uep)

if __name__ == '__main__':
    with Connection(conn_dm):
        worker_dm = Worker(list(map(Queue, listen)))
        worker_dm.work()

    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()

    with Connection(conn_uep):
        worker_uep = Worker(list(map(Queue, listen)))
        worker_uep.work()


