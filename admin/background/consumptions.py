#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetimes
import data.users
import data.analyses
import data.subscriptions
import data.usages

def run(interval):
    if interval == 'day':
        user_ids = [user['_id'] for user in data.users.get_all_active_users()]
        map(log_data_usage, user_ids)
        
def log_data_usage(username, date=None):
    date = date or datetimes.get_datetime_ago(days=1)
    consumptions = get_consumptions(username, date)
    count = sum(consumptions.itervalues())
    datetime = datetimes.to_timestamp(date)
    return data.usages.log_usage(username, 'consumption', consumptions=consumptions, count=count, datetime=datetime)

def get_consumptions(username, date):
    queries = get_queries(username)
    return dict((query, data.analyses.get_query_count(query, date=date)) for query in queries)
    
def get_queries(username):
    subscriptions = data.subscriptions.get_subscriptions(username)
    return [subscription.get('query') or subscription.get('keyword') for subscription in subscriptions]
