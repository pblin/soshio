#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import hashlib
import time, calendar

import config.loader

import timeframer
import data.analyses
from web.endpoint import celery
from report.run_async import run_async

def get_key(query, start, end):
    return (",".join(("export", query, start, end))).encode('utf-8')

def create(query, start, end, trial_mode=False):
    if trial_mode: return
    key = get_key(query, start, end)
    logging.info(u"Got export requst for %s from %s to %s" % (query, start, end))
    result = run_async(generate_export, key, "export", query, start, end)
    if result[0] == "ready":
        logging.debug("export url: " + result[1])
        return {'state': 'ready', 'download_url': result[1]}
    else:
        return {'state': 'running'}
    
labels = [
        'datetime',
        'query',
        'platform',
        'user',
        'sentiment',
        'location',
        'influence',
        'contexts',
        'emotions',
        'text'
    ]
def yield_rows(reports):
    yield u','.join(labels)
    for _,report in reports:
        if not report: continue
        yield u'\n'
        yield create_row(report).encode('utf-8')
    
def create_row(report):
    return u','.join(unicode(cell) if cell else '' for cell in yield_cells(report))
    
def yield_cells(report):
    for label in labels:
        yield report.get(label) if label not in yield_cell else yield_cell[label](report)

yield_cell = {
        'user': lambda report: hash(u'{0}.{1}'.format(report.get('user'), report.get('platform'))),
        'contexts': lambda report: u';'.join(report.get('contexts')),
        'emotions': lambda report: u';'.join(report.get('emotions')),
        'location': lambda report: report.get('location').replace(u",", u"，") if report.get('location') else "",
        'text': lambda report: report.get('text').replace(u",", u"，").replace('\r', " ").replace('\n', " ")
    }

def get_filename(query, start, end):
    m = hashlib.md5()
    m.update("%s,%s" % (get_key(query, start, end), calendar.timegm(time.localtime())))
    return m.hexdigest()

@celery.task()
def generate_export(query, start, end):
    '''
    Export obfuscated analysis data, no raw data to avoid privacy issues
    '''
    logging.warning(u"Got export requst for %s from %s to %s" % (query, start, end))
    timeframe = timeframer.get_timeframe_from_str(start, end)
    reports = data.analyses.get_export_docs(query, timeframe)
    filename = get_filename(query, start, end) + ".csv"
    with open("downloads/"+filename, "w") as f:
        for row in yield_rows(reports):
            f.write(row)
    return "https://" + config.loader.load().get('EXPORT', "export.getsoshio.com") + "/" + filename
