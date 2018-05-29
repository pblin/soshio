#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
from . import ironmq
import requests.exceptions
import datetimes


def get_queue():
    return ironmq.get_queue('posts')


def push(posts):
    queue = get_queue()
    messages = (create_messages(post) for post in posts if post)

    def try_push(message, retry=True):
        try:
            queue.post(message)
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as error:
            if not retry:
                logging.error(
                    'Error <{error}> raised while pushing post <{id}>. Skipping...'.format(
                        error=error.message,
                        id=id))
                return
            logging.warning(
                'Error <{error}> raised while pushing post <{id}>. Retrying...'.format(
                    error=error.message,
                    id=id))
            try_push(id, retry=False)
    map(try_push, messages)


def create_messages(post):
    post_json = json.dumps(post, default=datetimes.dthandler)
    return {
        'body': post_json,
        'timeout': 120,
        'expires_in': 24 * 3600
    }
