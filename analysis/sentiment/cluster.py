#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import itertools
import numpy
import scorer

def create_term_emotion_matrix(terms, base_dicts, emotions):
    logging.info('Clustering <{0}> terms with <{1}> bases and <{2}> emotions'.format(len(terms), len(base_dicts), len(emotions)))
    bases = frozenset(base_dicts.keys())
    
    base_emotion_matrix = create_base_matrix(base_dicts.values(), emotions)
    
    term_base_matrix = create_term_matrix(terms, bases, scorer.score_term)
    return numpy.dot(term_base_matrix, base_emotion_matrix)
    
def get_base_emotion(base_dict,emotion):
    return base_dict.get(emotion) or 0.0
    
def create_base_matrix(base_dicts, emotions):
    values = [base_dict.get(emotion) or 0.0 for base_dict in base_dicts for emotion in emotions]
    return numpy.array(values).reshape((len(base_dicts), len(emotions)))
    
def create_term_matrix(terms, bases, score_term):
    values = list(itertools.chain.from_iterable(score_term(term, bases) for term in terms))
    return numpy.array(values).reshape((len(terms), len(bases)))
    
def normalize_columns(matrix):
    column_sums = matrix.sum(axis=0)
    return matrix / column_sums[numpy.newaxis,:]
