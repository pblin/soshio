#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import caching
import calc.pmi
import data.docs

def score_term(term, bases):
    term_occurs = data.docs.get_term_doc_count(term) # NOTE: don't cache to save memory and storage
    def score_term_base(base):
        base_occurs = get_cached_occur(base)
        #if not (term_occurs and base_occurs): return 0.0
        co_occurs = data.docs.get_term_doc_count(term, base)
        logging.info("Score for (%s, %s): %d, %d, %d" % (term, base, 
                                                         term_occurs, base_occurs, co_occurs))
        simularity = calc.pmi.calculate_score(co_occurs, term_occurs, base_occurs)
        return simularity * (1.0 if not is_negation_of(term,base) else -1.0)
    return map(score_term_base, bases)
    
@caching.cached()
def get_cached_occur(term):
    return data.docs.get_term_doc_count(term)
        
def is_negation_of(large, small):
    if len(large) < 2: return False
    if small not in large: return False
    for negation in (u'不',u'唔',u'冇'):
        if large.startswith(negation):
            return True
    return False
