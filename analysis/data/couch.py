#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import requests
import time
import json
import config.loader
import datetime

import datetimes

def get_db_env():
    return config.loader.load().get('COUCH_ENV',{})
    
def get_db_variables(uri=None, user=None, password=None):
    force_local = config.loader.load().get('FORCE_LOCAL',False)
    db_env = get_db_env()
    if force_local: uri = u'localhost'
    return [
            uri or db_env.get('URI',u'http://127.0.0.1:5984'),
            user or db_env.get('USER',u''),
            password or db_env.get('PASSWORD',u''),
        ]
    
def load_json(func):
    def jsonified_func(*args, **kwargs):
        response = func(*args, **kwargs)
        logging.debug('Received response code <{0}> from Couch'.format(response.status_code))
        if response.status_code >= 300:
            if '"error":"case_clause"' not in response.text: # NOTE: ignore duplicate doc id error, the docs are still saved
                logging.warning('Received unexpected response <{0}> from Couch'.format(response.text))
        try:
            return response.json()
        except ValueError, error:
            logging.error(u'<{0}> thrown for function <{1}> with arguments <{2}> <{3}>; returning empty dict'.format(error, repr(func), repr(args), repr(kwargs)))
            return {}

    return jsonified_func
    
class RestDatabase(object):
    def __init__(self, uri=None):
        self.uri, user, password = get_db_variables(uri)
        self.auth = (user, password)
        
    def __enter__(self):
        logging.debug(u'Starting database connection <{0}>'.format(self.uri))
        return self
        
    def __exit__(self,type,value,traceback):
        logging.debug(u'Closing database connection <{0}>'.format(self.uri))
        
    @load_json
    def _get(self, uri, **kwargs):
        logging.debug(u'GET from Couch <{0}> with params <{1}>'.format(uri, kwargs.get('params') or None))
        retries = 3
        while retries:            
            try:
                return requests.get(uri, auth=self.auth, **kwargs)
            except requests.exceptions.ConnectionError, error:
                logging.error(u'Received error <{0}> will try again after sleep'.format(error))
                time.sleep(1)
            retries -= 1
        
    def get_db_info(self):
        return self._get(self.uri)
        
    def get_doc(self, id):
        uri = u'{0}/{1}'.format(self.uri, id)
        return self._get(uri)
        
    def get_view(self, design, view, params=None):
        uri = u'{0}/_design/{1}/_view/{2}'.format(self.uri,design,view)
        return self._get(uri, params=params)
        
    @load_json
    def post_doc(self, doc):
        json_data = json.dumps(doc, default=datetimes.dthandler)
        headers = {'content-type': 'application/json; charset=utf8'}
        return requests.post(self.uri, auth=self.auth, data=json_data, headers=headers)
        
    @load_json
    def post_docs(self, docs):
        data = {'docs':[doc for doc in docs if doc]}
        json_data = json.dumps(data, default=datetimes.dthandler)
        uri = '{0}/_bulk_docs'.format(self.uri)
        headers = {'content-type': 'application/json; charset=utf8'}
        return requests.post(uri, auth=self.auth, data=json_data, headers=headers)
        
    def search(self, design, index, facets=None, sorts=None, **optional_params):
        params = {
                'query': self.create_search_param(facets),
                'sort': self.create_search_sort_param(sorts)
            }
        params.update(optional_params)
        uri = u'{0}/_design/{1}/_search/{2}'.format(self.uri,design,index)
        return self._get(uri, params=params)
        
    def create_search_param(self, facets=None):
        if not facets: return
        return u' AND '.join(u'{0}:{1}'.format(key.lower(),value) for key,value in facets.items() if value)

    def create_search_sort_param(self, sorts):
        if not sorts: return
        sort_strs = u'","'.join(sorts)
        return u'["{0}"]'.format(sort_strs)

    
