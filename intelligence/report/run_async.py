#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

import data.cache as task_cache

def run_async(task_func, key, queue, *args, **kwargs):
    task_id = task_cache.get_cache(key)
    if task_id:
        result = task_func.AsyncResult(task_id)
        if result.ready():
            contents = result.get()
            result.forget()  # delete data on IronCache
            task_cache.delete_cache(key)
            return ("ready", contents)
    else:
        result = task_func.apply_async(queue=queue, args=args, kwargs=kwargs)
        task_cache.set_cache(key, result.task_id)
    return ("running", None)
