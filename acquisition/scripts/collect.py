#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import datetimes
import background.endpoint
import data.subscriptions
import data.posts
    
def recollect_historical_data(username, hours=1): # NOTE: run without datecheck to recover whatever lost data possible
    logging.info(u'Collecting historic data for <{0}> back to <{1}> hours ago'.format(username, hours))
    is_old = datetimes.get_datetime_str_age_check(hours)
    subscriptions = data.subscriptions.get_subscriptions(username=username)
    query_objs = map(data.subscriptions.subscription_to_query_obj, subscriptions)
    background.endpoint.process_queries(query_objs, is_old)
