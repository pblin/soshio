#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import argparse
import config.loader

def setup_test():
    config.loader.default = 'test-config.yaml'
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(u'Default config <{0}>'.format(config.loader.default))
   
def is_test(prod=True):
    return (not prod) or os.environ.get('TEST')
    
def run_local():
    parser = argparse.ArgumentParser(description='Start web server process')
    parser.add_argument('-p', '--prod', action='store_true', default=False, help='Run production environment')
    args = parser.parse_args()
    test_mode = is_test(args.prod)
    app = get_app(test_mode=test_mode)
    app.run(port=5001, debug=test_mode)

if is_test():
    setup_test()

import web.endpoint

if __name__ == '__main__':
    run_local()
else:
    app = web.endpoint.app
    celery = web.endpoint.celery

