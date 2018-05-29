#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import logging
import HTMLParser
import sentiment.analysis
import context.analysis
import services.geo

def analyze(post):
    logging.debug('Processing post id %s...' % post['id'])
    text = post.get('text','')
    if not text: return
    query = post.get('query')
    id = post.get('id')
    platform = post.get('platform')
    shares = clean_engagement(post.get('shares'))
    replies = clean_engagement(post.get('replies'))
    reach = clean_engagement(post.get('reach'))
    analysis = {
            '_id': u'{0}_{1}_{2}'.format(query, platform, id),
            'query': query,
            'id': post.get('id'),
            'user': post.get('username'),
            'datetime': post.get('datetime'),
            'gender': post.get('gender'),
            'location': get_location(post.get('location')),
            'text': text,
            'platform': post.get('platform'),
            'sentiment': sentiment.analysis.analyze(clean_html_codes(text)),
            'context': context.analysis.analyze(clean_html_codes(text)),
            'shares': shares,
            'replies': replies,
            'reach': reach,
            'influence': score_influence(shares, replies, reach),
            'uri': post.get('uri')
        }
    if analysis.get('sentiment'):
        analysis['sentiment']['emotions'] = adjust_emotions(analysis['sentiment']['emotions'])
    return dict((key, value) for key, value in analysis.iteritems() if value)
    
STOP_LOCATION_NAMES = (u'海外', u'其他', u'未知')
def clean_location(location):
    if not location: return
    for name in STOP_LOCATION_NAMES:
        location = location.replace(name, u'')
    return location

def get_location(location):
    if type(location) is dict:
        return location
    location = clean_location(location)
    if not location or location.isspace() or location == ",": return
    geo_info = services.geo.get_location(location)
    if not geo_info: return {'raw':location}
    english, coordinates = geo_info
    return {'english':english, 'coordinates':coordinates, 'raw':location}
    
def clean_engagement(value):
    if not value: return 0.0
    try:
        return float(value)
    except ValueError as error:
        logging.warning(u'Received non-numeral engagement value <{0}>'.format(value))
        return 0.0
    
def score_influence(shares, replies, reach):
    return shares + (replies * 2) + math.log1p(reach) # TODO: determine reasonable equation
    
def adjust_emotions(emotions): # TODO: move to sentiment analysis
    return dict((emotion, int(score * 1000)) for emotion, score in emotions.items())

def clean_html_codes(text):
    h = HTMLParser.HTMLParser()
    return h.unescape(text)

import unittest

class AnalystTests(unittest.TestCase):
    def test_clean_html_codes(self):
        result = clean_html_codes(u'北京&quot;法盲法官&quot;让人绝望')
        self.assertEqual(result, u'北京"法盲法官"让人绝望')


    
