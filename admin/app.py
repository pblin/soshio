#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import argparse
import config.loader
import web.endpoint

def run(*args, **kwargs):
    port = int(os.environ.get('PORT',5007))
    web.endpoint.run(port=port, *args, **kwargs)
    
def run_test():
    config.loader.default = 'test-config.yaml'
    reload(logging)
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(u'Default config <{0}>'.format(config.loader.default))
    run(debug=True)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start web server process')
    parser.add_argument('-p', '--prod', action='store_true', default=False, help='Run production environment')
    args = parser.parse_args()
    if not args.prod or os.environ.get('TEST'):
        run_test()
    else: run()
