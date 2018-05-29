#!/usr/bin/python
# -*- coding: utf-8 -*-

import couch
import config.loader
import datetimes
import json

def get_database(for_salesforce=False):
    db_variables = get_db_variables(for_salesforce)
    return couch.RestDatabase(*db_variables)
    
def get_db_variables(for_salesforce):
    target = 'LOG_ENV' if not for_salesforce else 'SALESFORCE_ENV'
    env = config.loader.load().get(target) or {}
    return env.get('URI'), env.get('USER'), env.get('PASSWORD')
    
def get_usages(username, limit=14):
    params = {
            'descending':'true',
            'startkey':json.dumps([username,9999]),
            'endkey':json.dumps([username]),
            'group_level':4, # NOTE: group on day
            'limit': limit
        }
    with get_database() as database:
        results = database.get_view('datetime', 'counts', params=params)
    return list_results(results)
    
def get_consumption(username, limit=6):
    params = {
            'descending':'true',
            'startkey':json.dumps([username,9999]),
            'endkey':json.dumps([username]),
            'group_level':3, # NOTE: group on month
            'limit': limit
        }
    with get_database() as database:
        results = database.get_view('datetime', 'consumption', params=params)
    return list_results(results)
    
def get_salesforce_consumption():
    params = {'descending':'true', 'group_level':3} # NOTE: group on month
    with get_database(for_salesforce=True) as database:
        results = database.get_view('datetime', 'counts', params=params)
    return list_results(results)
    
def list_results(results):
    if not results: return []
    return list((row['key'], row['value']) for row in results['rows'])

def log_usage(username, action, **notes):
    usage = {
            'username': username,
            'action': action,
            'datetime': datetimes.now_in_timestamp()
        }
    if notes: usage.update(notes)
    with get_database() as database:
        return database.post_doc(usage)

def get_past_subscriptions(username):
    params = {
            'descending':'true',
            'startkey':json.dumps([username,9999]),
            'endkey':json.dumps([username]),
            'group_level':1 # NOTE: group on user
        }
    with get_database() as database:
        results = database.get_view('datetime', 'consumption', params=params)
    try:
        first = results['rows'][0]
        if first['key'][0] != username: return []
        return first['value']['consumptions'].keys()
    except (KeyError, IndexError) as error:
        return []
