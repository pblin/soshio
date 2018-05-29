#!/usr/bin/python
# -*- coding: utf-8 -*-

import timeframer
import data.analyses

def create(query, start, end, trial_mode=False, **kwargs):
    timeframe = timeframer.get_timeframe_from_str(start, end)
    return create_conversations(query, timeframe, **kwargs if not trial_mode else {})

def create_conversations(query, timeframe, **kwargs):
    next = kwargs.pop('next')[0] if 'next' in kwargs else None
    sorts = kwargs.pop('sort') if 'sort' in kwargs else ['-datetime']
    facets = dict((key,value[0] if key == 'text' else u'"{0}"'.format(value[0])) for key, value in kwargs.items() if value and value[0])
    result = data.analyses.search_query(query, timeframe, facets=facets, sorts=sorts, bookmark=next)
    return parse_result(result)
    
def parse_result(result):
    rows = result.get('rows') or []
    return {
            'conversations': map(create_conversation, rows),
            'next': result.get('bookmark'),
            'count': result.get('total_rows')
        }
    
def create_conversation(row):
    post = row['fields']
    post['id'] = row['id']
    return post
