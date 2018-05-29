#!/usr/bin/python
# -*- coding: utf-8 -*-

import data.analyses

def execute(mode, **params):
    if 'trial_mode' in params: return
    if mode not in execute_funcs: return
    return execute_funcs[mode](**params)

def get(post_id):
    return data.analyses.get_doc(post_id)
    
def update(post_id, sentiment=None): # NOTE: the fields here should match the supported functions on the update handler
    if not sentiment: return
    return data.analyses.update_doc(post_id, sentiment=sentiment)

def update_by_text(post_id, sentiment=None):
    if not sentiment: return
    post_text = get(post_id).get('text')
    if not post_text: return
    facets = {'text':u'"{0}"'.format(post_text)} # TODO: determine a good way to not include replies
    # NOTE: explicitly limited bulk update to the closest 20 posts for speed and reduce impact of bad updates
    results = data.analyses.search_query('', facets=facets, limit=20).get('rows') or []
    post_ids = set(result['id'] for result in results)
    post_ids.add(post_id)
    return {'results':[update(id, sentiment=sentiment) for id in post_ids]}

execute_funcs = {
        'get': get,
        'id': update,
        'text': update_by_text
    }
