#!/usr/bin/python
# -*- coding: utf-8 -*-


def cast_iter(cast=None):
    import functools

    def decorator(func):
        @functools.wraps(func)
        def casted_func(*args, **kwargs):
            cast_func = kwargs.pop('cast', cast)
            result = func(*args, **kwargs)
            return cast_func(result) if cast_func else result
        return casted_func
    return decorator
