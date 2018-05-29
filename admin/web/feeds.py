#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
import datetimes
import data.analyses

def get_throughput():
    platforms = collections.defaultdict(list)
    throughputs = list(data.analyses.get_feed_throughputs())
    if not throughputs: return []
    platform_names = frozenset(platform for _,value in throughputs for platform in value.keys())
    for key, value in throughputs:
        timestamp = datetimes.unpack_key_to_timestamp(key)
        for platform in platform_names:
            platforms[platform].append({'datetime':timestamp, 'count':value.get(platform) or 0})
    return [{'key':platform, 'values':sorted(values, key=lambda value: value['datetime'])} for platform, values in platforms.iteritems()]
