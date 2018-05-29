#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
import os

import sqs
import requests.exceptions

def get_queue():
    if os.environ.get('TEST'):
        return sqs.get_queue('test-posts')
    return sqs.get_queue('posts')

def pop(max=10, timeout=300):
    try:
        messages = sqs.read(get_queue(), max) or []
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as error:
        logging.warning('Error <{error}> raised while getting posts. Skipping...'.format(error=error.message))
        return {}
    return dict(load_post(message) for message in messages)

def load_post(message):
    return message, json.loads(message.get_body())
    
def delete(ids):
    queue = get_queue()
    def try_delete(id, retry=True):
        try:
            sqs.delete(queue,id)
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as error:
            if not retry:
                logging.error('Error <{error}> raised while deleting post <{id}>. Skipping...'.format(error=error.message, id=id))
                return
            logging.warning('Error <{error}> raised while deleting post <{id}>. Retrying...'.format(error=error.message, id=id))
            try_delete(id, retry=False)
    map(try_delete, ids)
    
