#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import analyst
import data.posts
import data.analyses

def work():
    posts = data.posts.pop()
    logging.info('Received <{count}> posts'.format(count=len(posts)))
    if not posts: return
    analyses = dict((post['id'], analyst.analyze(post)) for id, post in posts.iteritems())
    data.analyses.save(analyses.itervalues())
    data.posts.delete(posts.iterkeys())
    logging.info('Processed <{count}> posts, failed <{failed}>'.format(count=len(analyses), failed=len(posts)-len(analyses)))
    return True
