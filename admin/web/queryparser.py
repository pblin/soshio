#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import string
import collections

operator_strs = ('and','or','not','(',')','|','&','-')
def create_query_lambda(query):
    new_query = query.replace('(','( ').replace(')',' )').lower()
    create_boolean_code, lowercases = get_create_boolean_code()
    output = u' '.join(create_boolean_code(new_query))
    input = list(string.ascii_lowercase.strip(u''.join(lowercases)))
    evalable = u'lambda {0} : {1}'.format(u','.join(input), output)
    keywords = list(term for term in new_query.split() if term not in operator_strs)
    return evalable, keywords
    
def get_create_boolean_code():
    lowercases = collections.deque(string.ascii_lowercase)
    def create_boolean_code(query):
        terms = query.split()
        for i, term in enumerate(terms): # TODO: handle quotes " "
            if term in operator_strs: yield term
            else:
                yield lowercases.popleft()
                if i<len(terms)-1 and terms[i+1] not in operator_strs:
                    yield u'and'
    return create_boolean_code, lowercases

def get_keywords_needed(query):
    set_query = query.lower().replace(' not ',' - ').replace(' and ',' - ').replace(' or ',' | ')
    lambda_str, keywords = create_query_lambda(set_query)
    inputs = (set([keyword]) for keyword in keywords)
    try:
        return list(eval(lambda_str)(*inputs))
    except TypeError as error:
        logging.error(u'Failed parsing query <{0}>, with exception: {1}'.format(repr(query), error.message))
        return []

import unittest
    
class QueryParserTests(unittest.TestCase):
    def test_get_keywords_needed_handles_and(self):
        result = get_keywords_needed(u'this and that')
        self.assertIn('this', result)
        self.assertNotIn('that', result)
        
    def test_get_keywords_needed_handles_or(self):
        result = get_keywords_needed(u'this or that')
        self.assertIn('this', result)
        self.assertIn('that', result)
        
    def test_get_keywords_needed_handles_not(self):
        result = get_keywords_needed(u'this and not that')
        self.assertIn('this', result)
        self.assertNotIn('that', result)
        
    def test_get_keywords_needed_handles_brackets(self):
        result = get_keywords_needed(u'this or (that and here)')
        self.assertIn('this', result)
        self.assertIn('that', result)
        result = get_keywords_needed(u'(this or that) and here')
        self.assertNotIn('this', result)
        self.assertIn('here', result)
        result = get_keywords_needed(u'(this or that) or here')
        self.assertIn('this', result)
        self.assertIn('that', result)
        self.assertIn('here', result)
        result = get_keywords_needed(u'(this and that) and here')
        self.assertIn('this', result)
        self.assertNotIn('that', result)
        self.assertNotIn('here', result)
        
