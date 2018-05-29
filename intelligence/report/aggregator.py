#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
import copy
import operator

def aggregate(results):
    reports = map(operator.itemgetter(1), results)
    return reduce(aggregate_reports, reports) if reports else None

def aggregate_reports(current, new):
    result = {}
    for facet in new:
        aggregate_facet = get_aggregator_func(facet)
        result[facet] = aggregate_facet(current.get(facet,{}), new[facet])
    return result
        
def aggregate_counter(current, new):
    result = collections.Counter(current)
    result.update(new)
    return result
    
special_aggregators = {
        'count': lambda x, y: x + y
    }
get_aggregator_func = lambda facet: special_aggregators.get(facet) or aggregate_counter
