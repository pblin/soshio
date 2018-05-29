#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import timeframer
import aggregator
import trender
import contexter
import demographer
import data.analyses
from web.endpoint import celery
from report.run_async import run_async
    
def create(query, section, start, end):
    query = clean_query(query)
    timeframe, level = timeframer.get_timeframe_details(start, end)
    return get_create_section(section)(query, timeframe, level)
    
def clean_query(query):
    '''
    Clean up URL encoding that replaces spaces with +, *cough*Mashape*cough*
    '''
    return query.replace('+',' ')

def get_key(query, section, timeframe, level):
    return (",".join(
                    (section, level, query,
                    timeframe[0].isoformat(), timeframe[1].isoformat())
                   )).encode('utf8')

@celery.task()
def get_report(query, section, timeframe, level):
    results = list(data.analyses.get_reports(query, section, timeframe, level))
    report = aggregator.aggregate(results)
    if not report: return None
    report['trends'] = trender.create_trends(results)
    return report
    
def get_create_section(section):
    def create_section(query, timeframe, level):
        key = get_key(query, section, timeframe, level)
        result = run_async(get_report, key, "intelligence", query, section, timeframe, level)
        if result[0] == "ready":
            tmp = result[1] or {}
            tmp['state'] = 'ready'
            return tmp
        else:
            return {'state': 'running'}
    return specialized_creaters.get(section) or create_section

specialized_creaters = {
        'contexts': contexter.create,
        'demographics': demographer.create
    }
