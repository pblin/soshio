#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import pymongo
import config.loader

def get_collection(collection_name, uri=None, db_name=None):
    return AutomatedCollection(collection_name, uri, db_name)
    
def get_db_env():
    return config.loader.load().get('MONGO_ENV',{})
    
def get_db_variables(uri=None, db_name=None):
    force_local = config.loader.load().get('FORCE_LOCAL',False)
    if force_local: uri = u'localhost'
    return uri or get_db_env().get('URI',u'localhost'), db_name or get_db_env().get('DB')
    
class AutomatedCollection(object):
    def __init__(self, collection_name, uri=None, db_name=None):
        self.collection_name = collection_name
        self.uri, self.db_name = get_db_variables(uri, db_name)
        
    def __enter__(self):
        logging.info('Starting database connection <{0}>'.format(self.uri))
        self.connection = pymongo.Connection(self.uri)
        logging.info('Loaded database name <{0}>'.format(self.db_name))
        self.database = self.connection[self.db_name]
        try:
            logging.info('Loading collection <{0}>'.format(self.collection_name))
            self.collection = self.database[self.collection_name]
        except KeyError:
            logging.info('Creating new collection <{0}>'.format(self.collection_name))
            self.collection = self.database.create_collection(self.collection_name)
        return self.collection
        
    def __exit__(self,type,value,traceback):
        logging.info('Closing database connection <{0}>'.format(self.uri))
        self.connection.disconnect()
    
    
import unittest

class MongoTests(unittest.TestCase):
    def test_get_collection_creates_if_missing(self):
        def test_get_connection(local=False):
            return {'test_db':self.TestDb()}
        
        get_connection = test_get_connection
        collection = get_collection('test_name', db_name='test_db')
        self.assertTrue(collection)
        
    class TestDb(dict):
        def create_collection(self, x):
            return True
    
    class TestCollection(object):
        def __init__(self):
            self.count = 0
        
        def insert(self, x):
            self.count += 1
