#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import argparse
import config.loader
import background.endpoint
import time

def run(cycle=True, interval=3):
    while True:
        if background.endpoint.work(): continue
        if not cycle: break
        time.sleep(interval*60)
    
def test_run():
    config.loader.default = 'test-config.yaml'
    reload(logging)
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(u'Default config <{0}>'.format(config.loader.default))
    run(cycle=False)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start web server process')
    parser.add_argument('-p', '--prod', action='store_true', default=False, help='Run production environment')
    args = parser.parse_args()
    if not args.prod: test_run()
    else: run()
