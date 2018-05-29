#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import argparse
import background.endpoint

def setup_test_env():
    logging.basicConfig(level=logging.INFO)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kicks off cron job')
    parser.add_argument('interval', metavar='I', help='Interval of process')
    parser.add_argument('-p', '--prod', action='store_true', default=False, help='Run production environment')
    args = parser.parse_args()
    if not args.prod:
        setup_test_env()
    background.endpoint.run(args.interval)
