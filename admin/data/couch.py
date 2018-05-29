#!/usr/bin/python
# -*- coding: utf-8 -*-

import config.loader
import datetimes
import logging
import requests
import json

def get_db_env():
    return config.loader.load().get('COUCH_ENV',{})
    
def get_db_variables(uri=None, user=None, password=None):
    db_env = get_db_env()
    auth = (user or db_env.get('USER') or u'', password or db_env.get('PASSWORD') or u'')
    return uri or db_env.get('URI') or u'http://127.0.0.1:5984', auth
    
def load_json(func):
    def jsonified_func(*args, **kwargs):
        response = func(*args, **kwargs)
        logging.debug('Received response code <{0}> from Couch'.format(response.status_code))
        if response.status_code >= 300:
            logging.warning('Received unexpected response <{0}> from Couch'.format(response.text))
        return response.json()
    return jsonified_func
    
class RestDatabase(object):
    def __init__(self, *args, **kwargs):
        self.uri, self.auth = get_db_variables(*args, **kwargs)
        
    def __enter__(self):
        logging.debug(u'Starting database connection <{0}>'.format(self.uri))
        return self
        
    def __exit__(self,type,value,traceback):
        logging.debug(u'Closing database connection <{0}>'.format(self.uri))
        
    @load_json
    def _get(self, uri, **kwargs):
        logging.debug(u'GET from Couch <{0}>'.format(uri))
        return requests.get(uri, auth=self.auth, **kwargs)
        
    def get_doc(self, id):
        uri = u'{0}/{1}'.format(self.uri, id)
        return self._get(uri)
        
    @load_json
    def post_doc(self, doc):
        json_data = json.dumps(doc)
        headers = {'content-type': 'application/json; charset=utf8'}
        return requests.post(self.uri, auth=self.auth, data=json_data, headers=headers)
        
    @load_json
    def post_docs(self, docs):
        data = {'docs':[doc for doc in docs if doc]}
        json_data = json.dumps(data, default=datetimes.dthandler)
        uri = '{0}/_bulk_docs'.format(self.uri)
        headers = {'content-type': 'application/json; charset=utf8'}
        return requests.post(uri, auth=self.auth, data=json_data, headers=headers)
        
    def get_view(self, design, view, params=None):
        uri = u'{0}/_design/{1}/_view/{2}'.format(self.uri,design,view)
        return self._get(uri, params=params)
        
    def search(self, design, index, query, facets=None, sorts=None, **optional_params):
        params = {
                'query': self.create_search_query_param(query, facets) if facets else query,
                'sort': self.create_search_sort_param(sorts)
            }
        params.update(optional_params)
        uri = u'{0}/_design/{1}/_search/{2}'.format(self.uri,design,index)
        return self._get(uri, params=params)
        
    _lucene_operators = ('and','or','not','to')
    def create_search_query_param(self, query, facets=None):
        query = u'"{0}"'.format(query)
        if facets:
            for key, value in facets.items():
                if not value: continue
                value = u' '.join(term if term not in self._lucene_operators else term.upper() for term in value.split())
                value = u'({0})'.format(value) if ' TO ' not in value else value
                query += u' AND {0}:{1}'.format(key, value)
        return query

    def create_search_sort_param(self, sorts):
        if sorts:
            sort_strs = u'","'.join(sorts)
            return u'["{0}"]'.format(sort_strs)
    