#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import collections
import math
import data.terms
import data.sentiments
import calc.tokenize
import calc.extract
import config.loader
import caching

def analyze(text):
    logging.info(u'Analyzing sentiment for text <{0}>'.format(text))
    bag = get_sentiment_bag(text)
    logging.debug(" ".join(bag))
    logging.info(u'Analysing with <{0}> terms'.format(len(bag)))
    
    logging.info(u'Determining sentiment emotions')
    emotions = determine_emotions(bag, len(text))

    logging.info(u'Determining sentiment polarity')
    polarity = determine_polarity(emotions)
    
    logging.info(u'Determining polarity classification')
    classification = determine_classification(polarity)

    logging.info(u'Completed analysis')
    return {
        'polarity': polarity,
        'emotions': emotions,
        'classification': classification
    }
    
def clean_text(text):
    for bracketed_term in calc.extract.yield_bracketed_terms(text):
        text = text.replace(bracketed_term,u' ')
    for quotes in calc.extract.yield_quotes(text):
        text = text.replace(quotes,u' ')
    return text
    
def get_sentiment_bag(text):
    cleaned_text = clean_text(text)
    iter_terms = calc.tokenize.tokenize_by_jieba(cleaned_text, shortest_length=0)
    return collections.Counter(iter_terms)
    
@caching.cached() # TODO: use Reddis cache???
def get_terms_cache():
    return dict(data.terms.get_terms())
    
def determine_emotions(bag, text_length):
    emotions = collections.defaultdict(float)
    terms_sentiments = get_terms_cache()
    for term, count in bag.items():
        for emotion, pmi in terms_sentiments.get(term,{}).iteritems():
            logging.debug(term + " " + emotion)
            emotions[emotion] += pmi
    len_offset = math.log1p(text_length)
    return dict((emotion, score / len_offset) for emotion, score in emotions.iteritems())
    
@caching.cached()
def get_sentiments_cache():
    return dict(data.sentiments.get(polarity=True))
    
def determine_polarity(emotions):
    if not emotions: return 0.0
    sentiments = get_sentiments_cache()
    total_polarity = sum(sentiments.get(emotion,0) * polarity for emotion, polarity in emotions.iteritems())
    return standardize(total_polarity)
    
def standardize(x):
    mean = config.loader.load().get('POLARITY_MEAN') or 0.0
    deviation = config.loader.load().get('POLARITY_DEVIATION') or 1.0
    shifted_x = (x - mean) * deviation
    return math.erf(shifted_x ** 3.0)
    
def determine_classification(polarity):
    deviation = config.loader.load().get('CLASSIFICATION_DEVIATION') or 0.5
    mean = config.loader.load().get('CLASSIFICATION_MEAN') or 0.0
    if polarity <= mean - deviation: return 'negative'
    if mean + deviation <= polarity: return 'positive'
    return 'neutral'
