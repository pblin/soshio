#!/usr/bin/python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import sys, os
    sys.path.append(os.getcwd())

import csv
import logging
import unittest
import os.path
import collections
import analysis
import pprint
import random
import caching
import config.loader

def get_expected_classificaiton(expected):
    if expected in ('positive','1'):
        return 'positive'
    elif expected in ('negative','-1'):
        return 'negative'
    return 'neutral'
    
def get_testcases():
    testcases = list(load_status_testcases())
    #testcases = random.sample(testcases, min(len(testcases),500))
    file_path = os.path.join('testcases','local.statuses.txt')
#    with open(file_path,'w') as status_file:
#        for i,(expected,text) in enumerate(testcases):
#            status_file.write(u'{0}:::{1},{2}\n'.format(i+1,text,expected).encode('utf-8'))
    return testcases

def load_status_testcases():
    file_path = os.path.join('testcases','posts.txt')
    with open(file_path) as status_file:
        for i, row in enumerate(csv.reader(status_file)):
            yield row[0].decode('utf-8'), row[1].strip()
                
def get_results(testcases):
    for i, testcase in enumerate(testcases):
        text, expected = testcase
        result = analysis.analyze(text)
        yield i+1, expected, result['classification'], result['polarity'], result['emotions'], text
    
class ValidationTests(unittest.TestCase):
    def assert_acceptable_result(self, results):
        groupby_expected = collections.defaultdict(list)
        groupby_actual = collections.defaultdict(list)
        groupby_actual_counts = collections.defaultdict(collections.Counter)
        groupby_polarity_counts = collections.Counter()
        groupby_neu_counts = collections.defaultdict(collections.Counter)
        groupby_neu_fails = collections.defaultdict(list)
        groupby_counts_subj = collections.defaultdict(collections.Counter)
        groupby_expected_subj = collections.defaultdict(list)
        groupby_actual_subj = collections.defaultdict(list)
        groupby_neu_fails_subj = collections.defaultdict(list)
        success_counts = collections.defaultdict(float)
        case_counts = collections.defaultdict(float)
        fails = []
        nones = collections.defaultdict(int)
        epicfail = collections.defaultdict(int)
        subjfail = 0
        
        def get_subjectivity(emotions):
            return sum(emotions.itervalues())
        
        for i, expectation, classification, polarity, emotions, text in results:
            expected = get_expected_classificaiton(expectation)
            subj = get_subjectivity(emotions)
            case_counts[expected] += 1
            groupby_actual[classification].append(polarity)
            groupby_expected[expected].append(polarity)
            groupby_actual_subj[classification].append(subj)
            groupby_expected_subj[expected].append(subj)
            
            groupby_actual_counts[classification].update({expected:1})
            
            subj_decimal = int(subj * (10 ** 1))
            str_subj_decimal  = str(subj_decimal) if subj_decimal < 5 else '>5'
            groupby_counts_subj[expected].update({str_subj_decimal:1})
            
            str_decimal = str(int(polarity * (10 ** 1)))
            groupby_polarity_counts.update({str_decimal:1})
            if classification == 'neutral':
                groupby_neu_counts[expected].update({str_decimal:1})
            
            if expected != classification:
                if polarity == 0 and emotions: subjfail += 1
                if not emotions: nones[expected] += 1
                if expected != 'neutral' and classification != 'neutral': epicfail[expected] += 1
                if classification == 'neutral':
                    groupby_neu_fails[expected].append(polarity)
                    groupby_neu_fails_subj[expected].append(subj)
                fails.append((i, expected, classification, polarity, text))
            else: success_counts[classification] += 1
                
        cases = dict(case_counts)
        successes = dict(success_counts)
        actuals = dict((actual, len(cases)) for actual, cases in groupby_actual.iteritems())
        
        success_count = sum(cases for cases in success_counts.itervalues())
        failed_count = len(results) - success_count
        accuracy = float(success_count) / len(results)
        precision = dict((cls, count / len(groupby_actual[cls])) for cls, count in success_counts.iteritems())
        recall = dict((cls, count / case_counts[cls]) for cls, count in success_counts.iteritems())
        beta = 0.5
        fvalue = dict((cls, (1+beta**2) * pre * recall[cls] / (beta ** 2 * pre + recall[cls])) for cls, pre in precision.iteritems())
        
        def average(numbers):
            return sum(numbers) / len(numbers)
            
        def get_range(numbers):
            return min(numbers), average(numbers), max(numbers)

        print ''
        # thresholds = config.loader.load()
        # print '---------- variables ----------'
        # print 'polarity deviation', thresholds.get('POLARITY_DEVIATION')
        # print 'polarity mean', thresholds.get('POLARITY_MEAN')
        # print 'classification deviation', thresholds.get('CLASSIFICATION_DEVIATION')
        # print 'classification mean', thresholds.get('CLASSIFICATION_MEAN')
        print '---------- summary ----------'
        print 'failed, total:', failed_count, len(results)
        print 'cases:',  cases
        print 'success:', successes
        print 'actual:', actuals
        print 'classification x expected counts:'
        pprint.pprint(dict((actual, dict(counter)) for actual, counter in groupby_actual_counts.iteritems()))
        print '---------- analysis ----------'
        print 'accuracy:', accuracy
        print 'precision:', precision
        print 'recall:', recall
        print 'f-value:', fvalue
        print 'avg polarity:', sum(sum(pols) for pols in groupby_expected.itervalues()) / len(results)
        # print 'polarity counts:', dict(groupby_polarity_counts)
        
        # print '---------- polarity ----------'
        # print 'polarity expected:'
        # pprint.pprint(dict((expected, average(pols)) for expected, pols in groupby_expected.iteritems()))
        # print 'polarity actual:'
        # pprint.pprint(dict((actual, get_range(pols)) for actual, pols in groupby_actual.iteritems()))
        # print 'polarity neutrual counts:'
        # pprint.pprint(dict((expected, dict(counter)) for expected, counter in groupby_neu_counts.iteritems()))
        # print 'polarity neutrual failures:'
        # pprint.pprint(dict((expected, get_range(pols)) for expected, pols in groupby_neu_fails.iteritems()))
        
        # print '---------- subjectivity ----------'
        # print 'subjectivity expected:'
        # pprint.pprint(dict((expected, get_range(subjs)) for expected, subjs in groupby_expected_subj.iteritems()))
        # print 'subjectivity actual:'
        # pprint.pprint(dict((actual, get_range(subjs)) for actual, subjs in groupby_actual_subj.iteritems()))
        # print 'subjectivity counts:'
        # pprint.pprint(dict((expected, dict(counter)) for expected, counter in groupby_counts_subj.iteritems()))
        # print 'subjectivity neutrual failures:'
        # pprint.pprint(dict((expected, get_range(subjs)) for expected, subjs in groupby_neu_fails_subj.iteritems()))
        
        print '---------- counts ----------'
        print 'nones:', dict(nones), sum(nones.values())
        print 'epicfail:', dict(epicfail), sum(epicfail.values())
        # print 'subjfail:', subjfail
        print 'failures:'
        print 'row, expected, actual'
        for failure in fails:
            print failure[:4]
            print failure[4]
        
        self.assertGreaterEqual(accuracy, 0.6)
        self.assertGreaterEqual(fvalue.get('positive',0), 0.7)
        self.assertGreaterEqual(fvalue.get('negative',0), 0.7)
        
    def test_statuses(self):
        testcases = get_testcases()
        results = list(get_results(testcases))
        self.assert_acceptable_result(results)
        
    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ValidationTests))
    return suite
    
def set_print_to_file(prefix='new-'):
    import sys
    import codecs
    import time
    
    original = sys.stdout
    class FileStdOut(object):
        def __init__(self, *files):
            self.files = files
        
        def write(self, obj):
            for file in self.files:
                file.write(obj)
    
    filename = 'local.results.{0}{1}.txt'.format(prefix, int(time.time()))
    print filename
    path = os.path.join('testcases',filename)
    file = codecs.open(path,'w+','utf8')
    sys.stdout = FileStdOut(sys.stdout, file)
    
def run():
    caching.clear_cache()
    unittest.TextTestRunner(verbosity=2).run(suite())
    
def setup_env(test=True):
    if test:
        data.mongo.get_db_env = lambda : config.loader.load('config/test-config.yaml').get('DB_ENV',{})
    set_print_to_file(prefix='test-' if test else 'prod-')
    
if __name__ == '__main__':
    import data.mongo
    #logging.basicConfig(level=logging.INFO)
    setup_env(os.environ.get('TEST', 0))
    run()
