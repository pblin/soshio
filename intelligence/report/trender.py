#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetimes
import collections
import data.analyses

trend_facets = ('sentiments','emotions','platforms','genders','count')
def create_trends(results):
    trends = collections.defaultdict(dict)
    for result in results:
        key, report = result
        datetime_str = datetimes.unpack_key_to_timestamp(key[1:])
        for facet in trend_facets:
            if not report.get(facet): continue
            trends[facet][datetime_str] = report[facet]
    return trends
