#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import mongo

def get_collection():
    return mongo.get_collection('terms')
    
def save_terms(items):
    to_dict = lambda item: {'_id':item[0], 'sentiments':item[1], 'updated':datetime.datetime.now()}
    terms = map(to_dict, items)
    with get_collection() as collection:
        return map(collection.save, terms)
        
def get_terms(newer_than=None, sentiments=True):
    spec = {}
    if newer_than: spec['updated'] = {'$gte': datetime.datetime.now() - datetime.timedelta(days=newer_than)}
    fields = {'_id':1}
    if sentiments: fields['sentiments'] = 1
    with get_collection() as collection:
        for term in collection.find(spec, fields):
            result = [term['_id']]
            if sentiments: result.append(term['sentiments'])
            yield tuple(result)
        
def remove_terms(ttl=None):
    query = {}
    if ttl: query['updated'] = {'$lte':datetime.datetime.now() - datetime.timedelta(days=ttl)}
    with get_collection() as collection:
        return collection.remove(query)
