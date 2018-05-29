#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import math
import collections
import heapq
import jieba
import jieba.analyse
import calc.extract
import calc.tokenize

def get_topics(text):
    k = int(len(text) * 3.0 / 140.0)
    bag = calc.tokenize.tokenize_by_jieba(text)
    for term in jieba.analyse.extract_tags(text, topK=k):
        if term.isspace(): continue
        yield term, bag[term]

def get_headlines(text):
    return calc.extract.yield_bracketed_terms(text, u'【】')

def get_trends(text):
    return calc.extract.yield_bracketed_terms(text, u'##')
    
brackets = (u'《》',u'「」',u'『』')
def get_titles(text):
    for bracket in brackets:
        for title in calc.extract.yield_bracketed_terms(text, bracket):
            yield title
    
candidate_funcs = {
        'headlines':get_headlines,
        'trends':get_trends,
        'titles':get_titles,
        # 'names':calc.extract.yield_names_near_titles,
        # 'users':calc.extract.yield_usernames,
        # 'uris':calc.extract.yield_uris,
    }
    
def normalize_text(text):
    return calc.extract.clean_symbols(text).strip().lower().replace(u'.',u'DOT')

def yield_analysis(text):
    logging.debug(u'Extracting context from text <{0}>'.format(text))
    yield 'topics', dict(get_topics(text))
    for info_type, candidate_func in candidate_funcs.items():
        candidates = list(candidate_func(text))
        if candidates:
            bag = collections.Counter(map(normalize_text, candidates))
            yield info_type, bag

def analyze(text):
    return dict(yield_analysis(text))