#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re
import jianfan
import collections
import jieba
import os.path

cleaner = re.compile(r'<[^<]*?>|\$|\&[\w]{2,4}\;|http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}[^\s]*|\@[^:\s]+:|\\\\w')
stopper = re.compile(ur'(?<!目)的(?!(確|确))',flags=(re.UNICODE))
null_char = '\x00'.decode('utf-8')
def clean_string(text):
    try:
        return stopper.sub(u' ',cleaner.sub(u' ',text)).replace(null_char,u' ').strip().lower()
    except Exception, error:
        logging.error(u'Error <{0}> occured during clean_string, for string <{1}>'.format(repr(error), repr(text)))

alphebeter = re.compile(r'\W?(\w+)\W?')
def segment_by_space(text):
    return list(alphebeter.findall(text))
    
characterizer = re.compile(ur'\w+',flags=(re.UNICODE))
def segment_by_char(text, ngram=4):
    for segment in characterizer.findall(text):
        for i in range(len(segment)):
            for j in range(1,len(segment)+1):
                if j - i > ngram: break
                if segment[i:j]: yield segment[i:j]
    
symbolizer = re.compile(ur'\W\W+',flags=(re.UNICODE))
def segment_by_symbol(text):
    for segment in symbolizer.findall(text.replace(u' ','x')):
        segment = segment.strip()
        for i in range(len(segment)-1):
            for j in range(1,len(segment)):
                if i != j: yield segment[i:j+1]
    
def tokenize(text):
    logging.debug('Original text is <{0}>'.format(repr(text)))
    bag = collections.Counter()
    text = clean_string(text.strip())
    
    for word in segment_by_space(text): # segmentation for western words
        bag.update([word])
        text = text.replace(word, ' ', 1)
    bag.update(list(segment_by_char(text))) # segmentation for chinese words
    bag.update(list(segment_by_symbol(text))) # segmentation for symbols to catch emoticons
    return bag
    
dictionary_path = os.path.join('calc', u'tokens.dict')
jieba.load_userdict(dictionary_path)
def tokenize_by_jieba(text, shortest_length=1):
    logging.debug('Original text is <{0}>'.format(repr(text)))
    text = jianfan.ftoj(text)
    text = clean_string(text.strip())
    logging.debug(" ".join(jieba.cut(text, cut_all=False)))
    return collections.Counter(term for term in jieba.cut(text, cut_all=False) if len(term) > shortest_length)


import unittest

class TokenizeTests(unittest.TestCase):
    def test_clean_string(self):
        result = clean_string(u'http://google.com <apple></apple>. $ &xy13; 的')
        self.assertEqual(result, '')
        result = clean_string(u'的確 目的 的确')
        self.assertEqual(result, u'的確 目的 的确')
    
    def test_segment_by_space(self):
        result = segment_by_space('this is')
        self.assertItemsEqual(list(result), ['this','is'])
        
    def test_segment_by_char(self):
        result = segment_by_char(u'你快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'你快',u'你快樂',u'你快樂嗎',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = segment_by_char(u'你 快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = segment_by_char(u'你,快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = segment_by_char(u'你，快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = segment_by_char(u'你。快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = segment_by_char(u'不快樂')
        self.assertItemsEqual(list(result), [u'不',u'不快',u'不快樂',u'樂'])
        
    def test_segment_by_symbol(self):
        result = segment_by_symbol(u'你:)快樂嗎')
        self.assertItemsEqual(list(result), [u':)'])
        result = segment_by_symbol(u'你:) 快樂嗎')
        self.assertItemsEqual(list(result), [u':)'])
        result = segment_by_symbol(u'你:-)快樂嗎')
        self.assertItemsEqual(list(result), [u':-',u':-)',u'-)'])
        
    def test_tokenize(self):
        result = tokenize('this is')
        self.assertItemsEqual(list(result), ['this','is'])
        result = tokenize(u'你快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'你快',u'你快樂',u'你快樂嗎',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = tokenize(u'this is 你快樂嗎')
        self.assertItemsEqual(list(result), ['this', 'is', u'你',u'你快',u'你快樂',u'你快樂嗎',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = tokenize(u'this is你快樂嗎')
        self.assertItemsEqual(list(result), ['this', 'is', u'你',u'你快',u'你快樂',u'你快樂嗎',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = tokenize(u'你[快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎'])
        result = tokenize(u'你:)快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎',u':)'])
        result = tokenize(u'你:-)快樂嗎')
        self.assertItemsEqual(list(result), [u'你',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎',u':-',u':-)',u'-)'])
        result = tokenize(u'this is你快樂嗎 :)')
        self.assertItemsEqual(list(result), ['this', 'is', u'你',u'你快',u'你快樂',u'你快樂嗎',u'快',u'快樂',u'快樂嗎',u'樂',u'樂嗎',u'嗎',u':)'])
