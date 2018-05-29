# -*- coding: utf-8 -*-
import logging
import urllib

import boto.sqs
from boto.sqs.message import Message
import config.loader

def get_aws_env(escape=True):
    aws_env = config.loader.load().get('AWS_ENV')
    if escape:
        return {"key": aws_env["KEY"], "secret": urllib.quote(aws_env["SECRET"],safe="")}
    return {"key": aws_env["KEY"], "secret": aws_env["SECRET"]}

def get_queue(queue_name, *args, **kwargs):
    env = get_aws_env(escape=False)
    logging.debug('Connecting to SQS queue <{0}>...'.format(queue_name))
    conn = boto.sqs.connect_to_region(
              "us-east-1",
              aws_access_key_id=env['key'],
              aws_secret_access_key=env['secret'])
    return conn.create_queue(queue_name)

def post(queue, message): # TODO: Wrap this into a class
    m = Message()
    m.set_body(message)
    queue.write(m)
