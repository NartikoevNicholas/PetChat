import time
import datetime
import redis
from redis import Redis


def request_is_limited(r: Redis, key: str, limit: int, period):
    y = period / limit
    t = r.time()
    t = float(f'{t[0]}.{t[1]}')

    old_value = r.get(key)
    if old_value:
        ip_t = float(old_value)
    else:
        ip_t = t

    # print(t, ip_t - t, y)
    if ip_t - t <= y:
        r.set(key, max(ip_t, t) + y)
        return False
    return True


r = redis.Redis(host='192.168.16.3', port=6379)
requests = 40

s = datetime.datetime.now()
for i in range(requests):
    if request_is_limited(r, 'a4', 20, 20):
        print(f'{i + 1})   limit')
        time.sleep(0.1)
    else:
        print(f'{i + 1})   allowed')

print(datetime.datetime.now() - s)
