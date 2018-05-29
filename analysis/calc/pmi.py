#!/usr/bin/python
# -*- coding: utf-8 -*-

import operator
import math

def calculate(list1, list2):
    if not list1 or not list2: return 0
    count1 = len(list1)
    count2 = len(list2)
    co = set(list1) & set(list2)
    co_count = float(len(co))
    return calculate_score(co_count, count1, count2)
    
def calculate_score(x_and_y, x, y):
    '''
    log( p(x,y) / p(x) / p(y) )
        ~= log( (x and y / total) / (x / total) / (y / total))
        ~= log( x and y / x / y * total )
    '''
    if x_and_y < 1: return 0
    return math.log1p(float(x_and_y) / x / y * (x+y))
    
import unittest

class PmiTests(unittest.TestCase):
    def test_calculate(self):
        dict1 = [u'one', u'two', u'three', u'four']
        dict2 = [u'one', u'two', u'three', u'five']
        result = calculate(dict1, dict2)
        self.assertTrue(0.405 < result < 0.406)
