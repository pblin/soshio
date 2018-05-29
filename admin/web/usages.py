#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import operator
import collections
import datetimes
import data.usages

def get_usages(username):
    actions = collections.defaultdict(list)
    usages = data.usages.get_usages(username)
    if not usages: return []
    action_names = frozenset(action for _,value in usages for action in value.keys())
    for key, value in usages:
        for action in action_names:
            actions[action.title()].append(to_dict(key, value.get(action) or 0))
    return [{'key':action, 'values':sorted(values,key=operator.itemgetter('datetime'))} for action, values in actions.iteritems()]
    
def get_consumption(username):
    if username != 'salesforce':
        usages = data.usages.get_consumption(username)
        consumption = ((key, usage.get('count') or 0) for key,usage in usages)
    else:
        consumption = data.usages.get_salesforce_consumption()
    return [to_dict(*consumption_tuple) for consumption_tuple in consumption]
    
def to_dict(key, value):
    return {
            'datetime':datetimes.unpack_key_to_timestamp(key[1:]),
            'count':value
        }
