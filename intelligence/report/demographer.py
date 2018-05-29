#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import random
import collections

import report.timeframer as timeframer
import aggregator
import report.trender as trender
import data.analyses
from web.endpoint import celery
from report.run_async import run_async

def get_key(query, timeframe):
    return "demographics," + ",".join((query.encode('utf-8'), timeframe[0].isoformat(), timeframe[1].isoformat()))

def create(query, timeframe, level):
    key = get_key(query, timeframe)
    result = run_async(get_demographics, key, "intelligence", query, timeframe, level)
    if result[0] == "ready":
        tmp = result[1]
        tmp['state'] = 'ready'
        return tmp
    else:
        return {'state': 'running'}

@celery.task()
def get_demographics(query, timeframe, level):
    report = create_genders(query, timeframe, level)
    report['locations'] = create_locations(query, timeframe, level)
    return report    

def create_genders(query, timeframe, level):
    results = list(data.analyses.get_reports(query, 'demographics', timeframe, level, view='datetime_genders'))
    report = aggregator.aggregate(results)
    if not report: return {}
    report['trends'] = trender.create_trends(results)
    return report

def create_locations(query, timeframe, level):
    if level == "hour": # We don't have hour level for location
        level = "day" 
    rows = data.analyses.get_counters(query, 'demographics', timeframe, level, view='datetime_locations')
    locations = aggregate_locations(rows)
    return dict(decode_locations(locations))

def aggregate_locations(rows):
    collection = collections.Counter()
    for row in rows:
        collection.update(transform_location_row(row))
    collection += collections.Counter()
    return collection

def transform_location_row(row):
    key, count = row
    location = key[-1]
    if 'english' not in location or location['english'].isnumeric() or location['english'].isspace():
        return {'removal':0}
    return {json.dumps(location):count}

def decode_locations(locations):
    for info_json, count in locations.iteritems():
        info = json.loads(info_json)
        yield info['english'], {
                'coordinates': info['coordinates'],
                'count': count,
                'chinese': info['raw']
            }
