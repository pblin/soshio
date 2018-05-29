#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import random
import datetimes
import collect.search
import data.subscriptions
import data.posts

def run(interval=3.0):
    logging.info(u'Starting cron process')
    is_old = datetimes.get_datetime_str_age_check(interval/60.0)
    process_queries(yield_query_objs(is_old), is_old)
    logging.info(u'Ending cron process')
    
def process_queries(query_objs, is_old):
    for query_obj in query_objs:
        posts = collect.search.search(query_obj, is_old=is_old)
        logging.info(u'Collected <{0}> posts for <{1}>'.format(len(posts), query_obj.query))
        data.posts.push(posts)
        data.subscriptions.mark_queried(query_obj.query)
    
def yield_query_objs(is_old):
    # Uses generator to check for latest datetime for each query
    # This is preferred over bulk filtering for parallelizing collectors
    unique_queries = list(get_unique_queries())
    random.shuffle(unique_queries)
    for query in unique_queries:
        query_obj = data.subscriptions.get_query_obj(query)
        if query_obj.queried and not is_old(query_obj.queried): continue
        yield query_obj
        
def get_unique_queries(*args, **kwargs):
    subscriptions = data.subscriptions.get_subscriptions(*args, **kwargs)
    return set(subscription['query'] for subscription in subscriptions)
    