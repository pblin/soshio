import time
import hashlib
import logging

from requests import HTTPError

from iron_worker import IronWorker
from iron_cache import IronCache
import config.loader

logger = logging.getLogger(__name__)

CACHE_NAME = "worker"

TIMEOUT = 40


def get_worker_cache():
    mq_env = config.loader.load().get('MQ_ENV', {})
    iron_env = {"project_id": mq_env['PROJECT'], "token": mq_env['TOKEN']}
    worker = IronWorker(**iron_env)
    cache = IronCache(**iron_env)
    return worker, cache


def get_url(url, task='get_url'):
    worker, cache = get_worker_cache()

    payload = {'task': task,
               'kwargs': {'url': url}}
    logger.debug(u"Queueing a get_url task for url %s" % url.decode('utf-8'))
    response = worker.queue(code_name="acquisition", payload=payload, priority=0)
    detail = worker.task(response)
    cnt = 0.0
    while detail.status == 'queued' or detail.status == 'running':
        time.sleep(1)
        detail = worker.task(detail)
        if detail.status == 'running':
            cnt += 1.0
        else:
            cnt += 0.1
        if cnt >= TIMEOUT:
            worker.cancel(detail)
            raise WorkerError("timeout")

    if detail.status == 'error' or detail.status == 'cancelled':
        raise WorkerError()
    if detail.status == 'complete':
        key = hashlib.md5(url).hexdigest()
        value = cache.get(cache=CACHE_NAME, key=key).value
        try:  # it's okay if cache delete fails. It won't hurt.
            cache.delete(cache=CACHE_NAME, key=key)
        except HTTPError:
            pass
        return value


class WorkerError(Exception):
    pass
