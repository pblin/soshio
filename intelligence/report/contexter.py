#!/usr/bin/python
# -*- coding: utf-8 -*-
import collections

import data.analyses
from web.endpoint import celery
from report.run_async import run_async

def get_key(query, timeframe):
    return ",".join(("contexts", query.encode('utf-8'), timeframe[0].isoformat(), timeframe[1].isoformat()))

def create(query, timeframe, level):
    key = get_key(query, timeframe)
    result = run_async(get_contexts, key, "intelligence", query, timeframe, level)
    if result[0] == "ready":
        return {'state': 'ready', 'contexts': result[1]}
    else:
        return {'state': 'running'}

def aggregate_contexts(rows):
    counts = collections.Counter()
    sentiments = collections.defaultdict(collections.Counter)
    for row in rows:
        context, count, sentiment = transform_row(row)
        counts.update({context:count})
        sentiments[context].update(sentiment)
    counts += collections.Counter() # removes 0 count items
    for context, count in counts.most_common(20):
        yield {
                'raw': context,
                'count': count,
                'sentiment': determine_sentiment(sentiments[context])
            }
    
def transform_row(row):
    key, val = row
    count = val['count']
    context = key[-1]
    if count < 2: return 'removal', 0, {}
    return context, count, val['sentiment']

def determine_sentiment(sentiment):
    diff = abs(sentiment['positive'] - sentiment['negative'])
    if diff < sentiment['neutral']: return 'neutral'
    return sentiment.most_common(1)[0][0]

@celery.task()
def get_contexts(query, timeframe, level):
    rows = data.analyses.get_counters(query, 'context', timeframe, level)
    return list(aggregate_contexts(rows))
