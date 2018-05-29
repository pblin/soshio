#!/usr/bin/python
# -*- coding: utf-8 -*-

import couch
import json
import datetimes

def get_query_count(query, date):
    expected_key = [query, date.year, date.month, date.day]
    params = {
            'group_level':4, # NOTE: group on day
            'limit':1,
            'startkey':json.dumps(expected_key),
        }
    with couch.RestDatabase() as database:
        results = database.get_view('overview', 'datetime', params=params)
    try:
        first = results['rows'][0]
        if first['key'] != expected_key: return 0
        return int(first['value']['count'])
    except (KeyError, IndexError) as error:
        return 0

def get_feed_throughputs():
    params = {
            'descending': 'true',
            'stale':'ok',
            'limit': 7,
            'group_level': 3, # NOTE: group on day
        }
    with couch.RestDatabase() as database:
        results = database.get_view('feeds','datetime', params=params)
    if not results or 'rows' not in results or not results['rows']: return
    for row in results['rows']:
        key = [i for i in row['key'] if i]
        if not key: continue
        yield key, row['value']
        
def batch_delete(before_datetime=None, before_months=None):
    before_datetime = before_datetime or datetimes.get_datetime_months_ago(before_months)
    params = {'reduce':'false', 'endkey':datetimes.to_timestamp(before_datetime)}
    with couch.RestDatabase() as database:
        results = database.get_view('analyses','datetime_revs', params=params)
    if not results: return
    docs = map(get_doc_delete, results.get('rows',[]))
    if not docs: return
    with couch.RestDatabase() as database:
        return database.post_docs(docs)
        
def get_doc_delete(row):
    return {
            '_id': row['id'],
            '_rev': row['value'],
            '_deleted': True
        }
