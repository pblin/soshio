#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetimes
import logging
import json
import couch

def get_doc(doc_id):
    with couch.RestDatabase() as database:
        doc = database.get_doc(doc_id)
        doc.pop('_id')
        doc.pop('query')
        return doc
        
def update_doc(doc_id, **updates):
    with couch.RestDatabase() as database:
        return database.post_update('analyses','analysis',doc_id, params=updates)
        
def search_query(query, timeframe=None, facets=None, sorts=None, **optional_params):
    facets = facets or {}
    if timeframe:
        datetime_facet = u'[{0} TO {1}]'.format(*map(datetimes.to_timestamp, timeframe))
        facets.update({'datetime': datetime_facet})
    with couch.RestDatabase() as database:
        return database.search('queries', 'facets', query, facets=facets, sorts=sorts, **optional_params)
        
report_designs = ['overview','demographics','sentiments','export']
def get_reports(query, design, timeframe, level, view='datetime', group=True, options=None):
    if design not in report_designs: return []
    level_num = get_group_level(level)
    params = get_hierarchical_datetime_keys(query, level_num, timeframe)
    if group: params['group_level'] = level_num
    return get_view_results(design, view, params, options=options)
    
counter_designs = ['demographics','context']
def get_counters(query, design, timeframe, level, view='datetime', options=None):
    if design not in counter_designs: return []
    level_num = get_group_level(level)
    params = get_hierarchical_datetime_keys(query, level_num, timeframe, level=level)
    params['group_level'] = level_num + 2
    return get_view_results(design, view, params, options=options)

def get_view_results(design, view, params, options=None):
    if options: params.update(options)
    with couch.RestDatabase() as database:
        results = database.get_view(design, view, params=params)
    if not results: return []
    return ((row['key'], row['value']) for row in results.get('rows',[]) if row['value'])
    
def get_export_docs(query, timeframe):
    return get_reports(query, 'export', timeframe, 'day', group=False, options={'reduce':'false'})
    
group_level = ['query','year','month','day','hour']
def get_group_level(level):
    return group_level.index(level) + 1

def get_hierarchical_datetime_keys(query, level_num, timeframe, level=None):
    start, end = timeframe
    base_key = [query]
    if level: base_key.append(level)
    levels = [group_level[key] for key in range(1,level_num)]
    startkey = base_key + [getattr(start, attr) for attr in levels]
    endkey = base_key + [getattr(end, attr) for attr in levels]
    endkey[-1] += 1
    #logging.warning(startkey)
    #logging.warning(endkey)
    return {
            'startkey':json.dumps(startkey),
            'endkey':json.dumps(endkey),
        }
