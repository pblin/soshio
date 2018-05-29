#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import couch
import json

def search_query(facets=None, sorts=None, **optional_params):
    facets = facets or {}
    with couch.RestDatabase() as database:
        return database.search('queries', 'facets', facets=facets, sorts=sorts, **optional_params)
        
def search_term(term, *args, **kwargs):
    facets = {'text':u'("{0}")'.format(term)} if term else {}
    return search_query(facets=facets, *args, **kwargs)
    
def search_hashed_doc_ids(term, *args, **kwargs):
    hashed_doc_ids = set([])
    kwargs['limit'] = kwargs.get('limit') or 200
    def search_hashed_ids_bookmark(term, *args, **kwargs):
        results = search_term(term, *args, **kwargs)
        hashed_ids = [hash(result['id']) for result in results.get('rows',[])]
        return hashed_ids, results.get('bookmark')
        
    hashed_ids, bookmark = search_hashed_ids_bookmark(term, *args, **kwargs)
    while hashed_ids and bookmark and bookmark != 'g2o':
        hashed_doc_ids = hashed_doc_ids.union(hashed_ids)
        hashed_ids, bookmark = search_hashed_ids_bookmark(term, bookmark=bookmark, *args, **kwargs)
    return list(hashed_doc_ids)
    
def get_term_doc_count(*terms):
    term = terms[0] if len(terms) == 1 else u'" AND "'.join(terms)
    return search_term(term).get('total_rows') or 0

def get_total_doc_count():
    with couch.RestDatabase() as database:
        return database.get_db_info().get('doc_count') or 0
        
def get_all_docs_texts():
    params = {'group_level':0}
    with couch.RestDatabase() as database:
        results = database.get_view('aggregate','texts',params=params)
        return results['rows'][0]['value']
    
