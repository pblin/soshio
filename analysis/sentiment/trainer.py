#!/usr/bin/python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import sys, os
    sys.path.append(os.getcwd())

import logging
import itertools
import caching
import config.loader
import cluster
import termgetter
import data.terms
import data.sentiments
    
def train(term_to_term=False, distributed=True):
    emotions = frozenset(get_emotion_dicts().keys())
    logging.info('Found <{0}> emotions'.format(len(emotions)))
    
    base_dicts = get_base_dicts(term_to_term)
    logging.info('Found <{0}> bases'.format(len(base_dicts)))
    
    terms = get_terms(ignore=base_dicts.keys())
    logging.info('Found <{0}> terms'.format(len(terms)))
    if not terms or len(terms) < len(base_dicts)/3: return
    
    train_terms = get_train_terms(base_dicts, emotions)
    if distributed:
        return distrubutedly_train_terms(train_terms, terms)
    return train_terms(terms)
    
def distrubutedly_train_terms(train_terms, terms, chunk_size=1000, use_cloud=False):
    logging.info(u'Starting distributed training <{0}>'.format(['locally','remotely'][int(use_cloud)]))
    if use_cloud:
        import cloud
        job_idds = cloud.map(train_terms, terms)
        term_iters = cloud.result(job_ids)
    else:
        import collections
        chunks = collections.defaultdict(list)
        chunk_count = len(terms) / chunk_size + 1
        for term in terms: chunks[hash(term) % chunk_count].append(term)
        term_iters = map(train_terms, chunks.values())
    return itertools.chain.from_iterable(term_iters)
    
def get_train_terms(base_dicts, emotions):
    def term_array_to_dict(term, term_array):
        return term, dict((emotion, term_array[j]) for j,emotion in enumerate(emotions) if term_array[j])

    def train_terms(terms):
        term_emotion_matrix = cluster.create_term_emotion_matrix(terms, base_dicts, emotions)
        term_dicts = (term_dict for term_dict in itertools.imap(term_array_to_dict, terms, term_emotion_matrix) if term_dict[1])
        term_ids = list(data.terms.save_terms(term_dicts))
        logging.info(u'Saved <{0}> emotional terms from <{1}> raws'.format(len(term_ids), len(terms)))
        return term_ids
    return train_terms
    
def save_bases():
    base_dicts = get_base_dicts().items()
    return list(data.terms.save_terms(base_dicts))
    
@caching.cached()
def get_emotion_dicts():
    return dict(data.sentiments.get(synonyms=True))
    
def get_base_dicts(use_terms=False):
    if use_terms:
        return dict(data.terms.get_terms(newer_than=7))
    emotion_dicts = get_emotion_dicts()
    return dict((synonym, {emotion: 1.0}) for emotion, synonyms in emotion_dicts.items() for synonym in synonyms)
    
def get_terms(ignore=None):
    terms = termgetter.get_terms()
    return set(terms).difference(ignore or [])
    
def setup_training_env():
    import data.couch
    data.couch.get_db_env = lambda : config.loader.load('config/test-config.yaml').get('COUCH_ENV',{})
    # logging.basicConfig(level=logging.DEBUG)
    
def train_engine(term_to_term=False):
    data.mongo.get_db_env = lambda : config.loader.load('config/test-config.yaml').get('DB_ENV',{}) # NOTE: testing only
    setup_training_env()
    save_bases()
    separation_degree = 0
    keep_going = train()
    while term_to_term and keep_going and separation_degree < 3:
        keep_going = train(term_to_term=True)
        separation_degree += 1
    data.terms.remove_terms(7)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    train_engine(1)
