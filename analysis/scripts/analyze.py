#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import itertools
import sentiment.analysis

def analyze_text(text):
    yield text.strip()
    sentiment_result = sentiment.analysis.analyze(text)
    yield sentiment_result.get('classification')
    
def analyze_file(filename):
    importpath = os.path.join(u'local_imports', filename)
    if not os.path.isfile(importpath): return
    exportpath = os.path.join(u'local_exports', u'local.{filename}.csv'.format(filename=filename))
    with open(exportpath,'w') as exportfile:
        with open(importpath,'r') as importfile:
            def create_row(line):
                text = line.decode('utf8')
                row = u','.join(analyze_text(text)) + u'\n'
                return row.encode('utf8')
            lines = itertools.imap(create_row, iter(importfile))
            exportfile.writelines(lines)

def analyze_imports():
    map(analyze_file, os.listdir(u'local_imports'))
