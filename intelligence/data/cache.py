#!/usr/bin/python
# -*- coding: utf-8 -*-
from web.endpoint import cache
from requests import HTTPError

CACHE_NAME = 'intelligence-tasks'

def get_cache(key):
    try:
        t = cache.get(cache=CACHE_NAME, key=key)
    except HTTPError:
        return None
    return t.value

def set_cache(key, value):
    return cache.put(cache=CACHE_NAME, key=key, value=value)

def delete_cache(key):
    return cache.delete(cache=CACHE_NAME, key=key)
