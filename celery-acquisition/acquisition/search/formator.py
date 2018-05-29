#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetimes


def map_results(query, statuses):
    map_query_status = get_map_query_status_func(query)
    return map(map_query_status, (status for status in statuses if status))


def get_map_query_status_func(query):
    def map_func(status):
        status_obj = dict(status)
        status_obj['id'] = unicode(status_obj['id'])
        status_obj['datetime'] = datetimes.extract_datetime(
            status_obj['datetime'])
        status_obj.update({'query': query})
        return status_obj
    return map_func
