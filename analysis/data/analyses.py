#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import couch

def save(iter_analyses):
    analyses = [analysis for analysis in iter_analyses if analysis]
    if not analyses: return
    with couch.RestDatabase() as database:
        response = database.post_docs(analyses)
        if 'error' in response and not response.get('reason'):
            logging.warning(u'Bulk insert failed, switching to individual insert')
            map(database.post_doc, analyses)