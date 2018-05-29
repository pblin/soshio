#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import iron_mq
import config.loader

def get_queue(queue_name, *args, **kwargs):
    variables = get_mq_variables(*args, **kwargs)
    mq = iron_mq.IronMQ(**variables)
    logging.info('Connecting to IronMQ Project <{0}>'.format(variables.get('project_id')))
    return mq.queue(queue_name) if queue_name else mq.queues()
    
def get_mq_env():
    return config.loader.load().get('MQ_ENV',{})
    
def get_mq_variables(host=None, token=None, project_id=None):
    env = get_mq_env()
    return {
            'host': host or env.get('HOST'),
            'token': token or env.get('TOKEN'),
            'project_id': project_id or env.get('PROJECT'),
        }
