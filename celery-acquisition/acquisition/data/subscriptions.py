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

    def ready_for_next(self, platform):
        platform = platform.replace(' ', '_')
        next_datetime = self._subscription.get(
            'next_query_datetime_' + platform, None)
        if next_datetime:
            ready = datetimes.now() >= next_datetime
        else:
            ready = True
        return ready

    def has_historic_data(self, platform):
        platform = platform.replace(' ', '_')
        return ('earliest_datetime_' + platform) in self._subscription


class SubscriptionManager():

    def __init__(self, collection_name='subscriptions'):
        self._collection_name = collection_name

    def _get_collection(self):
        return mongo.get_collection(self._collection_name)

    def get_queries(self, username=None, no_disabled=True):
        spec = {}
        if no_disabled:
            spec['$or'] = [
                {'disabled': False}, {'disabled': {'$exists': False}}]
        if username:
            spec['username'] = username
        with self._get_collection() as collection:
            return (
                set(subscription['query']
                    for subscription in collection.find(spec))
            )

    def mark_earliest_datetime(self, query, e_datetime, platform):
        if not e_datetime: #return if given null value
            return False 
        spec = {'query': query}
        platform = platform.replace(' ', '_')
        with self._get_collection() as collection:
            sub = self._subscription = collection.find_one(spec)
            updates = {
                    '$set': {
                        'earliest_datetime': e_datetime,
                        'earliest_datetime_' +
                        platform: e_datetime}}
            return collection.update(spec, updates, multi=True)

    def mark_latest_datetime(self, query, l_datetime, platform):
        spec = {'query': query}
        platform = platform.replace(' ', '_')
        with self._get_collection() as collection:
            updates = {'$set': {'latest_datetime_' + platform: l_datetime}}
            return collection.update(spec, updates, multi=True)

    def mark_next_query_datetime(self, query, platform, next_datetime=None):
        if not next_datetime:
            next_datetime = datetimes.now() + timedelta(hours=1)
        spec = {'query': query}
        platform = platform.replace(' ', '_')
        updates = {'$set': {'next_query_datetime_' + platform: next_datetime}}
        with self._get_collection() as collection:
            return collection.update(spec, updates, multi=True)
