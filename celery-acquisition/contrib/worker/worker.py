import logging
import sys
import json
import hashlib

import iron_cache
import requests

from browser import get_browser

CACHE_NAME = "worker"


class Worker:
    _json_file = '.iron.json'

    def _get_iron_env(self):
        with open(self._json_file) as f:
            return json.loads(f.read())

    def __init__(self):
        iron_env = self._get_iron_env()
        self._cache = iron_cache.IronCache(
            project_id=iron_env['project_id'],
            token=iron_env['token'])

    def tencent_get_url(self, url):
        br = get_browser()
        br.open("http://weibo.yunyun.com")
        response = br.open(url)
        result = response.read().decode('utf-8')
        key = hashlib.md5(url.encode('utf-8')).hexdigest()
        self._cache.put(cache=CACHE_NAME, key=key, value=result)
        print >> sys.stdout, key

    def get_url(self, url):
        response = requests.get(url)
        key = hashlib.md5(url.encode('utf-8')).hexdigest()
        result = response.text
        self._cache.put(cache=CACHE_NAME, key=key, value=result)
        print >> sys.stdout, key


def get_payload():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-payload" and (i + 1) < len(sys.argv):
            payload_file = sys.argv[i + 1]
            with open(payload_file, 'r') as f:
                payload = json.loads(f.read())
            break
    return payload

if __name__ == '__main__':
    payload = get_payload()

    func_name = payload['task']
    args = payload.get('args', [])
    kwargs = payload.get('kwargs', {})

    if payload.get('log-level'):
        logging.basicConfig(stream=sys.stderr, level=payload.get('log-level'))
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    worker = Worker()
    getattr(worker, func_name)(*args, **kwargs)
