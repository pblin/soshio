#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetimes
import logging
import mongo

def get_collection():
    return mongo.get_collection('subscriptions')
    
def get_subscription(username, query):
    with get_collection() as collection:
        return collection.find_one({'username':username, 'query':query})
        
def get_subscriptions(username=None, query=None):
    spec = {}
    if username: spec['username'] = username
    if query: spec['query'] = query
    with get_collection() as collection:
        return collection.find(spec)
    
def save_subscription(username, query, **notes):
    subscription_obj = create_subscription(username, query, **notes)
    with get_collection() as collection:
        return collection.save(subscription_obj, safe=True)
    
def remove_subscriptions(username, query=None):
    spec = {'username':username}
    if query: spec['query'] = query
    with get_collection() as collection:
        return collection.remove(spec) is None
    
def remove_users_subscriptions(usernames):
    get_usernames_spec = lambda username: {'username':username}
    spec = {'$or':map(get_usernames_spec, usernames or [])}
    with get_collection() as collection:
        return collection.remove(spec)
        
def create_subscription(username, query, **details):
    subscription = {
            '_id': u'{0}_{1}'.format(username, query),
            'username': username,
            'query': query,
            'datetime': datetimes.now()
        }
    subscription.update(details)
    return subscription
