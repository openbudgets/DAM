import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_url_dm = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn_dm = redis.from_url(redis_url_dm)

if __name__ == '__main__':

    with Connection(conn_dm):
        worker_dm = Worker(list(map(Queue, listen)))
        worker_dm.work()
