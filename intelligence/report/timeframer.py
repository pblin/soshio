#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetimes

def get_max_timeframe():
    return datetimes.datetime.min, datetimes.datetime.max
    
timedelta_condition_funcs = [
        (lambda x : x <= datetimes.timedelta(days=1), 'hour'),
        (lambda x : datetimes.timedelta(days=1) < x <= datetimes.timedelta(days=91), 'day'),
        (lambda x : datetimes.timedelta(days=91) < x, 'month'),
        (lambda x : x <= datetimes.timedelta(days=730), 'year')
    ]
    
def get_timeframe_from_str(*timeframe_strs):
    start, end = map(datetimes.extract_datetime, timeframe_strs)
    if not (start or end): return get_max_timeframe()
    if not end: return start, start + datetimes.timedelta(days=1)
    if not start or start > end: return end  - datetimes.timedelta(days=1), end
    if start == end: return start, end + datetimes.timedelta(days=1)
    return start, end
    
def get_level(start, end):
    delta = end - start
    for conidition_func, level in timedelta_condition_funcs:
        if conidition_func(delta):
            return level

def get_timeframe_details(*timeframe_strs):
    start, end = get_timeframe_from_str(*timeframe_strs)
    level = get_level(start, end)
    return (start,end), level
