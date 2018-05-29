#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import argparse
import config.loader
import background.endpoint

def setup_test_env():
    config.loader.default = 'test-config.yaml'
    reload(logging)
    logging.basicConfig(level=logging.DEBUG)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kicks off cron job')
    parser.add_argument('-p', '--prod', action='store_true', default=False, help='Run production environment')
    args = parser.parse_args()
    if not args.prod:
        setup_test_env()
    background.endpoint.run()
