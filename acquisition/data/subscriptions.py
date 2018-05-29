#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
import mongo
import datetimes

def get_collection():
    return mongo.get_collection('subscriptions')
    
def get_subscriptions(username=None, query=None, no_disabled=True):
    spec = {}
    if no_disabled: spec['$or'] = [{'disabled':False}, {'disabled':{'$exists':False}}]
    if query: spec['query'] = query
    if username: spec['username'] = username
    with get_collection() as collection:
        return collection.find(spec)

def mark_queried(query):
    spec = {'query': query}
    updates = {'$set': {'last_queried': datetimes.now()}}
    with get_collection() as collection:
        return collection.update(spec, updates)
        
def get_query_obj(query):
    spec = {
            'query': query,
            '$or': [{'disabled':False}, {'disabled':{'$exists':False}}]
        }
    with get_collection() as collection:
        subscription = collection.find_one(spec)
    return subscription_to_query_obj(subscription)
        
Query = collections.namedtuple('Query',['query','queried','keywords','match','args'])
def subscription_to_query_obj(subscription):
    return Query(
            subscription['query'],
            subscription.get('last_queried'),
            subscription['keywords'].keys(),
            eval(subscription['match_func']['lambda']),
            subscription['match_func']['args']
        )
