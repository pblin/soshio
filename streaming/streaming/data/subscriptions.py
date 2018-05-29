#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
from . import mongo
from datetime import timedelta

import datetimes


class Subscription:

    def __init__(self, query, no_disabled=True, username=None):
        spec = {}
        if no_disabled:
            spec['$or'] = [
                {'disabled': False}, {'disabled': {'$exists': False}}]
        spec['query'] = query
        if username:
            spec['username'] = username
        with self._get_collection() as collection:
            self._subscription = collection.find_one(spec)

    def __init__(self, subscription):
        self._subscription = subscription

    def _get_collection(self):
        return mongo.get_collection('subscriptions')

    _Query = collections.namedtuple(
        'Query', ['query', 'keywords', 'match', 'args'])

    def get_query_obj(self):
        return self._Query(
            self._subscription['query'],
            self._subscription['keywords'].keys(),
            eval(self._subscription['match_func']['lambda']),
            self._subscription['match_func']['args']
        )

    def get_created_datetime(self):
        return self._subscription['datetime']

    def get_latest_datetime(self, platform):
        platform = platform.replace(' ', '_')
        result = self._subscription.get('latest_datetime_' + platform, None)
#        if not result:
#           #backward compatibility
#            result = self._subscription.get('last_queried', None)
        if not result:
            result = self.get_created_datetime()  # new subscription
        return result


class SubscriptionManager():

    def __init__(self, collection_name='subscriptions'):
        self._collection_name = collection_name

    def _get_collection(self):
        return mongo.get_collection(self._collection_name)

    def get_queries(self, username=None, no_disabled=True, keyword=None):
        spec = {}
        if no_disabled:
            spec['$or'] = [
                {'disabled': False}, {'disabled': {'$exists': False}}]
        if username:
            spec['username'] = username
        if keyword:
            spec['keywords.'+keyword] = {'$exists': True }
        with self._get_collection() as collection:
            return (
                set(subscription['query']
                    for subscription in collection.find(spec))
            )

    def get_subscriptions(self, keyword, no_disabled=True):
        spec = {}
        if no_disabled:
            spec['$or'] = [
                {'disabled': False}, {'disabled': {'$exists': False}}]
        if keyword:
            spec[u'keywords.'+keyword] = {'$exists': True }
        with self._get_collection() as collection:
            return [Subscription(subscription) 
                        for subscription in collection.find(spec)]

    def get_keywords(self, no_disabled=True):
        spec = {}
        if no_disabled:
            spec['$or'] = [
                {'disabled': False}, {'disabled': {'$exists': False}}]        
        with self._get_collection() as collection:
            keywords = set()
            for row in collection.find(spec, {'keywords':1, '_id':0}):
                keywords.update(row['keywords'].keys())
            return keywords
